import { useState, useRef, useCallback } from 'react'
import { importsAPI } from '../services/api'
import '../css/import.css'

// ---------------------------------------------------------------------------
// SVG icons
// ---------------------------------------------------------------------------
function IconUpload() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <polyline points="16 16 12 12 8 16" />
      <line x1="12" y1="12" x2="12" y2="21" />
      <path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3" />
    </svg>
  )
}

function IconFile() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
    </svg>
  )
}

function IconCheck() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  )
}

function IconX() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  )
}

function IconAlertTriangle() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
      <line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" />
    </svg>
  )
}

// ---------------------------------------------------------------------------
// CSV parser (client-side preview only — CSV and TSV)
// ---------------------------------------------------------------------------
function parseCSVPreview(text, maxRows = 5, separator = ',') {
  const lines = text.trim().split(/\r?\n/)
  if (lines.length < 2) return { headers: [], rows: [] }
  const headers = lines[0].split(separator).map(h => h.trim().replace(/^"|"$/g, ''))
  const rows = lines.slice(1, maxRows + 1).map(line => {
    const cells = line.split(separator).map(c => c.trim().replace(/^"|"$/g, ''))
    return headers.reduce((obj, h, i) => { obj[h] = cells[i] ?? ''; return obj }, {})
  })
  return { headers, rows }
}

function parseJSONPreview(text, maxRows = 5) {
  try {
    const data = JSON.parse(text)
    if (!Array.isArray(data) || data.length === 0) return { headers: [], rows: [] }
    const headers = Object.keys(data[0])
    const rows = data.slice(0, maxRows).map(row =>
      headers.reduce((obj, h) => { obj[h] = String(row[h] ?? ''); return obj }, {})
    )
    return { headers, rows }
  } catch {
    return { headers: [], rows: [] }
  }
}

// ---------------------------------------------------------------------------
// Accepted file extensions + MIME types
// ---------------------------------------------------------------------------
const ACCEPTED_EXTENSIONS = '.csv,.tsv,.xlsx,.xls,.ods,.json'
const ACCEPTED_MIME = [
  'text/csv',
  'text/plain',
  'text/tab-separated-values',
  'application/json',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'application/vnd.ms-excel',
  'application/vnd.oasis.opendocument.spreadsheet',
].join(',')

// ---------------------------------------------------------------------------
// Import type configs
// ---------------------------------------------------------------------------
const IMPORT_TYPES = {
  transactions: {
    label: 'Transactions',
    description: 'Sales and purchase records. Feeds directly into forecasts and analytics.',
    requiredCols: ['date', 'product', 'quantity'],
    optionalCols: ['unit_price', 'transaction_type', 'notes'],
    sampleCSV: `date,product,transaction_type,quantity,unit_price,notes
2025-01-15,Tomatoes,sale,120,45.00,Market day
2025-01-16,Maize,purchase,500,18.50,Supplier delivery
2025-01-17,Beans,sale,80,95.00,
2025-01-18,Potatoes,sale,200,22.00,Wholesale`,
  },
  products: {
    label: 'Products',
    description: 'Product catalogue. Import your crop/livestock list before importing transactions.',
    requiredCols: ['name'],
    optionalCols: ['category', 'unit', 'unit_price', 'description'],
    sampleCSV: `name,category,unit,unit_price,description
Tomatoes,Vegetables,kg,45.00,Fresh tomatoes
Maize,Cereals,kg,18.50,Dry maize grain
Beans,Legumes,kg,95.00,Mixed beans
Potatoes,Vegetables,kg,22.00,Irish potatoes`,
  },
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export default function Import() {
  const [importType, setImportType] = useState('transactions')
  const [file, setFile]             = useState(null)
  const [preview, setPreview]       = useState(null)   // { headers, rows }
  const [dragOver, setDragOver]     = useState(false)
  const [loading, setLoading]       = useState(false)
  const [result, setResult]         = useState(null)   // import result
  const [error, setError]           = useState(null)
  const fileInputRef = useRef(null)

  const config = IMPORT_TYPES[importType]

  // ── file selection ────────────────────────────────────────────────────────
  const handleFile = useCallback((selectedFile) => {
    if (!selectedFile) return

    const ext = selectedFile.name.split('.').pop().toLowerCase()
    const allowed = ['csv', 'tsv', 'xlsx', 'xls', 'ods', 'json']
    if (!allowed.includes(ext)) {
      setError(`Unsupported file type ".${ext}". Accepted: CSV, TSV, XLSX, XLS, ODS, JSON.`)
      return
    }

    setError(null)
    setResult(null)
    setFile(selectedFile)

    // Client-side preview is only possible for text formats
    if (ext === 'csv') {
      const reader = new FileReader()
      reader.onload = (e) => setPreview(parseCSVPreview(e.target.result, 5, ','))
      reader.readAsText(selectedFile)
    } else if (ext === 'tsv') {
      const reader = new FileReader()
      reader.onload = (e) => setPreview(parseCSVPreview(e.target.result, 5, '\t'))
      reader.readAsText(selectedFile)
    } else if (ext === 'json') {
      const reader = new FileReader()
      reader.onload = (e) => setPreview(parseJSONPreview(e.target.result))
      reader.readAsText(selectedFile)
    } else {
      // Excel / ODS — can't parse client-side without a library
      setPreview({ headers: [], rows: [], binaryFormat: true, ext: ext.toUpperCase() })
    }
  }, [])

  const handleInputChange = (e) => handleFile(e.target.files[0])

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    handleFile(e.dataTransfer.files[0])
  }

  const handleDragOver = (e) => { e.preventDefault(); setDragOver(true) }
  const handleDragLeave = ()    => setDragOver(false)

  const clearFile = () => {
    setFile(null)
    setPreview(null)
    setResult(null)
    setError(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  // ── tab switch ────────────────────────────────────────────────────────────
  const handleTypeChange = (type) => {
    setImportType(type)
    clearFile()
  }

  // ── download sample ───────────────────────────────────────────────────────
  const downloadSample = () => {
    const blob = new Blob([config.sampleCSV], { type: 'text/csv' })
    const url  = URL.createObjectURL(blob)
    const a    = document.createElement('a')
    a.href     = url
    a.download = `sample_${importType}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  // ── submit ────────────────────────────────────────────────────────────────
  const handleImport = async () => {
    if (!file) return
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const { data } = importType === 'transactions'
        ? await importsAPI.transactions(file)
        : await importsAPI.products(file)
      setResult(data)
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Import failed. Please check your file and try again.')
    } finally {
      setLoading(false)
    }
  }

  // ── render ────────────────────────────────────────────────────────────────
  return (
    <div className="import-page">

      {/* ── Page header ── */}
      <div className="page-header">
        <div>
          <h2 className="page-title">Import Dataset</h2>
          <p className="page-subtitle">
            Upload a CSV file to bulk-load data into the system. Imported records are immediately
            available for forecasting and analytics.
          </p>
        </div>
      </div>

      {/* ── Type selector ── */}
      <div className="import-tabs">
        {Object.entries(IMPORT_TYPES).map(([key, cfg]) => (
          <button
            key={key}
            className={`import-tab${importType === key ? ' import-tab--active' : ''}`}
            onClick={() => handleTypeChange(key)}
          >
            {cfg.label}
          </button>
        ))}
      </div>

      <div className="import-layout">

        {/* ── Left: upload + preview ── */}
        <div className="import-main">

          {/* Description + sample download */}
          <div className="import-info card">
            <p className="import-info-text">{config.description}</p>
            <div className="import-cols">
              <span className="import-cols-label">Required columns:</span>
              {config.requiredCols.map(c => (
                <span key={c} className="import-col-tag import-col-tag--required">{c}</span>
              ))}
              {config.optionalCols.map(c => (
                <span key={c} className="import-col-tag import-col-tag--optional">{c}</span>
              ))}
            </div>
            <button className="btn-outline btn-sm" onClick={downloadSample}>
              Download sample CSV
            </button>
          </div>

          {/* Drop zone */}
          {!file ? (
            <div
              className={`import-dropzone${dragOver ? ' import-dropzone--over' : ''}`}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={() => fileInputRef.current?.click()}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && fileInputRef.current?.click()}
              aria-label="Upload CSV file"
            >
              <div className="import-dropzone-icon"><IconUpload /></div>
              <p className="import-dropzone-title">Drop your file here</p>
              <p className="import-dropzone-sub">CSV · TSV · Excel (.xlsx / .xls) · ODS · JSON — max 5,000 rows</p>
              <input
                ref={fileInputRef}
                type="file"
                accept={ACCEPTED_EXTENSIONS}
                className="import-file-input"
                onChange={handleInputChange}
                aria-hidden="true"
              />
            </div>
          ) : (
            <div className="import-file-card card">
              <div className="import-file-info">
                <div className="import-file-icon"><IconFile /></div>
                <div>
                  <p className="import-file-name">{file.name}</p>
                  <p className="import-file-size">{(file.size / 1024).toFixed(1)} KB</p>
                </div>
                <button
                  className="import-file-remove"
                  onClick={clearFile}
                  aria-label="Remove file"
                >
                  <IconX />
                </button>
              </div>

              {/* Preview table */}
              {preview && (
                preview.binaryFormat ? (
                  <div className="import-binary-notice">
                    <IconFile />
                    <span>
                      <strong>{preview.ext} file detected.</strong> Preview is not available for
                      spreadsheet files — the data will be parsed server-side when you click Import.
                    </span>
                  </div>
                ) : preview.headers.length > 0 ? (
                  <div className="import-preview">
                    <p className="import-preview-label">Preview (first 5 rows)</p>
                    <div className="import-table-wrapper">
                      <table className="import-table">
                        <thead>
                          <tr>
                            {preview.headers.map(h => <th key={h}>{h}</th>)}
                          </tr>
                        </thead>
                        <tbody>
                          {preview.rows.map((row, ri) => (
                            <tr key={ri}>
                              {preview.headers.map(h => (
                                <td key={h}>{row[h]}</td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ) : null
              )}

              <button
                className="btn-primary btn-full"
                onClick={handleImport}
                disabled={loading}
              >
                {loading ? 'Importing…' : `Import ${config.label}`}
              </button>
            </div>
          )}

          {/* Error banner */}
          {error && (
            <div className="import-alert import-alert--error">
              <IconAlertTriangle />
              <span>{error}</span>
            </div>
          )}

          {/* Result card */}
          {result && (
            <div className={`import-result card${result.skipped > 0 ? ' import-result--warn' : ' import-result--ok'}`}>
              <div className="import-result-header">
                {result.skipped === 0
                  ? <><div className="import-result-icon import-result-icon--ok"><IconCheck /></div><strong>Import successful</strong></>
                  : <><div className="import-result-icon import-result-icon--warn"><IconAlertTriangle /></div><strong>Import complete with warnings</strong></>
                }
              </div>
              <div className="import-result-stats">
                <div className="import-stat">
                  <span className="import-stat-value import-stat-value--ok">{result.inserted}</span>
                  <span className="import-stat-label">Inserted</span>
                </div>
                <div className="import-stat">
                  <span className="import-stat-value import-stat-value--skip">{result.skipped}</span>
                  <span className="import-stat-label">Skipped</span>
                </div>
              </div>

              {result.errors && result.errors.length > 0 && (
                <div className="import-errors">
                  <p className="import-errors-title">Row errors</p>
                  <ul className="import-errors-list">
                    {result.errors.map((e, i) => (
                      <li key={i}>Row {e.row}: {e.error}</li>
                    ))}
                  </ul>
                </div>
              )}

              {result.inserted > 0 && importType === 'transactions' && (
                <p className="import-result-hint">
                  Tip: Go to <strong>Forecasts → Generate All</strong> to run predictions on your new data.
                </p>
              )}

              <button className="btn-outline btn-sm" onClick={clearFile}>
                Import another file
              </button>
            </div>
          )}
        </div>

        {/* ── Right: instructions ── */}
        <aside className="import-sidebar">
          <div className="card import-guide">
            <h3 className="import-guide-title">How it works</h3>
            <ol className="import-guide-steps">
              <li>
                <span className="import-step-num">1</span>
                <div>
                  <strong>Download the sample CSV</strong> to see the expected column structure.
                </div>
              </li>
              <li>
                <span className="import-step-num">2</span>
                <div>
                  <strong>Fill in your data.</strong> Column names are flexible — the system
                  recognises common variations (e.g. <em>product_name</em>, <em>item</em>, <em>crop</em>).
                </div>
              </li>
              <li>
                <span className="import-step-num">3</span>
                <div>
                  <strong>Upload the file.</strong> Preview the first 5 rows to verify the
                  columns look correct before confirming.
                </div>
              </li>
              <li>
                <span className="import-step-num">4</span>
                <div>
                  <strong>Click Import.</strong> Any unknown products are created automatically.
                  Errors are listed row-by-row so you can fix and re-upload.
                </div>
              </li>
            </ol>

            <hr className="import-guide-divider" />

            <h4 className="import-guide-subtitle">Accepted date formats</h4>
            <ul className="import-guide-list">
              <li><code>2025-01-15</code> (YYYY-MM-DD)</li>
              <li><code>15/01/2025</code> (DD/MM/YYYY)</li>
              <li><code>01/15/2025</code> (MM/DD/YYYY)</li>
            </ul>

            <h4 className="import-guide-subtitle">Transaction types</h4>
            <ul className="import-guide-list">
              <li><code>sale</code> — outgoing stock</li>
              <li><code>purchase</code> — incoming stock</li>
              <li>Omit the column → defaults to <code>sale</code></li>
            </ul>

            <h4 className="import-guide-subtitle">Supported file formats</h4>
            <ul className="import-guide-list">
              <li><code>.csv</code> — Comma-separated values</li>
              <li><code>.tsv</code> — Tab-separated values</li>
              <li><code>.xlsx</code> — Excel 2007+ workbook</li>
              <li><code>.xls</code> — Legacy Excel workbook</li>
              <li><code>.ods</code> — LibreOffice / Google Sheets</li>
              <li><code>.json</code> — Array of objects</li>
            </ul>

            <h4 className="import-guide-subtitle">Limits</h4>
            <ul className="import-guide-list">
              <li>Max 5,000 rows per file</li>
              <li>Max 10 MB file size</li>
              <li>UTF-8 or Windows-1252 encoding</li>
            </ul>
          </div>
        </aside>

      </div>
    </div>
  )
}
