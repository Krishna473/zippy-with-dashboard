import { useState, useMemo, useEffect, useCallback } from "react";
import { findLabel } from "./data.js";
import { SEARCH_CONFIG } from "./searchConfig.js";
import {
  TABLE_CONFIG,
  fetchList,
  createRecord,
  updateRecord,
  deleteRecord,
  coerceFieldValue,
  displayFieldValue,
} from "./api.js";
import Sidebar from "./components/sidebar.jsx";
import TopBar from "./components/TopBar.jsx";
import StatsGrid from "./components/StatsGrid.jsx";
import DataTable from "./components/DataTable.jsx";
import RecordModal from "./components/RecordModal.jsx";
import Dashboard from "./components/Dashboard.jsx";
import BulkTools from "./components/BulkTools.jsx";
import SalesCRM from "./components/SalesCRM.jsx";

const PAGE_SIZE = 10;

export default function App() {
  const [currentKey, setCurrentKey] = useState("pet_parents");
  const [records, setRecords] = useState([]); // raw objects from the API, in list order
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState("");
  const [activeTab, setActiveTab] = useState("dashboard"); // "dashboard" | "data"
  const [modalMode, setModalMode] = useState(null); // null | "new" | "edit"
  const [editingRecord, setEditingRecord] = useState(null);
  const [formValues, setFormValues] = useState({});
  const [saving, setSaving] = useState(false);
  const [showSalesCRM, setShowSalesCRM] = useState(false);
  const [salesRole, setSalesRole] = useState("executive");

  const salesRoleByKey = {
    sales_regional_manager: "regionalManager",
    sales_manager: "manager",
    sales_executive_crm: "executive",
  };
  const tableConfig = TABLE_CONFIG[currentKey];
  const columns = tableConfig?.fields ?? [];
  const searchConfig = SEARCH_CONFIG[currentKey];

  const loadRecords = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchList(currentKey);
      setRecords(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message || "Failed to load data from the API");
      setRecords([]);
    } finally {
      setLoading(false);
    }
  }, [currentKey]);

  useEffect(() => {
    loadRecords();
  }, [loadRecords]);

  const filtered = useMemo(() => {
    const term = searchTerm.trim().toLowerCase();
    if (!term || !searchConfig) return records;
    return records.filter((record) =>
      String(record[searchConfig.column] ?? "").toLowerCase().includes(term)
    );
  }, [records, searchTerm, searchConfig]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));

  useEffect(() => {
    setCurrentPage((page) => Math.min(page, totalPages));
  }, [totalPages]);

  const safePage = Math.min(currentPage, totalPages);
  const start = (safePage - 1) * PAGE_SIZE;
  const pageItems = filtered.slice(start, start + PAGE_SIZE);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
   
  function selectTable(key) {
    setCurrentPage(1);
    setSearchTerm("");
    setError(null);

    if (salesRoleByKey[key]) {
      setSalesRole(salesRoleByKey[key]);
      setShowSalesCRM(true);
      return;
    }

    setCurrentKey(key);
    setActiveTab("data");
  }

  function openNewModal() {
    const initial = {};
    columns.forEach((field) => {
      initial[field.key] = field.type === "bool" ? false : field.default ?? "";
    });
    setFormValues(initial);
    setEditingRecord(null);
    setModalMode("new");
  }

  function openEditModal(record) {
    const initial = {};
    columns.forEach((field) => {
      initial[field.key] = displayFieldValue(field, record);
    });
    setFormValues(initial);
    setEditingRecord(record);
    setModalMode("edit");
  }

  function closeModal() {
    setModalMode(null);
    setEditingRecord(null);
    setFormValues({});
  }

  function handleFieldChange(key, value) {
    setFormValues((prev) => ({ ...prev, [key]: value }));
  }

  async function saveModal(e) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const payload = {};
      columns.forEach((field) => {
        if (field.readOnly) return;
        payload[field.key] = coerceFieldValue(field, formValues[field.key]);
      });
      if (editingRecord) {
        await updateRecord(currentKey, editingRecord.id, payload);
      } else {
        await createRecord(currentKey, payload);
      }
      closeModal();
      await loadRecords();
      setRefreshTrigger((n) => n + 1);
    } catch (err) {
      setError(err.message || "Failed to save record");
    } finally {
      setSaving(false);
    }
  }



  async function handleDelete(record) {
    if (!window.confirm("Delete this record?")) return;
    setError(null);
    try {
      await deleteRecord(currentKey, record.id);
      await loadRecords();
      setRefreshTrigger((n) => n + 1);
    } catch (err) {
      setError(err.message || "Failed to delete record");
    }
  }

  const columnLabels = columns.map((f) => f.label || f.key);

  if(showSalesCRM) {
    return (
      <SalesCRM
        role={salesRole}
        onRoleChange={setSalesRole}
        onExit={() => setShowSalesCRM(false)}
      />
    );
  }

  return (
    <div className="zzc-app">
      <Sidebar currentKey={currentKey} onSelect={selectTable}/>

      <main className="zzc-main">
        <TopBar
          title={findLabel(currentKey)}
          subtitle={`${filtered.length} records · table ${currentKey}`}
          showSearch={activeTab === "data" && Boolean(searchConfig)}
          showNewRecord={activeTab === "data"}
          searchPlaceholder={searchConfig ? "Search " + searchConfig.placeholder : ""}
          searchTerm={searchTerm}
          onSearchChange={(value) => {
            setSearchTerm(value);
            setCurrentPage(1);
          }}
          onNewRecord={openNewModal}
          activeTab={activeTab}
          onTabChange={setActiveTab}
          onOpenSalesCRM={() => { setSalesRole("executive"); setShowSalesCRM(true); }}
        />

        {error && (
          <div className="zzc-content" style={{ paddingTop: 0 }}>
            <div
              style={{
                background: "#fee2e2",
                color: "#991b1b",
                padding: "10px 14px",
                borderRadius: 8,
                marginBottom: 12,
                fontSize: 14,
              }}
            >
              {error}
            </div>
          </div>
        )}

        {activeTab === "dashboard" && <Dashboard />}
        
        {activeTab === "bulk" && <BulkTools />}

        {activeTab === "data" && (
          <>
            <StatsGrid refreshTrigger={refreshTrigger} />

            {loading ? (
              <div className="zzc-content">
                <p className="zzc-muted">Loading {findLabel(currentKey)}…</p>
              </div>
            ) : (
              <DataTable
                columns={columnLabels}
                pageItems={pageItems.map((record, index) => ({
                  row: columns.map((field) => formatCell(field, record)),
                  index,
                  record,
                }))}
                onEdit={(index) => openEditModal(pageItems[index])}
                onDelete={(index) => handleDelete(pageItems[index])}
                currentPage={safePage}
                totalPages={totalPages}
                onPrevPage={() => setCurrentPage((p) => Math.max(1, p - 1))}
                onNextPage={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              />
            )}
          </>
        )}
      </main>

      <RecordModal
        mode={modalMode}
        columns={columns.map((f) => ({ key: f.key, label: f.label || f.key, type: f.type, readOnly: f.readOnly, required: f.required }))}
        values={formValues}
        onChange={handleFieldChange}
        onSave={saveModal}
        onCancel={closeModal}
        saving={saving}
      />
    </div>
  );
}

function formatCell(field, record) {
  const value = record[field.key];
  if (value === null || value === undefined) return "";
  if (typeof value === "boolean") return value ? "true" : "false";
  return String(value);
}
