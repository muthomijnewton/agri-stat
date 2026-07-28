/**
 * Paginator — shared client-side pagination component.
 *
 * Props:
 *   total      {number}   total number of items
 *   page       {number}   current 1-based page number
 *   pageSize   {number}   rows per page
 *   onPage     {fn}       called with new page number
 *   onPageSize {fn}       called with new page-size value
 *   pageSizeOptions {number[]}  defaults to [10, 25, 50, 100]
 */
export default function Paginator({
  total,
  page,
  pageSize,
  onPage,
  onPageSize,
  pageSizeOptions = [10, 25, 50, 100],
}) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize))
  const from = total === 0 ? 0 : (page - 1) * pageSize + 1
  const to   = Math.min(page * pageSize, total)

  /* Build page-number window: always show first, last, current ±2 */
  const pages = buildPageWindow(page, totalPages)

  return (
    <div className="paginator">
      {/* Left: row-count selector */}
      <div className="paginator-size">
        <span>Rows per page:</span>
        <select
          value={pageSize}
          onChange={(e) => {
            onPageSize(Number(e.target.value))
            onPage(1) // reset to first page
          }}
          aria-label="Rows per page"
        >
          {pageSizeOptions.map((n) => (
            <option key={n} value={n}>{n}</option>
          ))}
        </select>
      </div>

      {/* Centre: range label */}
      <span className="paginator-info" aria-live="polite">
        {total === 0 ? 'No results' : `${from}–${to} of ${total}`}
      </span>

      {/* Right: page buttons */}
      <nav className="paginator-nav" aria-label="Pagination">
        {/* First / Prev */}
        <button
          className="paginator-btn"
          onClick={() => onPage(1)}
          disabled={page <= 1}
          aria-label="First page"
        >
          «
        </button>
        <button
          className="paginator-btn"
          onClick={() => onPage(page - 1)}
          disabled={page <= 1}
          aria-label="Previous page"
        >
          ‹
        </button>

        {/* Numbered buttons */}
        {pages.map((p, i) =>
          p === '…' ? (
            <span key={`ellipsis-${i}`} className="paginator-ellipsis">…</span>
          ) : (
            <button
              key={p}
              className={`paginator-btn${p === page ? ' paginator-btn--active' : ''}`}
              onClick={() => onPage(p)}
              aria-label={`Page ${p}`}
              aria-current={p === page ? 'page' : undefined}
            >
              {p}
            </button>
          )
        )}

        {/* Next / Last */}
        <button
          className="paginator-btn"
          onClick={() => onPage(page + 1)}
          disabled={page >= totalPages}
          aria-label="Next page"
        >
          ›
        </button>
        <button
          className="paginator-btn"
          onClick={() => onPage(totalPages)}
          disabled={page >= totalPages}
          aria-label="Last page"
        >
          »
        </button>
      </nav>
    </div>
  )
}

/* Build a compact window of page numbers with ellipsis gaps */
function buildPageWindow(current, total) {
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)

  const delta = 2
  const left  = current - delta
  const right = current + delta

  const pages = []

  for (let p = 1; p <= total; p++) {
    if (p === 1 || p === total || (p >= left && p <= right)) {
      pages.push(p)
    }
  }

  const windowed = []
  let prev = null
  for (const p of pages) {
    if (prev !== null && p - prev > 1) windowed.push('…')
    windowed.push(p)
    prev = p
  }
  return windowed
}
