import { useEffect, useState } from 'react'
import api from '../services/api'
import { useAuth } from '../context/AuthContext'
import '../css/market-prices.css'

const SOURCE_NAMES = { kamis: 'KAMIS · Kenya Ministry of Agriculture', hdx: 'HDX · World Food Programme' }
const PAGE_SIZE = 50

export default function MarketPrices() {
  const { user } = useAuth()
  const [summary, setSummary] = useState({ sources: [], markets: 0 })
  const [data, setData] = useState({ items: [], total: 0 })
  const [query, setQuery] = useState('')
  const [search, setSearch] = useState('')
  const [source, setSource] = useState('')
  const [page, setPage] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [revision, setRevision] = useState(0)
  const [job, setJob] = useState(null)
  const [refreshing, setRefreshing] = useState(false)
  const [refreshMessage, setRefreshMessage] = useState('')

  const refreshSources = async () => {
    setRefreshing(true)
    setRefreshMessage('Requesting the latest source data…')
    try {
      const response = await api.post('/v1/market-prices/refresh')
      setJob(response.data.task_id)
    } catch (err) {
      setRefreshMessage(err.response?.data?.detail || 'Could not start the source refresh.')
      setRefreshing(false)
    }
  }

  useEffect(() => {
    if (!job) return
    let active = true
    let timer
    const started = Date.now()
    const poll = async () => {
      try {
        const response = await api.get(`/v1/jobs/${job}`)
        if (!active) return
        if (response.data.status === 'SUCCESS') {
          setRefreshMessage('The latest available prices have been retrieved.')
          setRefreshing(false); setJob(null); setRevision(value => value + 1)
          return
        }
        if (response.data.status === 'FAILURE') throw new Error(response.data.message)
        if (Date.now() - started > 600000) throw new Error('The refresh is taking longer than expected. Reload this page later to check the retrieval date.')
        setRefreshMessage('Fetching source data in the background. Existing prices remain available.')
        timer = setTimeout(poll, 2500)
      } catch (err) {
        if (active) { setRefreshMessage(err.response?.data?.detail || err.message); setRefreshing(false); setJob(null) }
      }
    }
    poll()
    return () => { active = false; clearTimeout(timer) }
  }, [job])

  useEffect(() => {
    let active = true
    setLoading(true)
    setError('')
    Promise.all([
      api.get('/v1/market-summary'),
      api.get('/v1/market-prices', { params: { q: search, source: source || undefined, skip: page * PAGE_SIZE, limit: PAGE_SIZE } }),
    ]).then(([overview, prices]) => {
      if (active) { setSummary(overview.data); setData(prices.data) }
    }).catch(err => {
      if (active) setError(err.response?.data?.detail || 'Could not load market prices. Check that the backend is running.')
    }).finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [search, source, page, revision])

  return <div className="container market-page">
    <div className="page-header">
      <div><h1>Market prices</h1><p>Published agricultural prices from Kenyan markets, with source and observation dates.</p></div>
      {user?.is_admin && <button className="btn btn-primary" disabled={refreshing} onClick={refreshSources}>{refreshing ? 'Refreshing…' : 'Fetch latest prices'}</button>}
    </div>
    {refreshMessage && <p role="status">{refreshMessage}</p>}
    <div className="market-source-grid">
      {summary.sources.map(item => <section className="market-source-card" key={item.source}>
        <h2>{SOURCE_NAMES[item.source] || item.source}</h2>
        <strong>{item.observations.toLocaleString()} price records</strong>
        <p>Latest published date: <b>{item.latest_date}</b></p>
        <p>Retrieved: {item.last_refreshed ? new Date(item.last_refreshed.endsWith('Z') || /[+-]\d\d:\d\d$/.test(item.last_refreshed) ? item.last_refreshed : item.last_refreshed + 'Z').toLocaleString('en-KE') : 'Not yet'}</p>
        <a href={item.source_url} target="_blank" rel="noreferrer">View original source ↗</a>
      </section>)}
    </div>
    <p className="market-note">These are public market quotes. Sales, revenue and stock figures populate when you record your own business activity. HDX contains monthly history; KAMIS supplies recent published pages for seven staple and vegetable commodities.</p>
    <form className="market-controls" onSubmit={event => { event.preventDefault(); setSearch(query.trim()); setPage(0) }}>
      <label>Product or market<input value={query} onChange={event => setQuery(event.target.value)} placeholder="For example, maize or Nairobi" /></label>
      <label>Source<select value={source} onChange={event => { setSource(event.target.value); setPage(0) }}>
        <option value="">All sources</option><option value="kamis">KAMIS</option><option value="hdx">HDX / WFP</option>
      </select></label>
      <button className="btn btn-primary" type="submit">Search</button>
    </form>
    {error && <p role="alert" className="error">{error}</p>}
    {loading ? <p role="status">Loading market prices…</p> : <>
      <p>{data.total.toLocaleString()} matching price records · {summary.markets} markets in the catalog</p>
      {data.items.length === 0 ? <p>No published prices match this search.</p> : <div className="market-table-wrap">
        <table className="market-table"><thead><tr><th>Product</th><th>Market</th><th>Published date</th><th>Price per unit</th><th>Quote</th><th>Source</th></tr></thead>
          <tbody>{data.items.map(item => <tr key={item.id}>
            <td>{item.product}</td><td>{item.market}</td><td>{item.date}</td>
            <td>{item.currency} {Number(item.price).toLocaleString('en-KE', { maximumFractionDigits: 2, minimumFractionDigits: 2 })} / {item.unit}</td>
            <td>{item.price_type}</td><td><a href={item.source_url} target="_blank" rel="noreferrer">{item.source.toUpperCase()} ↗</a></td>
          </tr>)}</tbody>
        </table>
      </div>}
      <div className="market-pagination">
        <button disabled={page === 0} onClick={() => setPage(page - 1)}>Previous</button>
        <span>Page {page + 1} of {Math.max(1, Math.ceil(data.total / PAGE_SIZE))}</span>
        <button disabled={(page + 1) * PAGE_SIZE >= data.total} onClick={() => setPage(page + 1)}>Next</button>
      </div>
    </>}
  </div>
}
