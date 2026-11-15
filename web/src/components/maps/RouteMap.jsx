import { useEffect, useRef, useState } from 'react'
import 'leaflet/dist/leaflet.css'
import { amount, displayTime } from '../../services/foundation'
const colors = { HIGH:'#8e231d', MODERATE:'#76500b', LOW:'#17472f', UNKNOWN:'#4e5961' }
export default function RouteMap({ data, selected = '', compact = false }) {
  const element=useRef(null), [error,setError]=useState(''), [layer,setLayer]=useState('routes')
  useEffect(()=>{
    let map, cancelled=false, observer
    import('leaflet').then(module=>{
      if(cancelled||!element.current)return
      const L=module.default
      map=L.map(element.current,{scrollWheelZoom:false}).setView([.2,37.8],6)
      const tiles=L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}).addTo(map)
      tiles.on('tileerror',()=>{if(!cancelled)setError('Background tiles could not load. Recorded locations and routes remain available below.')})
      const bounds=[]
      const connected=(data?.routes||[]).filter(r=>!selected||r.origin_location_id===selected||r.dest_location_id===selected)
      const visible=new Set([selected,...connected.flatMap(r=>[r.origin_location_id,r.dest_location_id])])
      for(const location of data?.locations||[]){
        if(location.latitude===null||location.longitude===null||selected&&!visible.has(location.id))continue
        const point=[Number(location.latitude),Number(location.longitude)];bounds.push(point)
        const text=document.createElement('div')
        text.textContent=`${location.name} · ${location.type}. Three-day forecast rain: ${location.rain_3d_mm===null?'unknown':amount(location.rain_3d_mm)+' mm'}. Soil moisture: ${location.soil_moisture===null?'unknown':amount(location.soil_moisture*100)+'% (estimated)'}. Weather fetched: ${displayTime(location.fetched_at)}.`
        const rain=location.rain_3d_mm
        const color=layer==='rain'?(rain===null?'#4e5961':rain>=50?'#8e231d':rain>15?'#76500b':'#17472f'):layer==='soil'?'#154f70':'#173e2b'
        L.circleMarker(point,{radius:location.id===selected?10:6,color,fillColor:color,fillOpacity:.75,weight:2}).bindPopup(text).addTo(map)
        if(layer!=='routes'&&(layer==='rain'?rain!==null:location.soil_moisture!==null)) L.circle(point,{radius:2500,color,fillOpacity:.1,weight:1,dashArray:'4 5'}).addTo(map)
      }
      for(const route of connected){
        if(!route.geometry)continue
        const text=document.createElement('div');text.textContent=`${route.name}. Saved risk: ${route.risk}. Inspected: ${displayTime(route.inspected_at)}. Unknown road surface: ${route.unknown_surface_ratio===null?'not inspected':amount(Number(route.unknown_surface_ratio)*100)+'%'}.`
        const line=L.geoJSON(route.geometry,{style:{color:colors[route.risk]||colors.UNKNOWN,weight:5,dashArray:route.risk==='UNKNOWN'?'6 6':route.risk==='HIGH'?'2 7':undefined}}).bindPopup(text).addTo(map)
        if(line.getBounds().isValid())bounds.push(line.getBounds().getSouthWest(),line.getBounds().getNorthEast())
      }
      if(bounds.length)map.fitBounds(bounds,{padding:[28,28],maxZoom:11})
      observer=new ResizeObserver(()=>map.invalidateSize());observer.observe(element.current)
    }).catch(()=>setError('The interactive map could not load. Use the location and route tables.'))
    return()=>{cancelled=true;observer?.disconnect();map?.remove()}
  },[data,selected,layer])
  return <div className="route-map"><div className="map-toolbar"><label>Map layer<select value={layer} onChange={e=>{setError('');setLayer(e.target.value)}}><option value="routes">Road corridors</option><option value="rain">3-day rainfall forecast</option><option value="soil">Estimated soil moisture</option></select></label><span className="muted">Select a point or line for details</span></div>
    {error&&<p className="notice" role="status">{error}</p>}<div ref={element} className={compact?'map-canvas compact':'map-canvas'} role="region" aria-label="Recorded locations, road corridors and weather" />
    <div className="map-legend"><span>— Low</span><span>— Moderate</span><span>┄ High</span><span>┄ Unknown</span></div>
    <p className="muted">Dashed circles show approximate 5 km weather cells, not measured flood or crop-stress boundaries. Forecast rain and soil moisture are model estimates. Saved route risk is not a live road-closure report.</p>
  </div>
}
