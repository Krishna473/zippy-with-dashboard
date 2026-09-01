export default function DataTable({
  columns,
  pageItems,
  onEdit,
  onDelete,
  currentPage,
  totalPages,
  onPrevPage,
  onNextPage,
}) {
  return (
    <div className="zzc-content">
      <div className="zzc-table-card">
        <table className="zzc-table">
          <thead>
            <tr>
              {columns.map((col) => (
                <th key={col}>{col}</th>
              ))}
              <th className="actions">Actions</th>
            </tr>
          </thead>
          <tbody>
            {pageItems.length === 0 ? (
              <tr className="zzc-empty-row">
                <td colSpan={columns.length + 1}>No records found</td>
              </tr>
            ) : (
              pageItems.map(({ row, index }) => (
                <tr key={index}>
                  {row.map((cell, i) => (
                    <td key={i}>{cell}</td>
                  ))}
                  <td className="actions">
                    <button className="zzc-btn-sm" onClick={() => onEdit(index)}>
                      Edit
                    </button>
                    <button className="zzc-btn-sm zzc-btn-danger" onClick={() => onDelete(index)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="zzc-pagination-row">
        <span className="zzc-muted zzc-small">
          Page {currentPage} of {totalPages}
        </span>
        <div className="zzc-pagination-btns">
          <button className="zzc-btn zzc-btn-outline" disabled={currentPage <= 1} onClick={onPrevPage}>
            Previous
          </button>
          <button className="zzc-btn zzc-btn-outline" disabled={currentPage >= totalPages} onClick={onNextPage}>
            Next
          </button>
        </div>
      </div>
    </div>
  );
}

