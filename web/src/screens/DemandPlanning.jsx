import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import { useAuth } from '../context/AuthContext'
import '../css/farm-operations.css'
import ForecastBand from '../components/charts/ForecastBand'

const errorText = e => typeof e.response?.data?.detail === 'string' ? e.response.data.detail : 'Request failed. Check the entries and try again.'
const number = v => Number(v).toLocaleString('en-KE', { maximumFractionDigits: 2 })
export default function DemandPlanning() {
  const { user } = useAuth()
  const [locations, setLocations] = useState([]), [products, setProducts] = useState([]), [routes, setRoutes] = useState([])
  const [location, setLocation] = useState(''), [product, setProduct] = useState(''), [route, setRoute] = useState('')
  const [days, setDays] = useState([]), [runs, setRuns] = useState([])
  const [error, setError] = useState(''), [message, setMessage] = useState(''), [busy, setBusy] = useState(false)
  const [historical, setHistorical] = useState(false)
  useEffect(() => {
    const all = async path => { let rows = [], page; do { page = (await api.get(path, { params: { skip: rows.length, limit: 500 } })).data; rows.push(...page) } while (page.length === 500); return rows }
    Promise.all([all('/v1/locations'), all('/v1/products'), all('/v1/supply-routes')]).then(([l,p,r]) => {
      setLocations(l.filter(x => x.location_type === 'FARM')); setProducts(p); setRoutes(r)
    }).catch(e => setError(errorText(e)))
  }, [])
  async function refresh() {
    if (!location || !product) return
    const [d,r] = await Promise.all([api.get('/v1/planning/demand-days', { params: { location_id: location, product_id: product } }), api.get('/v1/planning/runs', { params: { location_id: location } })])
    setDays(d.data); setRuns(r.data.filter(x => x.product_id === Number(product)))
  }
  useEffect(() => { setDays([]); setRuns([]); setRoute(''); setError('') }, [location, product])
  async function action(work) {
    setBusy(true); setError(''); setMessage('')
    try { await work(); await refresh() } catch (e) { setError(errorText(e)) } finally { setBusy(false) }
  }
  async function confirm(event) {
    event.preventDefault(); const form = event.currentTarget, data = new FormData(form)
    await action(async () => {
      await api.post('/v1/planning/demand-days', { location_id: location, product_id: Number(product), date: data.get('date'),
        quantity: historical ? data.get('quantity') : null, stockout: data.get('stockout') === 'yes', source: data.get('source'), use_sales_ledger: !historical })
      setMessage('Day confirmed. Historical totals are used for modelling only; they do not change stock or create sales receipts.'); form.reset(); setHistorical(false)
    })
  }
  const selected = products.find(p => p.id === Number(product))
  const connected = routes.filter(r => [r.origin_location_id, r.dest_location_id].includes(location))
  return <div className="farm-page">
    <h1>Demand planning</h1>
    <p className="farm-intro">Estimate buyer demand from your farm’s confirmed daily sales. This does not predict harvest yield. Start by recording real harvests and sales on <Link to="/farm-operations">Farm stock &amp; sales</Link>.</p>
    {error && <div className="farm-error" role="alert">{error}</div>}{message && <div className="farm-success" role="status">{message}</div>}
    <section className="farm-card"><h2>1. Choose the farm and produce</h2><div className="farm-grid">
      <label>Farm<select value={location} onChange={e => setLocation(e.target.value)} disabled={busy}><option value="">Choose farm</option>{locations.map(l => <option key={l.id} value={l.id}>{l.name}</option>)}</select></label>
      <label>Produce<select value={product} onChange={e => setProduct(e.target.value)} disabled={busy}><option value="">Choose produce</option>{products.map(p => <option key={p.id} value={p.id}>{p.name} ({p.unit})</option>)}</select></label>
    </div><button disabled={!location || !product || busy} onClick={() => action(async () => {})}>Load records / refresh progress</button></section>
    <section className="farm-card"><h2>2. Confirm each completed day</h2>
      <p>Confirm that all sales for that date are recorded, including a genuine zero-sale day. Flag any day when stock ran out. Missing dates are never filled with made-up sales.</p>
      <p>{days.length} daily records loaded. Training requires at least 120 consecutive, complete days through yesterday, without stockouts. This minimum allows a first test; it does not guarantee useful predictions.</p>
      {user.is_admin && <form onSubmit={confirm}><fieldset disabled={!location || !product || busy}>
        <label>Record source<select value={historical ? 'historical' : 'ledger'} onChange={e => setHistorical(e.target.value === 'historical')}><option value="ledger">Total the recorded farm sales for this date</option><option value="historical">Enter a genuine historical daily total</option></select></label>
        <div className="farm-grid"><label>Completed date<input name="date" type="date" required /></label>
        {historical && <label>Total sold ({selected?.unit || 'base units'})<input name="quantity" type="number" min="0" step="0.0001" required /></label>}
        <label>Did stock run out?<select name="stockout" required defaultValue=""><option value="" disabled>Choose an answer</option><option value="no">No — stock was available</option><option value="yes">Yes — sales may understate demand</option></select></label>
        <label>Source or confirmation note<input name="source" minLength="3" maxLength="180" placeholder="For example: reconciled farm sales book" required /></label></div>
        <button type="submit">Confirm this day</button>
      </fieldset></form>}
      <details><summary>Review recorded days</summary><div className="farm-table"><table><thead><tr><th>Date</th><th>Sold</th><th>Stockout</th><th>Source</th></tr></thead><tbody>{days.map(d => <tr key={d.date}><td>{d.date}</td><td>{number(d.quantity)}</td><td>{d.stockout ? 'Yes' : 'No'}</td><td>{d.source}</td></tr>)}</tbody></table></div></details>
    </section>
    <section className="farm-card"><h2>3. Train and check the forecast</h2>
      <p>Training runs in the background. It compares LightGBM and Prophet with a weekly baseline on 14 hidden days. Earlier rainfall, soil moisture and route rainfall help describe conditions without using future observations.</p>
      <label>Inspected supply route<select value={route} onChange={e => setRoute(e.target.value)} disabled={busy}><option value="">Choose a connected route</option>{connected.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}</select></label>
      {!connected.length && location && <p>Create and inspect a route on <Link to="/roads-weather">Roads &amp; weather</Link>. A route connects two verified locations.</p>}
      {user.is_admin && <button disabled={busy || !route || !product} onClick={() => action(async () => { const r = await api.post('/v1/planning/train', { location_id: location, product_id: Number(product), route_id: route }); setMessage(`Training queued: ${r.data.run_id}. Use Refresh progress to check the result.`) })}>Train and validate</button>}
      {runs.map(run => <article key={run.id} className="farm-card"><h3>{run.status} · {run.id.slice(0,8)}</h3><p>{run.result.message}</p>
        {run.result.candidates && <><p>Holdout: {run.result.holdout_start} to {run.result.holdout_end}. Baseline average error: {number(run.result.baseline.mae)} {selected?.unit}/day. Selected model: {run.result.selected_model || 'none'}.</p><ul>{Object.entries(run.result.candidates).map(([name,r]) => <li key={name}>{name}: {r.error || `average error ${number(r.metrics.mae)}, quantile loss ${number(r.metrics.pinball_loss)}, interval coverage ${number(r.metrics.coverage_p10_p90*100)}%`}</li>)}</ul></>}
        {run.result.forecasts && <ForecastBand forecasts={run.result.forecasts} unit={selected?.unit || 'units'} model={run.result.selected_model} />}
        {run.status === 'validated' && user.is_admin && <button disabled={busy} onClick={() => action(async () => { const r = await api.post(`/v1/planning/runs/${run.id}/plan`); setMessage(`Planning job queued: ${r.data.task_id}. Refresh shortly to see the plan. Job details are available in the API.`) })}>Calculate purchased-stock plan</button>}
        {run.result.planning_message && <p role="status">Planning: {run.result.planning_status} — {run.result.planning_message}</p>}
        {run.result.latest_plan && <div><h4>Purchased-stock planning estimate</h4><p>Adjusted transit: {number(run.result.latest_plan.adjusted_lead_time_days)} days. Reorder point: {number(run.result.latest_plan.reorder_point)} {selected?.unit}. Suggested purchase: {number(run.result.latest_plan.recommended_order_quantity)} {selected?.unit}. Risk: {run.result.latest_plan.risk_level}.</p><p>Calculated at {run.result.latest_plan.as_of}. Recalculate after sales or receipts; this is a saved estimate.</p><ul>{run.result.latest_plan.reasons.map((r,i) => <li key={i}>{r}</li>)}</ul></div>}
      </article>)}
    </section><p>For a farm growing its own produce, use forecasts to plan selling and dispatch. Replenishment quantities apply only when buying additional produce and require an incoming route to this farm; growing more requires a separate crop-production plan.</p>
  </div>
}
