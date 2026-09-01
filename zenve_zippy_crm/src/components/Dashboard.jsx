import { useEffect, useState } from "react";
import { fetchList } from "../api.js";
import "./Dashboard.css";
// ---------------------------------------------------------------------------
// Small aggregation helpers — everything on this page is computed client-side
// from the same list endpoints the Data view already uses (fetchList), since
// the backend has no dedicated analytics/dashboard endpoint. No mock data.
// ---------------------------------------------------------------------------

function sum(rows, key) {
  return rows.reduce((total, row) => total + (Number(row[key]) || 0), 0);
}

function groupCount(rows, key) {
  const counts = {};
  rows.forEach((row) => {
    const k = row[key] || "unknown";
    counts[k] = (counts[k] || 0) + 1;
  });
  return Object.entries(counts)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);
}

function groupSum(rows, groupKey, sumKey) {
  const totals = {};
  rows.forEach((row) => {
    const k = row[groupKey] || "unknown";
    totals[k] = (totals[k] || 0) + (Number(row[sumKey]) || 0);
  });
  return Object.entries(totals)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);
}

function monthOf(dateStr) {
  if (!dateStr) return null;
  return String(dateStr).slice(0, 7); // "YYYY-MM"
}

function formatDate(dateStr) {
  if (!dateStr) return "—";
  return String(dateStr).slice(0, 10);
}

function formatINR(n) {
  return "₹" + Math.round(n || 0).toLocaleString("en-IN");
}

// Builds the 3-level drill-down: regions (pin codes) → stores → products & orders.
// The real schema has no direct seller/pincode link on Order/OrderItem — only
// `product_name` (text) and Inventory's product_id+seller_id+pincode. So an
// order is attributed to a store when at least one of its items' product_name
// matches a product carried by that store (via Inventory). This is the closest
// honest mapping the actual schema supports.
function buildDrillDown({ doctors, inventory, products, sellers, orders, orderItems }) {
  const priceById = {};
  const productById = {};
  products.forEach((p) => {
    priceById[p.id] = Number(p.price) || 0;
    productById[p.id] = p;
  });
  const sellerById = {};
  sellers.forEach((s) => {
    sellerById[s.id] = s;
  });

  const pincodes = new Set(
    [...doctors.map((r) => r.pincode), ...products.map((r) => r.pincode), ...inventory.map((r) => r.pincode)].filter(Boolean)
  );

  const invByStoreKey = {}; // `${pincode}|${sellerId}` -> inventory rows
  inventory.forEach((inv) => {
    if (!inv.pincode || !inv.seller_id) return;
    const key = `${inv.pincode}|${inv.seller_id}`;
    (invByStoreKey[key] ||= []).push(inv);
  });

  const itemsByOrderId = {};
  orderItems.forEach((oi) => {
    (itemsByOrderId[oi.order_id] ||= []).push(oi);
  });

  const storesByPincode = {};
  const productsByStoreKey = {};
  const ordersByStoreKey = {};

  Object.entries(invByStoreKey).forEach(([key, invRows]) => {
    const [pincode, sellerIdStr] = key.split("|");
    const seller = sellerById[Number(sellerIdStr)];
    if (!seller) return;

    const productNames = new Set(invRows.map((r) => productById[r.product_id]?.name).filter(Boolean));

    const soldByName = {};
    const revenueByName = {};
    orderItems.forEach((oi) => {
      if (productNames.has(oi.product_name)) {
        soldByName[oi.product_name] = (soldByName[oi.product_name] || 0) + (Number(oi.quantity) || 0);
        revenueByName[oi.product_name] = (revenueByName[oi.product_name] || 0) + (Number(oi.total_price) || 0);
      }
    });

    productsByStoreKey[key] = invRows.map((inv) => {
      const p = productById[inv.product_id] || {};
      return {
        name: p.name || `Product #${inv.product_id}`,
        price: Number(p.price) || 0,
        stock: Number(p.stock_quantity) || 0,
        avail: Number(inv.available_quantity) || 0,
        sold: soldByName[p.name] || 0,
        revenue: revenueByName[p.name] || 0,
        rx: p.is_prescription_required === true || p.is_prescription_required === "Yes" ? "Yes" : "No",
      };
    });

    const ordersTable = [];
    let storeRevenue = 0;
    orders.forEach((o) => {
      const matchedItems = (itemsByOrderId[o.id] || []).filter((oi) => productNames.has(oi.product_name));
      if (matchedItems.length === 0) return;
      const amount = matchedItems.reduce((s, it) => s + (Number(it.total_price) || 0), 0);
      storeRevenue += amount;
      ordersTable.push({
        orderNumber: o.order_number,
        date: formatDate(o.placed_at),
        items: matchedItems.length,
        amount,
        status: o.status,
        paymentStatus: o.payment_status,
      });
    });
    ordersTable.sort((a, b) => b.date.localeCompare(a.date));
    ordersByStoreKey[key] = ordersTable;

    const skus = new Set(invRows.map((r) => r.product_id)).size;
    const units = sum(invRows, "available_quantity");
    const stockValue = invRows.reduce((s, r) => s + (Number(r.available_quantity) || 0) * (priceById[r.product_id] || 0), 0);

    (storesByPincode[pincode] ||= []).push({
      key,
      sellerId: seller.id,
      name: seller.business_name,
      type: seller.seller_type || "—",
      verification: seller.verification_status || "—",
      rating: seller.rating ?? "—",
      skus,
      units,
      stockValue,
      orders: ordersTable.length,
      revenue: storeRevenue,
    });
  });

  const pincodeRows = [...pincodes].map((pc) => {
    const docCount = doctors.filter((doc) => doc.pincode === pc).length;
    const stores = storesByPincode[pc] || [];
    const skus = new Set(stores.flatMap((s) => (invByStoreKey[s.key] || []).map((r) => r.product_id))).size;
    const units = stores.reduce((s, st) => s + st.units, 0);
    const stockValue = stores.reduce((s, st) => s + st.stockValue, 0);
    const ordersCount = stores.reduce((s, st) => s + st.orders, 0);
    const revenue = stores.reduce((s, st) => s + st.revenue, 0);
    const invRowsHere = inventory.filter((i) => i.pincode === pc);
    const lowStock = invRowsHere.filter((i) => (Number(i.available_quantity) || 0) <= (Number(i.reorder_level) || 0)).length;
    return { pincode: pc, doctors: docCount, stores: stores.length, skus, units, stockValue, orders: ordersCount, revenue, lowStock };
  });

  return { pincodeRows, storesByPincode, productsByStoreKey, ordersByStoreKey };
}

function downloadCSV(filename, headers, rows) {
  const escape = (v) => `"${String(v ?? "").replace(/"/g, '""')}"`;
  const csv = [headers.map(escape).join(",")].concat(rows.map((r) => r.map(escape).join(","))).join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

const PALETTE = ["#0f9d8f", "#f97350", "#8b6bd1", "#3fb6a8", "#f0a63e", "#4f8ef0"];

// ---------------------------------------------------------------------------
// Lightweight chart primitives (no charting library — CSS/SVG only)
// ---------------------------------------------------------------------------

function VerticalBars({ data, color = PALETTE[0] }) {
  const max = Math.max(1, ...data.map((d) => d.value));
  return (
    <div className="dash-vbars">
      {data.map((d) => (
        <div className="dash-vbar-col" key={d.name}>
          <div className="dash-vbar-track">
            <div className="dash-vbar-fill" style={{ height: `${(d.value / max) * 100}%`, background: color }} />
          </div>
          <span className="dash-vbar-value">{d.value}</span>
          <span className="dash-vbar-label" title={d.name}>{d.name}</span>
        </div>
      ))}
    </div>
  );
}

function HorizontalBars({ data, color = PALETTE[1], formatValue = (v) => v }) {
  const max = Math.max(1, ...data.map((d) => d.value));
  return (
    <div className="dash-hbars">
      {data.map((d) => (
        <div className="dash-hbar-row" key={d.name}>
          <span className="dash-hbar-label" title={d.name}>{d.name}</span>
          <div className="dash-hbar-track">
            <div className="dash-hbar-fill" style={{ width: `${(d.value / max) * 100}%`, background: color }} />
          </div>
          <span className="dash-hbar-value">{formatValue(d.value)}</span>
        </div>
      ))}
    </div>
  );
}

function GroupedBars({ data, series, colors = PALETTE }) {
  const max = Math.max(1, ...data.flatMap((d) => series.map((s) => Number(d[s]) || 0)));
  return (
    <div className="dash-grouped">
      {data.map((d) => (
        <div className="dash-grouped-col" key={d.name}>
          <div className="dash-grouped-bars">
            {series.map((s, i) => (
              <div className="dash-grouped-track" key={s}>
                <div
                  className="dash-grouped-fill"
                  style={{ height: `${((Number(d[s]) || 0) / max) * 100}%`, background: colors[i % colors.length] }}
                />
              </div>
            ))}
          </div>
          <span className="dash-vbar-label" title={d.name}>{d.name}</span>
        </div>
      ))}
      <div className="dash-legend">
        {series.map((s, i) => (
          <span className="dash-legend-item" key={s}>
            <span className="dash-legend-dot" style={{ background: colors[i % colors.length] }} />
            {s}
          </span>
        ))}
      </div>
    </div>
  );
}

function PieChart({ data, colors = PALETTE }) {
  const total = Math.max(1, sum(data, "value"));
  const stops = data
    .reduce((segments, d, i) => {
      const prevEnd = i === 0 ? 0 : segments[i - 1].end;
      segments.push({ color: colors[i % colors.length], start: prevEnd, end: prevEnd + (d.value / total) * 360 });
      return segments;
    }, [])
    .map((s) => `${s.color} ${s.start}deg ${s.end}deg`);
  return (
    <div className="dash-pie-wrap">
      <div className="dash-pie" style={{ background: `conic-gradient(${stops.join(", ")})` }} />
      <ul className="dash-legend-list">
        {data.map((d, i) => (
          <li key={d.name}>
            <span className="dash-legend-dot" style={{ background: colors[i % colors.length] }} />
            {d.name} <span className="zzc-muted">({d.value})</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function StackedMonthBars({ data }) {
  const max = Math.max(1, ...data.map((d) => d.commerce + d.consults + d.services));
  return (
    <div className="dash-stacked">
      {data.map((d) => (
        <div className="dash-stacked-row" key={d.month}>
          <span className="dash-hbar-label">{d.month}</span>
          <div className="dash-stacked-track">
            <div className="dash-stacked-seg" style={{ width: `${(d.commerce / max) * 100}%`, background: PALETTE[0] }} title={`commerce: ${formatINR(d.commerce)}`} />
            <div className="dash-stacked-seg" style={{ width: `${(d.consults / max) * 100}%`, background: PALETTE[1] }} title={`consults: ${formatINR(d.consults)}`} />
            <div className="dash-stacked-seg" style={{ width: `${(d.services / max) * 100}%`, background: PALETTE[3] }} title={`services: ${formatINR(d.services)}`} />
          </div>
          <span className="dash-hbar-value">{formatINR(d.commerce + d.consults + d.services)}</span>
        </div>
      ))}
      <div className="dash-legend">
        <span className="dash-legend-item"><span className="dash-legend-dot" style={{ background: PALETTE[0] }} />commerce</span>
        <span className="dash-legend-item"><span className="dash-legend-dot" style={{ background: PALETTE[1] }} />consults</span>
        <span className="dash-legend-item"><span className="dash-legend-dot" style={{ background: PALETTE[3] }} />services</span>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------

function Panel({ title, subtitle, wide, onExport, children }) {
  return (
    <div className={"dash-panel" + (wide ? " dash-panel-wide" : "")}>
      <div className="dash-panel-header">
        <div>
          <h2 className="dash-panel-title">{title}</h2>
          {subtitle && <p className="zzc-muted zzc-small">{subtitle}</p>}
        </div>
        {onExport && (
          <button className="zzc-btn zzc-btn-outline dash-export-btn" onClick={onExport}>
            Export CSV
          </button>
        )}
      </div>
      {children}
    </div>
  );
}

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [d, setD] = useState(null);
  const [drillPincode, setDrillPincode] = useState(null);
  const [drillStoreKey, setDrillStoreKey] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    Promise.all([
      fetchList("pet_parents"),
      fetchList("pets"),
      fetchList("doctors"),
      fetchList("appointments"),
      fetchList("products"),
      fetchList("inventory"),
      fetchList("orders"),
      fetchList("sellers"),
      fetchList("services"),
      fetchList("payouts"),
      fetchList("service_bookings"),
      fetchList("consultations"),
      fetchList("order_items"),
      fetchList("executive_tasks"),
      fetchList("sales_executives"),
    ])
      .then(
        ([
          petParents,
          pets,
          doctors,
          appointments,
          products,
          inventory,
          orders,
          sellers,
          services,
          payouts,
          serviceBookings,
          consultations,
          orderItems,
          executiveTasks,
          salesExecutives,
        ]) => {
          if (cancelled) return;

          // Product id -> price, for stock valuation
          const priceById = {};
          products.forEach((p) => {
            priceById[p.id] = Number(p.price) || 0;
          });

          const totalGMV = sum(orders, "total_amount");
          const platformCommission = sum(payouts, "commission_amount");
          const consultRevenue = sum(appointments, "consultation_fee");
          const stockValue = inventory.reduce((s, row) => s + (Number(row.available_quantity) || 0) * (priceById[row.product_id] || 0), 0);

          const pincodes = new Set(
            [...doctors.map((r) => r.pincode), ...products.map((r) => r.pincode), ...inventory.map((r) => r.pincode)].filter(Boolean)
          );

          const kpis = [
            { label: "TOTAL GMV", value: formatINR(totalGMV), sub: "Commerce + consults + services", highlight: true },
            { label: "PLATFORM COMMISSION", value: formatINR(platformCommission), sub: "Take-rate revenue" },
            { label: "STOCK VALUE", value: formatINR(stockValue), sub: `${inventory.length} SKUs below reorder` },
            { label: "ORDERS", value: orders.length, sub: `${orders.filter((o) => o.payment_status === "paid").length} paid payments` },
            { label: "APPOINTMENTS", value: appointments.length, sub: `${serviceBookings.length} service bookings` },
            { label: "PIN CODES LIVE", value: pincodes.size, sub: "Doctors + inventory coverage" },
            { label: "DOCTORS", value: doctors.length, sub: `${doctors.filter((x) => x.is_active === "Yes" || x.is_active === true).length} verified` },
            { label: "SELLERS", value: sellers.length, sub: "SKUs active" },
            { label: "PET PARENTS", value: petParents.length, sub: `${pets.length} pets on record` },
            { label: "SERVICES", value: services.length, sub: "Grooming, walking, boarding" },
            { label: "SALES EXECUTIVES", value: salesExecutives.length, sub: `${executiveTasks.length} open field tasks` },
            { label: "CONSULT REVENUE", value: formatINR(consultRevenue), sub: `Commerce ${formatINR(totalGMV)}` },
          ];

          // Drill-down explorer: regions → stores → products & orders
          const drill = buildDrillDown({ doctors, inventory, products, sellers, orders, orderItems });

          // Revenue mix by month
          const commerceByMonth = groupSum(orders.map((o) => ({ ...o, month: monthOf(o.placed_at) })), "month", "total_amount");
          const consultsByMonth = groupSum(appointments.map((a) => ({ ...a, month: monthOf(a.appointment_date) })), "month", "consultation_fee");
          const servicesByMonth = groupSum(serviceBookings.map((s) => ({ ...s, month: monthOf(s.booking_date) })), "month", "price");
          const months = [...new Set([...commerceByMonth, ...consultsByMonth, ...servicesByMonth].map((r) => r.name))]
            .filter((m) => m && m !== "unknown")
            .sort();
          const revenueMix = months.map((m) => ({
            month: m,
            commerce: commerceByMonth.find((r) => r.name === m)?.value || 0,
            consults: consultsByMonth.find((r) => r.name === m)?.value || 0,
            services: servicesByMonth.find((r) => r.name === m)?.value || 0,
          }));

          // Field sales: open vs done tasks (executive_tasks has no executive reference field, so this is a system-wide total, not per-executive)
          const doneStatuses = ["completed", "done", "closed"];
          const openCount = executiveTasks.filter((t) => !doneStatuses.includes(String(t.status).toLowerCase())).length;
          const doneCount = executiveTasks.filter((t) => doneStatuses.includes(String(t.status).toLowerCase())).length;

          setD({
            kpis,
            drill,
            revenueMix,
            pincodeDepth: [...pincodes].map((pc) => ({
              name: pc,
              doctors: doctors.filter((doc) => doc.pincode === pc).length,
              skus: new Set(inventory.filter((i) => i.pincode === pc).map((i) => i.product_id)).size,
              units: sum(inventory.filter((i) => i.pincode === pc), "available_quantity"),
            })),
            topProducts: groupSum(orderItems, "product_name", "total_price").slice(0, 6),
            orderPipeline: groupCount(orders, "status"),
            consultationsByMode: groupCount(consultations, "consultation_mode"),
            fieldSales: { open: openCount, done: doneCount },
            petMix: groupCount(pets, "species"),
            supplySide: groupCount(sellers, "seller_type"),
          });
          setLoading(false);
        }
      )
      .catch((err) => {
        if (!cancelled) {
          setError(err.message || "Failed to load dashboard data");
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  if (error) {
    return (
      <div className="zzc-content">
        <div className="dash-error">Couldn't load the dashboard from the backend ({error})</div>
      </div>
    );
  }

  if (loading || !d) {
    return (
      <div className="zzc-content">
        <p className="zzc-muted">Building the investor dashboard…</p>
      </div>
    );
  }

  return (
    <div className="zzc-content">
      <div className="dash-hero">
        <h2 className="dash-hero-title">Zenve Zippy — business intelligence</h2>
        <p className="zzc-muted">
          Live view of the marketplace: veterinary network, pet commerce, services, pin-code coverage and the field sales engine. Every number is read directly from the production cloud.
        </p>
        <div className="dash-hero-actions">
          <button
            className="zzc-btn zzc-btn-outline dash-export-btn"
            onClick={() => downloadCSV("kpis.csv", ["label", "value", "detail"], d.kpis.map((k) => [k.label, k.value, k.sub]))}
          >
            Export all KPIs
          </button>
          <button
            className="zzc-btn zzc-btn-outline dash-export-btn"
            onClick={() =>
              downloadCSV(
                "revenue-mix.csv",
                ["month", "commerce", "consults", "services"],
                d.revenueMix.map((r) => [r.month, r.commerce, r.consults, r.services])
              )
            }
          >
            Export revenue
          </button>
          <button
            className="zzc-btn zzc-btn-outline dash-export-btn"
            onClick={() =>
              downloadCSV(
                "regions.csv",
                ["Pin code", "Doctors", "Stores", "SKUs", "Units", "Stock value", "Orders", "Revenue", "Low stock"],
                d.drill.pincodeRows.map((r) => [r.pincode, r.doctors, r.stores, r.skus, r.units, formatINR(r.stockValue), r.orders, formatINR(r.revenue), r.lowStock])
              )
            }
          >
            Export regions
          </button>
        </div>
      </div>

      <div className="dash-kpi-grid">
        {d.kpis.map((k) => (
          <div className={"dash-kpi-card" + (k.highlight ? " highlight" : "")} key={k.label}>
            <p className="dash-kpi-label">{k.label}</p>
            <p className="dash-kpi-value">{k.value}</p>
            <p className="dash-kpi-sub">{k.sub}</p>
          </div>
        ))}
      </div>

      <div className="dash-panel">
        <div className="dash-panel-header">
          <div>
            <h2 className="dash-panel-title">Drill-down explorer</h2>
            <p className="zzc-muted zzc-small">Region (pin code) → store → products &amp; orders. Click any row to go deeper.</p>
          </div>
          <div className="dash-breadcrumb">
            <button
              className={"dash-crumb" + (!drillPincode ? " active" : "")}
              onClick={() => {
                setDrillPincode(null);
                setDrillStoreKey(null);
              }}
            >
              All regions
            </button>
            {drillPincode && (
              <>
                <span className="dash-crumb-sep">/</span>
                <button className={"dash-crumb" + (drillPincode && !drillStoreKey ? " active" : "")} onClick={() => setDrillStoreKey(null)}>
                  Pin {drillPincode}
                </button>
              </>
            )}
            {drillStoreKey && (
              <>
                <span className="dash-crumb-sep">/</span>
                <button className="dash-crumb active">
                  {d.drill.storesByPincode[drillPincode]?.find((s) => s.key === drillStoreKey)?.name}
                </button>
              </>
            )}
          </div>
        </div>

        {/* Level 1: all regions */}
        {!drillPincode && (
          <>
            <div className="dash-panel-subheader">
              <span className="zzc-muted zzc-small">{d.drill.pincodeRows.length} regions live</span>
              <button
                className="zzc-btn zzc-btn-outline dash-export-btn"
                onClick={() =>
                  downloadCSV(
                    "regions.csv",
                    ["Pin code", "Doctors", "Stores", "SKUs", "Units", "Stock value", "Orders", "Revenue", "Low stock"],
                    d.drill.pincodeRows.map((r) => [r.pincode, r.doctors, r.stores, r.skus, r.units, formatINR(r.stockValue), r.orders, formatINR(r.revenue), r.lowStock])
                  )
                }
              >
                Export CSV
              </button>
            </div>
            <div className="zzc-table-card">
              <table className="zzc-table">
                <thead>
                  <tr>
                    {["Pin code", "Doctors", "Stores", "SKUs", "Units", "Stock value", "Orders", "Revenue", "Low stock"].map((c) => (
                      <th key={c}>{c}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {d.drill.pincodeRows.length === 0 ? (
                    <tr className="zzc-empty-row">
                      <td colSpan={9}>No pin-coded records yet</td>
                    </tr>
                  ) : (
                    d.drill.pincodeRows.map((row) => (
                      <tr key={row.pincode} className="dash-drill-row" onClick={() => setDrillPincode(row.pincode)}>
                        <td><strong>{row.pincode}</strong></td>
                        <td>{row.doctors}</td>
                        <td>{row.stores}</td>
                        <td>{row.skus}</td>
                        <td>{row.units}</td>
                        <td>{formatINR(row.stockValue)}</td>
                        <td>{row.orders}</td>
                        <td>{formatINR(row.revenue)}</td>
                        <td>{row.lowStock}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </>
        )}

        {/* Level 2: stores serving the selected pin code */}
        {drillPincode && !drillStoreKey && (
          <>
            <div className="dash-panel-subheader">
              <span className="zzc-muted zzc-small">Stores serving pin {drillPincode}</span>
              <button
                className="zzc-btn zzc-btn-outline dash-export-btn"
                onClick={() => {
                  const stores = d.drill.storesByPincode[drillPincode] || [];
                  downloadCSV(
                    `stores-${drillPincode}.csv`,
                    ["Store", "Type", "Verification", "Rating", "SKUs", "Units", "Stock value", "Orders", "Revenue"],
                    stores.map((s) => [s.name, s.type, s.verification, s.rating, s.skus, s.units, formatINR(s.stockValue), s.orders, formatINR(s.revenue)])
                  );
                }}
              >
                Export CSV
              </button>
            </div>
            <div className="zzc-table-card">
              <table className="zzc-table">
                <thead>
                  <tr>
                    {["Store", "Type", "Verification", "Rating", "SKUs", "Units", "Stock value", "Orders", "Revenue"].map((c) => (
                      <th key={c}>{c}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {(d.drill.storesByPincode[drillPincode] || []).length === 0 ? (
                    <tr className="zzc-empty-row">
                      <td colSpan={9}>No stores carry inventory for this pin code</td>
                    </tr>
                  ) : (
                    (d.drill.storesByPincode[drillPincode] || []).map((s) => (
                      <tr key={s.key} className="dash-drill-row" onClick={() => setDrillStoreKey(s.key)}>
                        <td><strong>{s.name}</strong></td>
                        <td>{s.type}</td>
                        <td>{s.verification}</td>
                        <td>{s.rating}</td>
                        <td>{s.skus}</td>
                        <td>{s.units}</td>
                        <td>{formatINR(s.stockValue)}</td>
                        <td>{s.orders}</td>
                        <td>{formatINR(s.revenue)}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </>
        )}

        {/* Level 3: products and orders for the selected store */}
        {drillPincode && drillStoreKey && (
          <div className="dash-store-detail-grid">
            <div>
              <div className="dash-panel-subheader">
                <span className="zzc-muted zzc-small">Products of this store in {drillPincode}</span>
                <button
                  className="zzc-btn zzc-btn-outline dash-export-btn"
                  onClick={() => {
                    const rows = d.drill.productsByStoreKey[drillStoreKey] || [];
                    downloadCSV(
                      "products.csv",
                      ["Product", "Price", "Stock", "Avail.", "Sold", "Revenue", "Rx"],
                      rows.map((p) => [p.name, formatINR(p.price), p.stock, p.avail, p.sold, formatINR(p.revenue), p.rx])
                    );
                  }}
                >
                  Export CSV
                </button>
              </div>
              <div className="zzc-table-card">
                <table className="zzc-table">
                  <thead>
                    <tr>
                      {["Product", "Price", "Stock", "Avail.", "Sold", "Revenue", "Rx"].map((c) => (
                        <th key={c}>{c}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {(d.drill.productsByStoreKey[drillStoreKey] || []).length === 0 ? (
                      <tr className="zzc-empty-row">
                        <td colSpan={7}>No products in this store's inventory</td>
                      </tr>
                    ) : (
                      (d.drill.productsByStoreKey[drillStoreKey] || []).map((p, i) => (
                        <tr key={i}>
                          <td>{p.name}</td>
                          <td>{formatINR(p.price)}</td>
                          <td>{p.stock}</td>
                          <td>{p.avail}</td>
                          <td>{p.sold}</td>
                          <td>{formatINR(p.revenue)}</td>
                          <td>{p.rx}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            <div>
              <div className="dash-panel-subheader">
                <span className="zzc-muted zzc-small">Orders from this store</span>
                <button
                  className="zzc-btn zzc-btn-outline dash-export-btn"
                  onClick={() => {
                    const rows = d.drill.ordersByStoreKey[drillStoreKey] || [];
                    downloadCSV(
                      "orders.csv",
                      ["Order", "Date", "Items", "Amount", "Status", "Payment"],
                      rows.map((o) => [o.orderNumber, o.date, o.items, formatINR(o.amount), o.status, o.paymentStatus])
                    );
                  }}
                >
                  Export CSV
                </button>
              </div>
              <div className="zzc-table-card">
                <table className="zzc-table">
                  <thead>
                    <tr>
                      {["Order", "Date", "Items", "Amount", "Status", "Payment"].map((c) => (
                        <th key={c}>{c}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {(d.drill.ordersByStoreKey[drillStoreKey] || []).length === 0 ? (
                      <tr className="zzc-empty-row">
                        <td colSpan={6}>No orders matched to this store yet</td>
                      </tr>
                    ) : (
                      (d.drill.ordersByStoreKey[drillStoreKey] || []).map((o, i) => (
                        <tr key={i}>
                          <td>{o.orderNumber}</td>
                          <td>{o.date}</td>
                          <td>{o.items}</td>
                          <td>{formatINR(o.amount)}</td>
                          <td>{o.status}</td>
                          <td>{o.paymentStatus}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="dash-grid">
        <Panel
          title="Revenue mix by month"
          subtitle="Commerce vs consultations vs services"
          onExport={() =>
            downloadCSV(
              "revenue-mix.csv",
              ["month", "commerce", "consults", "services"],
              d.revenueMix.map((r) => [r.month, r.commerce, r.consults, r.services])
            )
          }
        >
          {d.revenueMix.length === 0 ? <p className="zzc-muted zzc-small">No dated records yet.</p> : <StackedMonthBars data={d.revenueMix} />}
        </Panel>

        <Panel
          title="Pin-code network depth"
          subtitle="Click a bar to drill into that region"
          onExport={() =>
            downloadCSV(
              "pincode-depth.csv",
              ["pincode", "doctors", "skus", "units"],
              d.pincodeDepth.map((r) => [r.name, r.doctors, r.skus, r.units])
            )
          }
        >
          {d.pincodeDepth.length === 0 ? (
            <p className="zzc-muted zzc-small">No pin-coded records yet.</p>
          ) : (
            <GroupedBars data={d.pincodeDepth} series={["doctors", "skus", "units"]} />
          )}
        </Panel>

        <Panel
          title="Top products by revenue"
          onExport={() => downloadCSV("top-products.csv", ["product", "revenue"], d.topProducts.map((p) => [p.name, p.value]))}
        >
          {d.topProducts.length === 0 ? (
            <p className="zzc-muted zzc-small">No order items yet.</p>
          ) : (
            <HorizontalBars data={d.topProducts} color={PALETTE[1]} formatValue={formatINR} />
          )}
        </Panel>

        <Panel
          title="Order pipeline"
          subtitle="Status distribution"
          onExport={() => downloadCSV("order-pipeline.csv", ["status", "count"], d.orderPipeline.map((p) => [p.name, p.value]))}
        >
          {d.orderPipeline.length === 0 ? <p className="zzc-muted zzc-small">No orders yet.</p> : <PieChart data={d.orderPipeline} />}
        </Panel>

        <Panel
          title="Consultations by mode"
          subtitle="Clinic, home, video, emergency"
          onExport={() => downloadCSV("consultations.csv", ["mode", "count"], d.consultationsByMode.map((p) => [p.name, p.value]))}
        >
          {d.consultationsByMode.length === 0 ? (
            <p className="zzc-muted zzc-small">No consultations yet.</p>
          ) : (
            <VerticalBars data={d.consultationsByMode} color={PALETTE[2]} />
          )}
        </Panel>

        <Panel
          title="Field sales performance"
          subtitle="Open vs completed tasks per executive"
          onExport={() => downloadCSV("field-sales.csv", ["status", "count"], [["open", d.fieldSales.open], ["done", d.fieldSales.done]])}
        >
          <VerticalBars data={[{ name: "open", value: d.fieldSales.open }, { name: "done", value: d.fieldSales.done }]} color={PALETTE[4]} />
        </Panel>

        <Panel
          title="Pet mix"
          subtitle="Species on the platform"
          onExport={() => downloadCSV("pet-mix.csv", ["species", "count"], d.petMix.map((p) => [p.name, p.value]))}
        >
          {d.petMix.length === 0 ? <p className="zzc-muted zzc-small">No pets yet.</p> : <PieChart data={d.petMix} />}
        </Panel>

        <Panel
          title="Supply side"
          subtitle="Sellers by type and inventory source"
          onExport={() => downloadCSV("supply-side.csv", ["seller_type", "count"], d.supplySide.map((p) => [p.name, p.value]))}
        >
          {d.supplySide.length === 0 ? <p className="zzc-muted zzc-small">No sellers yet.</p> : <VerticalBars data={d.supplySide} color={PALETTE[5]} />}
        </Panel>
      </div>
    </div>
  );
}