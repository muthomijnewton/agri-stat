import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import { allRecords, amount, displayTime, errorMessage } from '../services/foundation'
import ForecastBand from '../components/charts/ForecastBand'
import RouteMap from '../components/maps/RouteMap'

export default function FarmDashboard() {
  const [locations,setLocations]=useState([]),[location,setLocation]=useState(''),[data,setData]=useState(null),[map,setMap]=useState(null)
  const [suggestionHidden,setSuggestionHidden]=useState(false)
  const [error,setError]=useState(''),[loading,setLoading]=useState(true),[version,setVersion]=useState(0),[runId,setRunId]=useState('')
  useEffect(()=>{const controller=new AbortController();setLoading(true);setError('');setSuggestionHidden(false)
    Promise.all([allRecords('/v1/locations',controller.signal),api.get('/v1/dashboard',{params:location?{location_id:location}:{},signal:controller.signal}),api.get('/v1/map-data',{signal:controller.signal})])
      .then(([l,d,m])=>{setLocations(l);setData(d.data);setMap(m.data);setRunId('')})
      .catch(e=>{if(e.code!=='ERR_CANCELED')setError(errorMessage(e))}).finally(()=>{if(!controller.signal.aborted)setLoading(false)})
    return()=>controller.abort()
  },[location,version])
  const farms=locations.filter(l=>l.location_type==='FARM'),runs=(data?.runs||[]).filter(r=>r.status==='validated'&&r.result.forecasts?.[0]?.date===data.today)
  const run=runs.find(r=>r.id===runId)||runs[0]
  const first=(data?.batches||[]).find(b=>b.status==='EXPIRING_SOON')
  return <div className="workspace-page">
    <header className="page-heading"><div><p className="eyebrow">YOUR FARM, IN FOCUS</p><h1>Farm overview</h1><p className="muted">What you have. What needs attention. What comes next.</p></div><Link className="primary-link" to="/farm-operations">+ Record harvest or sale</Link></header>
    <div className="scope-bar"><label>Location<select value={location} onChange={e=>setLocation(e.target.value)}><option value="">All my locations</option>{locations.filter(l=>l.location_type!=='MARKET').map(l=><option key={l.id} value={l.id}>{l.name}</option>)}</select></label><div className="scope-meta"><span>{loading?'Updating…':data?`Updated ${displayTime(data.as_of)} · EAT`:'Not loaded'}</span><button className="secondary" onClick={()=>setVersion(v=>v+1)} disabled={loading}>Refresh</button></div></div>
    {error&&<div className="error-banner" role="alert">{error}<p>The overview cannot confirm current figures. Retry when the API is available.</p></div>}
    {loading&&!data?<div className="loading-panel" role="status">Loading your farm records…</div>:data&&!error&&<>
      <section className="metric-grid" aria-label="Farm ledger summary">
        <article className="metric"><span>Available produce</span><strong>{Object.keys(data.available_by_unit).length?Object.entries(data.available_by_unit).map(([u,q])=>`${amount(q)} ${u}`).join(' · '):'No stock'}</strong><small>Usable batches · units kept separate</small></article>
        <article className="metric"><span>Farm sales recorded</span><strong>{amount(data.sales_count)}</strong><small>KSh {amount(data.sales_value_kes)} sales value · all time</small></article>
        <article className="metric"><span>Expiring within 3 days</span><strong>{data.batch_counts.expiring_soon}<em> batches</em></strong><small>{data.batch_counts.expired} expired · {data.batch_counts.unknown_expiry} without expiry</small></article>
        <article className="metric"><span>Routes to review</span><strong>{data.high_risk_routes}<em> high risk</em></strong><small>{data.route_count} recorded routes · saved assessment</small></article>
      </section>
      {!suggestionHidden&&<section className="next-actions" aria-label="Next actions"><div><p className="eyebrow">NEXT BEST STEP</p><h2>{!farms.length?'Start with your real farm':first?`Dispatch batch ${first.batch_code} first`:data.batch_counts.expired?'Review expired produce':'Keep your daily records complete'}</h2><p>{!farms.length?'Add a verified farm location, then record the produce you actually harvested.':first?`${first.product} · ${amount(first.quantity)} ${first.unit} · expires ${displayTime(first.expires_at)}. Confirm quality before dispatch.`:data.batch_counts.expired?'Expired batches are excluded from saleable stock. Set them aside and review their condition.':'Confirm yesterday’s sales, including genuine zero-sale days, so forecasting has a reliable foundation.'}</p></div><div className="prompt-choices"><Link className="primary-link" to={!farms.length||first||data.batch_counts.expired?'/farm-operations':'/demand-planning'}>{!farms.length?'Set up farm':first||data.batch_counts.expired?'Review stock':'Confirm daily sales'} →</Link><button className="secondary" onClick={()=>setSuggestionHidden(true)}>Not now</button></div></section>}
      <div className="overview-grid"><section className="panel forecast-panel"><div className="panel-heading"><div><p className="eyebrow">LOOK AHEAD</p><h2>Buyer demand · next 14 days</h2></div><Link to="/demand-planning">Open planning →</Link></div>
        {runs.length>0&&<label>Validated forecast<select value={run?.id||''} onChange={e=>setRunId(e.target.value)}>{runs.map(r=><option key={r.id} value={r.id}>{locations.find(l=>l.id===r.location_id)?.name} · {r.product_name} · {r.result.selected_model}</option>)}</select></label>}
        <ForecastBand forecasts={run?.result.forecasts} unit={run?.unit||'product base units'} model={run?.result.selected_model}/>
      </section>
      <section className="panel attention-panel"><p className="eyebrow">RECORDS THAT MATTER</p><h2>Keep the picture complete</h2><ol className="checklist"><li><strong>Record each harvest</strong><span>Keep dates and quantities for every batch.</span></li><li><strong>Sell from available stock</strong><span>Earliest expiry is allocated first.</span></li><li><strong>Confirm completed days</strong><span>Missing records never become zero sales.</span></li></ol><Link to="/import">Import genuine sales history →</Link><p className="muted">Public price observations stay separate from your farm ledger.</p></section>
      <section className="panel map-panel"><div className="panel-heading"><div><p className="eyebrow">FROM FARM TO MARKET</p><h2>Roads & weather</h2></div><Link to="/roads-weather">Explore map →</Link></div><RouteMap data={map} selected={location} compact /></section>
      <section className="panel batches-panel"><div className="panel-heading"><div><p className="eyebrow">FIRST EXPIRY, FIRST OUT</p><h2>Batch watch</h2></div><Link to="/farm-operations">Manage stock →</Link></div>
        {!data.batches.length?<div className="empty-state"><h3>No harvest batches yet</h3><p>Record an actual harvest to see expiry priorities here.</p></div>:<div className="table-scroll"><table><thead><tr><th>Batch / produce</th><th>Quantity</th><th>Expiry</th><th>Status</th></tr></thead><tbody>{data.batches.slice(0,8).map(b=><tr key={b.id}><td><strong>{b.batch_code}</strong><br/>{b.product}<small>{b.location}</small></td><td>{amount(b.quantity)} {b.unit}</td><td>{displayTime(b.expires_at)}</td><td><span className={`status-badge ${b.status.toLowerCase()}`}>{b.status.replaceAll('_',' ')}</span></td></tr>)}</tbody></table></div>}
        {data.batch_total>8&&<p className="muted">Showing the first 8 of {data.batch_total} batches by expiry.</p>}
      </section></div>
    </>}
  </div>
}
