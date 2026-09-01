import { useState } from "react";
import { fetchList, createRecord, updateRecord, TABLE_CONFIG, coerceFieldValue } from "../api.js";
import "./BulkTools.css";

// The backend supports partial updates (it uses `exclude_unset=True`), so
// every bulk action here sends only the field(s) actually being changed —
// not a full record replace. Verified directly against pets.py's
// update_product / update_inventory / update_doctor handlers.

const WORKING_SETS = [
  { key: "products", label: "Medicines & Products" },
  { key: "inventory", label: "Inventory" },
  { key: "doctors", label: "Doctors" },
];

function nowTime() {
  return new Date().toLocaleTimeString([], { hour12: false });
}

function toCSV(rows) {
  if (rows.length === 0) return "";
  const headers = Object.keys(rows[0]);
  const escape = (v) => `"${String(v ?? "").replace(/"/g, '""')}"`;
  return [headers.map(escape).join(",")].concat(rows.map((r) => headers.map((h) => escape(r[h])).join(","))).join("\n");
}

function downloadText(filename, text, mime = "text/csv;charset=utf-8;") {
  const blob = new Blob([text], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function parseCSV(text) {
  const lines = text.trim().split(/\r?\n/).filter((l) => l.trim().length > 0);
  if (lines.length < 2) return [];
  const headers = lines[0].split(",").map((h) => h.trim());
  return lines.slice(1).map((line) => {
    const values = line.split(",").map((v) => v.trim());
    const obj = {};
    headers.forEach((h, i) => {
      obj[h] = values[i] ?? "";
    });
    return obj;
  });
}

function parseImportText(text) {
  const trimmed = text.trim();
  if (!trimmed) return [];
  if (trimmed.startsWith("[") || trimmed.startsWith("{")) {
    const parsed = JSON.parse(trimmed);
    return Array.isArray(parsed) ? parsed : [parsed];
  }
  return parseCSV(trimmed);
}

function isValidNumber(v) {
  return v !== "" && v !== null && v !== undefined && !Number.isNaN(Number(v));
}

function workingSetHasIsActive(key) {
  return TABLE_CONFIG[key]?.fields.some((f) => f.key === "is_active") ?? false;
}

export default function BulkTools() {
  const [workingSet, setWorkingSet] = useState("products");
  const [filterPincode, setFilterPincode] = useState("");
  const [filterSellerId, setFilterSellerId] = useState("");
  const [filterCategoryId, setFilterCategoryId] = useState("");

  const [stockOp, setStockOp] = useState("add");
  const [stockValue, setStockValue] = useState("10");

  const [priceOp, setPriceOp] = useState("rupee");
  const [priceValue, setPriceValue] = useState("10");
  const [recalcDiscount, setRecalcDiscount] = useState(true);

  const [assignPincodeValue, setAssignPincodeValue] = useState("");
  const [importText, setImportText] = useState("");

  const [busy, setBusy] = useState(false);
  const [activityLog, setActivityLog] = useState([]);

  function addLog(message) {
    setActivityLog((prev) => [{ time: nowTime(), message }, ...prev].slice(0, 50));
  }

  const stockValueValid = isValidNumber(stockValue);
  const priceValueValid = isValidNumber(priceValue);
  const stockApplicable = workingSet === "products" || workingSet === "inventory";
  const priceApplicable = workingSet === "products";
  const showActivateDeactivate = workingSetHasIsActive(workingSet);

  // Products don't carry a seller_id or category_id in this schema — a
  // seller-id filter on products is derived through Inventory (which does
  // link product_id + seller_id). Category id has no matching field on
  // Product at all yet, so that filter is currently a no-op; it's kept in
  // the UI for when/if the backend adds that relationship.
  async function getFilteredProducts() {
    let rows = await fetchList("products");
    if (filterPincode.trim()) {
      rows = rows.filter((p) => String(p.pincode || "") === filterPincode.trim());
    }
    if (filterSellerId.trim()) {
      const inv = await fetchList("inventory");
      const ids = new Set(inv.filter((i) => String(i.seller_id) === filterSellerId.trim()).map((i) => i.product_id));
      rows = rows.filter((p) => ids.has(p.id));
    }
    return rows;
  }

  // Generalized filtered fetch for whichever table is passed in — used by
  // Assign pin code, Activate/Deactivate, Export CSV, and CSV/JSON import,
  // all of which operate on the currently selected working set (not just
  // products). Products and Inventory both support the seller-id filter;
  // Doctors has no seller relationship, so that filter is a no-op for it.
  async function getFilteredTable(tableKey) {
    let rows = await fetchList(tableKey);
    if (filterPincode.trim()) {
      rows = rows.filter((r) => String(r.pincode || "") === filterPincode.trim());
    }
    if (filterSellerId.trim()) {
      if (tableKey === "inventory") {
        rows = rows.filter((r) => String(r.seller_id) === filterSellerId.trim());
      } else if (tableKey === "products") {
        const inv = await fetchList("inventory");
        const ids = new Set(inv.filter((i) => String(i.seller_id) === filterSellerId.trim()).map((i) => i.product_id));
        rows = rows.filter((r) => ids.has(r.id));
      }
    }
    return rows;
  }

  async function getFilteredWorkingSet() {
    return getFilteredTable(workingSet);
  }

  async function runBusy(fn) {
    setBusy(true);
    try {
      await fn();
    } catch (err) {
      addLog(`Error: ${err.message || "something went wrong"}`);
    } finally {
      setBusy(false);
    }
  }

  function applyStockChange() {
    if (!stockApplicable || !stockValueValid) return;
    runBusy(async () => {
      const delta = Number(stockValue);
      let changed = 0;

      if (workingSet === "inventory") {
        const rows = await getFilteredTable("inventory");
        for (const row of rows) {
          const current = Number(row.available_quantity) || 0;
          let next;
          if (stockOp === "add") next = current + delta;
          else if (stockOp === "subtract") next = Math.max(0, current - delta);
          else next = delta;
          if (next !== current) {
            await updateRecord("inventory", row.id, { available_quantity: next });
            changed++;
          }
        }
        addLog(`Stock update (inventory): {"matched":${rows.length},"changed":${changed}}`);
      } else {
        const rows = await getFilteredProducts();
        for (const p of rows) {
          const current = Number(p.stock_quantity) || 0;
          let next;
          if (stockOp === "add") next = current + delta;
          else if (stockOp === "subtract") next = Math.max(0, current - delta);
          else next = delta;
          if (next !== current) {
            await updateRecord("products", p.id, { stock_quantity: next });
            changed++;
          }
        }
        addLog(`Stock update (products): {"matched":${rows.length},"changed":${changed}}`);
      }
    });
  }

  function applyPriceChange() {
    if (!priceApplicable || !priceValueValid) return;
    runBusy(async () => {
      const rows = await getFilteredProducts();
      const value = Number(priceValue);
      let changed = 0;
      for (const p of rows) {
        const current = Number(p.price) || 0;
        let next;
        if (priceOp === "rupee") next = current + value;
        else if (priceOp === "percent") next = current + current * (value / 100);
        else next = value;
        next = Math.max(0, Math.round(next * 100) / 100);

        const payload = { price: next };
        if (recalcDiscount) {
          const mrp = Number(p.mrp) || 0;
          payload.discount_percent = mrp > 0 ? Math.round((1 - next / mrp) * 1000) / 10 : p.discount_percent ?? 0;
        }
        if (next !== current) {
          await updateRecord("products", p.id, payload);
          changed++;
        }
      }
      addLog(`Price update: {"matched":${rows.length},"changed":${changed}}`);
    });
  }

  function applyAssignPincode() {
    if (!assignPincodeValue.trim()) return;
    runBusy(async () => {
      const rows = await getFilteredWorkingSet();
      for (const row of rows) {
        await updateRecord(workingSet, row.id, { pincode: assignPincodeValue.trim() });
      }
      addLog(`Assigned pin code ${assignPincodeValue.trim()} to ${rows.length} ${workingSet} rows`);
    });
  }

  function setActiveForFiltered(activate) {
    if (!showActivateDeactivate) return;
    runBusy(async () => {
      const rows = await getFilteredWorkingSet();
      for (const row of rows) {
        await updateRecord(workingSet, row.id, { is_active: activate ? "Yes" : "No" });
      }
      addLog(`${activate ? "Activated" : "Deactivated"} ${rows.length} ${workingSet} rows`);
    });
  }

  function exportCSV() {
    runBusy(async () => {
      const rows = await getFilteredWorkingSet();
      const label = WORKING_SETS.find((w) => w.key === workingSet)?.label || workingSet;
      downloadText(`${workingSet}.csv`, toCSV(rows));
      addLog(`Exported ${rows.length} ${label.toLowerCase()} rows`);
    });
  }

  function handleFileChoose(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => setImportText(String(reader.result || ""));
    reader.readAsText(file);
  }

  function runImport() {
    runBusy(async () => {
      const config = TABLE_CONFIG[workingSet];
      let rows;
      try {
        rows = parseImportText(importText);
      } catch (err) {
        addLog(`Import failed to parse: ${err.message}`);
        return;
      }

      let created = 0,
        updated = 0,
        failed = 0;

      for (const row of rows) {
        try {
          const payload = {};
          config.fields.forEach((field) => {
            if (field.readOnly) return;
            if (row[field.key] === undefined) return;
            payload[field.key] = coerceFieldValue(field, row[field.key]);
          });
          if (row.id !== undefined && row.id !== "") {
            await updateRecord(workingSet, row.id, payload);
            updated++;
          } else {
            await createRecord(workingSet, payload);
            created++;
          }
        } catch {
          failed++;
        }
      }
      addLog(`Import into ${workingSet}: {"created":${created},"updated":${updated},"failed":${failed}}`);
    });
  }

  return (
    <div className="zzc-content">
      <div className="bulk-tools-page">
        <div className="bulk-working-set">
          <span className="bulk-working-label">Working set:</span>
          {WORKING_SETS.map((ws) => (
            <button
              key={ws.key}
              className={"bulk-tab" + (workingSet === ws.key ? " active" : "")}
              onClick={() => setWorkingSet(ws.key)}
            >
              {ws.label}
            </button>
          ))}
          <button className="bulk-tab" onClick={exportCSV} disabled={busy}>
            Export CSV
          </button>
        </div>

        <div className="bulk-card">
          <h3>Target filter</h3>
          <p>Leave blank to apply to every row in {workingSet}. Filters combine (AND).</p>
          <div className="bulk-filter-grid">
            <input placeholder="Pin code" value={filterPincode} onChange={(e) => setFilterPincode(e.target.value)} />
            <input placeholder="Seller id (optional)" value={filterSellerId} onChange={(e) => setFilterSellerId(e.target.value)} />
            <input
              placeholder="Category id (products only)"
              value={filterCategoryId}
              onChange={(e) => setFilterCategoryId(e.target.value)}
            />
          </div>
        </div>

        <div className="bulk-operation-grid">
          <div className="bulk-card">
            <h3>Mass stock update</h3>
            <p>
              {workingSet === "inventory"
                ? "Updates inventory.available_quantity."
                : workingSet === "products"
                ? "Updates products.stock_quantity."
                : "Doctors don't have a stock field — switch to Medicines & Products or Inventory to use this."}
            </p>
            <div className="bulk-input-row">
              <select value={stockOp} onChange={(e) => setStockOp(e.target.value)}>
                <option value="add">Add units</option>
                <option value="subtract">Subtract units</option>
                <option value="set">Set to</option>
              </select>
              <input type="number" value={stockValue} onChange={(e) => setStockValue(e.target.value)} />
            </div>
            <button className="bulk-primary-btn" onClick={applyStockChange} disabled={busy || !stockApplicable || !stockValueValid}>
              Apply stock change
            </button>
          </div>

          <div className="bulk-card">
            <h3>Mass price update</h3>
            <p>
              Applies to medicines, pet food and accessories.
              {!priceApplicable && " (switch to Medicines & Products to use this)"}
            </p>
            <div className="bulk-input-row">
              <select value={priceOp} onChange={(e) => setPriceOp(e.target.value)}>
                <option value="rupee">Change by ₹</option>
                <option value="percent">Change by %</option>
                <option value="set">Set to ₹</option>
              </select>
              <input type="number" value={priceValue} onChange={(e) => setPriceValue(e.target.value)} />
            </div>
            <label className="bulk-checkbox">
              <input type="checkbox" checked={recalcDiscount} onChange={(e) => setRecalcDiscount(e.target.checked)} />
              Recalculate discount % against MRP
            </label>
            <button className="bulk-primary-btn" onClick={applyPriceChange} disabled={busy || !priceApplicable || !priceValueValid}>
              Apply price change
            </button>
          </div>
        </div>

        <div className="bulk-operation-grid">
          <div className="bulk-card">
            <h3>Assign pin code in bulk</h3>
            <p>Tag the filtered {workingSet} rows to a serviceable pin code.</p>
            <input
              className="bulk-full-input"
              placeholder="e.g. 560076"
              value={assignPincodeValue}
              onChange={(e) => setAssignPincodeValue(e.target.value)}
            />
            <div className="bulk-button-row" style={{ marginTop: 12 }}>
              <button className="bulk-primary-btn" onClick={applyAssignPincode} disabled={busy || !assignPincodeValue.trim()}>
                Assign pin code
              </button>
              {showActivateDeactivate && (
                <>
                  <button className="bulk-secondary-btn" onClick={() => setActiveForFiltered(true)} disabled={busy}>
                    Activate
                  </button>
                  <button className="bulk-secondary-btn" onClick={() => setActiveForFiltered(false)} disabled={busy}>
                    Deactivate
                  </button>
                </>
              )}
            </div>
          </div>

          <div className="bulk-card">
            <h3>CSV / JSON import</h3>
            <p>
              First row = column names. Include an id column to update existing rows, omit it to create new ones.
              <br />
              Example: name,price,mrp,pincode,stock_quantity
            </p>
            <textarea
              value={importText}
              onChange={(e) => setImportText(e.target.value)}
              placeholder={"name,price,mrp,pincode,stock_quantity\nCalcium Syrup 200ml,320,399,560076,50"}
            />
            <div className="bulk-file-row">
              <input type="file" accept=".csv,.json,text/csv,application/json" onChange={handleFileChoose} />
              <button className="bulk-primary-btn" onClick={runImport} disabled={busy || !importText.trim()}>
                Import into {workingSet}
              </button>
            </div>
          </div>
        </div>

        <div className="bulk-card">
          <h3>Activity log</h3>
          <div className="bulk-activity">
            {activityLog.length === 0 ? (
              <p>No actions yet.</p>
            ) : (
              activityLog.map((entry, i) => (
                <div key={i}>
                  {entry.time} · {entry.message}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
