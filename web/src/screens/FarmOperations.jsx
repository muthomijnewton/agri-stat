import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import { useAuth } from '../context/AuthContext'
import '../css/farm-operations.css'

const explainError = e => {
  const detail = e.response?.data?.detail
  return typeof detail === 'string' ? detail : Array.isArray(detail) ? detail.map(x => x.msg).join('; ') : 'The request could not be completed. Please try again.'
}
const money = value => Number(value).toLocaleString('en-KE', { style: 'currency', currency: 'KES' })
const stamp = value => new Date(value.endsWith('Z') || /[+-]\d\d:\d\d$/.test(value) ? value : `${value}Z`).toLocaleString()

export default function FarmOperations() {
  const { user } = useAuth()
  const draftKey = `agristat-pending-farm-sale-${user.id}`
  const [pending, setPending] = useState(() => {
    try { return JSON.parse(sessionStorage.getItem(draftKey) || 'null') } catch { return null }
  })
  const [locations, setLocations] = useState([])
  const [products, setProducts] = useState([])
  const [location, setLocation] = useState(pending?.location_id || '')
  const [stock, setStock] = useState([])
  const [sales, setSales] = useState([])
  const [readiness, setReadiness] = useState(null)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [busy, setBusy] = useState(false)
  const [loading, setLoading] = useState(true)
  const [saleProduct, setSaleProduct] = useState('')
  const [receiptProduct, setReceiptProduct] = useState('')
  const generation = useRef(0)
  const saleLock = useRef(false)

  async function catalog() {
    const all = async path => {
      let rows = [], page
      do { page = (await api.get(path, { params: { skip: rows.length, limit: 500 } })).data; rows.push(...page) } while (page.length === 500)
      return rows
    }
    const [farms, items] = await Promise.all([all('/v1/locations'), all('/v1/products')])
    const ownFarms = farms.filter(x => x.location_type === 'FARM')
    setLocations(ownFarms); setProducts(items)
    setLocation(current => current || ownFarms[0]?.id || '')
  }
  async function refresh(id = location) {
    const version = ++generation.current
    if (!id) { setStock([]); setSales([]); setReadiness(null); setLoading(false); return }
    setLoading(true)
    try {
      const results = await Promise.all([
        api.get('/v1/stock', { params: { location_id: id } }),
        api.get('/v1/sales', { params: { location_id: id } }),
        api.get('/v1/forecast-readiness', { params: { location_id: id } }),
      ])
      if (version !== generation.current) return
      setStock(results[0].data.items); setSales(results[1].data); setReadiness(results[2].data)
    } catch (e) { if (version === generation.current) setError(explainError(e)) }
    finally { if (version === generation.current) setLoading(false) }
  }
  useEffect(() => { catalog().catch(e => { setError(explainError(e)); setLoading(false) }) }, [])
  useEffect(() => { setError(''); refresh(location) }, [location])

  async function createFarm(event) {
    event.preventDefault(); const form = event.currentTarget; const data = new FormData(form)
    setBusy(true); setError(''); setMessage('')
    try {
      const result = await api.post('/v1/locations', { name: data.get('name'), location_type: 'FARM', latitude: data.get('latitude'), longitude: data.get('longitude') })
      await catalog(); setLocation(result.data.id); form.reset(); setMessage('Farm saved. You can now record harvested stock.')
    } catch (e) { setError(explainError(e)) } finally { setBusy(false) }
  }
  async function receive(event) {
    event.preventDefault(); const form = event.currentTarget; const data = new FormData(form)
    setBusy(true); setError(''); setMessage('')
    try {
      await api.post('/v1/inventory-batches', { location_id: location, product_id: Number(receiptProduct),
        batch_code: data.get('batch'), quantity_on_hand: data.get('quantity'), unit_cost: data.get('cost'),
        received_at: new Date(data.get('received')).toISOString(), expires_at: data.get('expires') ? new Date(data.get('expires')).toISOString() : null })
      form.reset(); setReceiptProduct(''); setMessage('Harvested stock recorded. It is now included in available stock.'); await refresh()
    } catch (e) { setError(explainError(e)) } finally { setBusy(false) }
  }
  function clearPending() { sessionStorage.removeItem(draftKey); setPending(null) }
  async function sell(event) {
    event.preventDefault()
    if (saleLock.current) return
    saleLock.current = true
    const form = event.currentTarget; const data = new FormData(form)
    const request = pending || { client_event_id: crypto.randomUUID(), location_id: location,
      items: [{ product_id: Number(saleProduct), quantity: data.get('quantity'), unit_price: data.get('price') }] }
    setBusy(true); setError(''); setMessage('')
    try {
      sessionStorage.setItem(draftKey, JSON.stringify(request)); setPending(request)
      const result = await api.post('/v1/sales', request)
      clearPending(); form.reset(); setSaleProduct('')
      setMessage(`Sale ${result.data.id.slice(0, 8)} ${result.data.replayed ? 'confirmed (already recorded)' : 'recorded'}: ${money(result.data.total_amount)}. Stock was deducted once, using the earliest-expiring batches.`)
      await refresh(request.location_id)
    } catch (e) {
      const status = e.response?.status
      if ([400, 404, 409, 422].includes(status)) clearPending()
      setError(explainError(e))
    } finally { setBusy(false); saleLock.current = false }
  }
  const productOptions = <><option value="">Choose produce</option>{products.map(p => <option key={p.id} value={p.id}>{p.name} ({p.unit})</option>)}</>
  const receiptUnit = products.find(p => String(p.id) === receiptProduct)?.unit || 'base units'
  const saleUnit = products.find(p => String(p.id) === saleProduct)?.unit || 'base units'

  return <div className="farm-page">
    <h1>Farm stock & sales</h1>
    <p className="farm-intro">Record what you harvested and sold. AgriStat uses the batches that expire first and keeps a record of every stock deduction.</p>
    {error && <div role="alert" className="farm-error">{error}</div>}
    {message && <div role="status" className="farm-success">{message}</div>}
    <section className="farm-card">
      <h2>1. Choose your farm</h2>
      <label>Farm<select value={location} disabled={busy || !!pending} onChange={e => setLocation(e.target.value)}><option value="">Choose a farm</option>{locations.map(f => <option value={f.id} key={f.id}>{f.name}</option>)}</select></label>
      {!locations.length && <p>No farm has been recorded yet. Add your real farm to begin; public market locations are kept separate.</p>}
      {user.is_admin && <details><summary>Add a farm</summary><form className="farm-form" onSubmit={createFarm}>
        <label>Farm name<input name="name" required maxLength={255} /></label>
        <label>Latitude<input name="latitude" type="number" min="-90" max="90" step="0.0000001" required /></label>
        <label>Longitude<input name="longitude" type="number" min="-180" max="180" step="0.0000001" required /></label>
        <p>Use verified farm coordinates. They will identify the weather grid for this location.</p>
        <button disabled={busy || !!pending} type="submit">Save farm</button>
      </form></details>}
    </section>
    {location && <>
      <section className="farm-card"><h2>Available produce</h2>
        {loading ? <p>Loading stock…</p> : !stock.length ? <p>No harvested stock recorded for this farm yet.</p> : <div className="farm-table"><table><thead><tr><th>Produce</th><th>Available</th><th>Expired</th><th>Available with unknown expiry</th></tr></thead><tbody>{stock.map(p => <tr key={p.product_id}><td>{p.name}</td><td>{Number(p.available)} {p.unit}</td><td>{Number(p.expired)} {p.unit}</td><td>{Number(p.unknown_expiry)} {p.unit}</td></tr>)}</tbody></table></div>}
        <p className="farm-help">Expired or future-dated batches cannot be sold. Batches without an expiry date are used after batches with a known expiry.</p>
      </section>
      <div className="farm-columns">
        {user.is_admin && <section className="farm-card"><h2>2. Record harvested stock</h2><p>Each batch is a separate harvest or lot. Enter its actual quantity and dates.</p>
          <form className="farm-form" onSubmit={receive}>
            <label>Produce<select value={receiptProduct} onChange={e => setReceiptProduct(e.target.value)} required>{productOptions}</select></label>
            <label>Batch code<input name="batch" required maxLength={100} placeholder="Your harvest or lot reference" /></label>
            <label>Quantity ({receiptUnit})<input name="quantity" type="number" min="0.0001" step="0.0001" required /></label>
            <label>Cost per {receiptUnit} (KES)<input name="cost" type="number" min="0" step="0.0001" required /></label>
            <label>Received into stock<input name="received" type="datetime-local" required /></label>
            <label>Expiry date and time, if known<input name="expires" type="datetime-local" /></label>
            <button type="submit" disabled={busy || !!pending}>Record harvested stock</button>
          </form>
        </section>}
        <section className="farm-card"><h2>3. Record a sale</h2><p>Enter the quantity actually sold and your actual selling price. FEFO selects the stock batches automatically.</p>
          {pending && <p role="status">This sale is awaiting confirmation: {pending.items[0].quantity} units at KES {pending.items[0].unit_price} each. Retry the same sale to confirm it without deducting stock twice.</p>}
          <form className="farm-form" onSubmit={sell}>
            <fieldset disabled={!!pending || busy}>
              <label>Produce<select value={saleProduct} onChange={e => setSaleProduct(e.target.value)} required>{productOptions}</select></label>
              <label>Quantity ({saleUnit})<input name="quantity" type="number" min="0.0001" step="0.0001" required /></label>
              <label>Selling price per {saleUnit} (KES)<input name="price" type="number" min="0" step="0.01" required /></label>
            </fieldset>
            <button type="submit" disabled={busy}>{busy ? 'Saving…' : pending ? 'Retry this sale' : 'Record sale & deduct stock'}</button>
          </form>
        </section>
      </div>
      <section className="farm-card"><h2>4. Sales history and forecasting</h2>
        <p>{readiness?.sales_recorded ?? 0} farm sales recorded. Confirm daily totals and check model readiness on <Link to="/demand-planning">Demand planning</Link>.</p>
        <p className="farm-help">A day without a recorded sale is not automatically a zero-demand day. Public market prices also do not count as your farm's sales.</p>
        {!loading && !sales.length && <p>Your recorded sales will appear here.</p>}
        {sales.map(sale => <details key={sale.id} className="farm-sale"><summary>{stamp(sale.sold_at)} · {money(sale.total_amount)} · reference {sale.id.slice(0,8)}</summary>
          {sale.items.map(line => <div key={line.product_id}><p><strong>{products.find(p => p.id === line.product_id)?.name || `Product ${line.product_id}`}</strong>: {Number(line.quantity)} {line.unit} at {money(line.unit_price)} per {line.unit}</p>
            <ul>{line.allocations.map(a => <li key={a.batch_id}>Batch {a.batch_code || a.batch_id.slice(0,8)}: {Number(a.quantity)} {line.unit}</li>)}</ul></div>)}
        </details>)}
        {sales.length === 20 && <p>Showing the 20 most recent sales for this farm.</p>}
      </section>
    </>}
  </div>
}
