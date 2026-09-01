export default function TopBar({
  title,
  subtitle,
  searchPlaceholder,
  showSearch,
  showNewRecord,
  searchTerm,
  onSearchChange,
  onNewRecord,
  activeTab,
  onTabChange,
  onOpenSalesCRM
}) {
  return (
    <header className="zzc-topbar">
      <div>
        <h1>{title}</h1>
        <p className="zzc-muted zzc-small">{subtitle}</p>
      </div>
      <div className="zzc-topbar-actions">
        {showSearch && (
        <input
          className="zzc-search-input"
          placeholder={searchPlaceholder}
          value={searchTerm}
          onChange={(e) => onSearchChange(e.target.value)}
        />
        )}
        {showNewRecord && (
          <button className="zzc-btn zzc-btn-primary" onClick={onNewRecord}>
          New record
        </button>
        )}
        
        {["dashboard", "data", "bulk"].map((tab) => (
          <button
            key={tab}
            className={"zzc-btn zzc-btn-outline" + (activeTab === tab ? " active" : "")}
            onClick={() => onTabChange(tab)}
          >
            {tab === "bulk" ? "Bulk tools" : tab}
          </button>
        ))}
        <button
  type="button"
  className="zzc-btn-link"
  onClick={onOpenSalesCRM}
>
  Sales CRM
</button>
        <a href="#" className="zzc-btn-link">Console</a>
      </div>
    </header>
  );
}
