import { useId, useState } from 'react'
import { amount } from '../../services/foundation'
export default function ForecastBand({ forecasts = [], unit = 'units', model }) {
  const id = useId().replaceAll(':', ''), [active, setActive] = useState(null)
  if (!forecasts.length) return <div className="empty-state"><span className="empty-symbol" aria-hidden="true">↗</span><h3>A forecast starts with your records</h3><p>Confirm complete daily sales and validate a model to see the next 14 days. Public market prices are not your farm’s demand.</p></div>
  const w=760, h=250, left=58, right=18, top=18, bottom=38
  const maximum=Math.max(1,...forecasts.map(f=>Number(f.p90)))*1.12
  const x=i=>left+i*(w-left-right)/Math.max(1,forecasts.length-1)
  const y=v=>h-bottom-Number(v)/maximum*(h-top-bottom)
  const band=forecasts.map((f,i)=>`${x(i)},${y(f.p90)}`).concat([...forecasts].reverse().map((f,i)=>`${x(forecasts.length-i-1)},${y(f.p10)}`)).join(' ')
  const median=forecasts.map((f,i)=>`${x(i)},${y(f.p50)}`).join(' ')
  const selected=active===null ? null : forecasts[active]
  return <div className="forecast-band">
    <div className="chart-legend"><span><i className="legend-line" />Middle estimate · P50</span><span><i className="legend-band" />Estimated range · P10–P90</span></div>
    <svg viewBox={`0 0 ${w} ${h}`} role="img" aria-labelledby={`${id}-title ${id}-desc`}>
      <title id={`${id}-title`}>14-day buyer demand forecast in {unit}</title><desc id={`${id}-desc`}>Shaded lower and upper predictive quantiles with a median line. Exact values are in the table below.</desc>
      <defs><pattern id={id} width="7" height="7" patternUnits="userSpaceOnUse"><path d="M0 7L7 0" stroke="#70897c" strokeWidth="1" /></pattern></defs>
      {[0,.25,.5,.75,1].map(r=><g key={r}><line x1={left} y1={y(maximum*r)} x2={w-right} y2={y(maximum*r)} stroke="#d6ded7"/><text x={left-9} y={y(maximum*r)+4} textAnchor="end" fill="#334b40" fontSize="12">{amount(maximum*r)}</text></g>)}
      <polygon points={band} fill="#d8e8dc" /><polygon points={band} fill={`url(#${id})`} opacity=".65"/><polyline points={median} fill="none" stroke="#173e2b" strokeWidth="3"/>
      {forecasts.map((f,i)=><g key={f.date}>
        <circle cx={x(i)} cy={y(f.p50)} r={active===i?7:4} fill="#173e2b" tabIndex="0" role="button" aria-label={`${f.date}: P10 ${amount(f.p10)}, P50 ${amount(f.p50)}, P90 ${amount(f.p90)} ${unit}`} onFocus={()=>setActive(i)} onMouseEnter={()=>setActive(i)} onClick={()=>setActive(i)} onKeyDown={e=>{if(e.key==='Enter'||e.key===' ')setActive(i)}} />
        {(i===0||i===forecasts.length-1||i%3===0)&&<text x={x(i)} y={h-12} textAnchor="middle" fill="#334b40" fontSize="12">{f.date.slice(5)}</text>}
      </g>)}
    </svg>
    <p className="chart-readout" aria-live="polite">{selected ? `${selected.date}: ${amount(selected.p50)} ${unit} median · estimated range ${amount(selected.p10)}–${amount(selected.p90)} ${unit}` : 'Focus or select a point for its estimates.'}</p>
    <p className="muted">{model && `${model} · `}This range is an estimate, not a guarantee. It predicts sales demand, not harvest yield.</p>
    <details><summary>View exact forecast values</summary><div className="table-scroll"><table><thead><tr><th>Date</th><th>P10 ({unit})</th><th>P50 ({unit})</th><th>P90 ({unit})</th></tr></thead><tbody>{forecasts.map(f=><tr key={f.date}><td>{f.date}</td><td>{amount(f.p10)}</td><td>{amount(f.p50)}</td><td>{amount(f.p90)}</td></tr>)}</tbody></table></div></details>
  </div>
}
