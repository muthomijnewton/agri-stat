import { lazy, Suspense, useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route, Link, NavLink, Navigate, useNavigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import RequireAuth from './components/RequireAuth'
import FarmDashboard from './screens/FarmDashboard'
import './css/App.css'
import './css/workspace.css'
const Landing=lazy(()=>import('./screens/Landing'))
const Login=lazy(()=>import('./screens/Login'))
const Register=lazy(()=>import('./screens/Register'))
const FarmOperations=lazy(()=>import('./screens/FarmOperations'))
const DemandPlanning=lazy(()=>import('./screens/DemandPlanning'))
const RoadsWeather=lazy(()=>import('./screens/RoadsWeather'))
const HistoryImport=lazy(()=>import('./screens/HistoryImport'))
const MarketPrices=lazy(()=>import('./screens/MarketPrices'))
const Products=lazy(()=>import('./screens/Products'))
const Profile=lazy(()=>import('./screens/Profile'))
const Transactions=lazy(()=>import('./screens/Transactions'))
const Forecasts=lazy(()=>import('./screens/Forecasts'))
const Recommendations=lazy(()=>import('./screens/Recommendations'))
const Analytics=lazy(()=>import('./screens/Analytics'))
const LegacyImport=lazy(()=>import('./screens/Import'))
const LegacyDashboard=lazy(()=>import('./screens/Dashboard'))

function Shell() {
  const {isAuthenticated,user,logout}=useAuth(), navigate=useNavigate()
  const [menu,setMenu]=useState(false),[online,setOnline]=useState(typeof navigator !== 'undefined' ? navigator.onLine : true)
  useEffect(()=>{const update=()=>setOnline(navigator.onLine);window.addEventListener('online',update);window.addEventListener('offline',update);return()=>{window.removeEventListener('online',update);window.removeEventListener('offline',update)}},[])
  const primary=[['/dashboard','◫','Overview'],['/farm-operations','▤','Stock & sales'],['/demand-planning','↗','Demand planning'],['/roads-weather','⌁','Roads & weather'],['/market-prices','▥','Market prices'],['/products','□','Produce catalog']]
  return <div className={isAuthenticated?'workspace':'public-app'}>
    <a className="skip-link" href="#main-content">Skip to content</a>
    {isAuthenticated&&<>
      <aside className={`workspace-sidebar ${menu?'is-open':''}`} aria-label="Main navigation">
        <Link className="workspace-brand" to="/dashboard" onClick={()=>setMenu(false)}><span aria-hidden="true">↗</span><strong>AgriStat<small>FARM INTELLIGENCE</small></strong></Link>
        <p className="nav-label">YOUR WORKSPACE</p><nav>{primary.map(([path,icon,name])=><NavLink key={path} to={path} title={name} onClick={()=>setMenu(false)}><span className="nav-icon" aria-hidden="true">{icon}</span>{name}</NavLink>)}{user?.is_admin&&<NavLink to="/import" title="Import farm history" onClick={()=>setMenu(false)}><span className="nav-icon" aria-hidden="true">⇧</span>Import farm history</NavLink>}</nav>
        <details className="legacy-navigation"><summary>Earlier records</summary><p>These pages use the original transaction ledger.</p><nav>{[['/transactions','Transactions'],['/forecasts','Earlier forecasts'],['/recommendations','Earlier recommendations'],['/analytics','Earlier analytics'],['/legacy/import','Earlier import']].map(([path,name])=><NavLink to={path} key={path} onClick={()=>setMenu(false)}>{name}</NavLink>)}</nav></details>
        <div className="sidebar-note"><strong>Built on real records.</strong><p>Your farm sales, public market prices and predictions remain distinct.</p></div>
      </aside>
      <header className="workspace-topbar"><button className="menu-toggle secondary" aria-expanded={menu} aria-label="Toggle navigation" onClick={()=>setMenu(!menu)}>☰ Menu</button><span className="workspace-title">GROW WITH CLARITY</span><div className="topbar-user"><span className={`connection-pill ${online?'':'offline'}`}>{online?'● Network available':'○ Offline · submissions unavailable'}</span><Link to="/profile">{user?.full_name||user?.username||'Profile'}</Link><button className="secondary" onClick={()=>{logout();navigate('/login',{replace:true})}}>Sign out</button></div></header>
    </>}
    {!online&&isAuthenticated&&<p className="offline-message" role="status">Offline: live figures and submissions are unavailable. This web app does not queue new sales offline.</p>}
    <main id="main-content" className={isAuthenticated?'workspace-content':'public-content'} tabIndex="-1"><Suspense fallback={<div className="loading-panel" role="status">Opening page…</div>}><Routes>
      <Route path="/" element={isAuthenticated?<Navigate to="/dashboard" replace/>:<Landing/>}/>
      <Route path="/login" element={isAuthenticated?<Navigate to="/dashboard" replace/>:<Login/>}/>
      <Route path="/register" element={isAuthenticated?<Navigate to="/dashboard" replace/>:<Register/>}/>
      {[
        ['/dashboard',FarmDashboard],['/farm-operations',FarmOperations],['/demand-planning',DemandPlanning],['/roads-weather',RoadsWeather],
        ['/import',HistoryImport],['/market-prices',MarketPrices],['/products',Products],['/profile',Profile],
        ['/transactions',Transactions],['/forecasts',Forecasts],['/recommendations',Recommendations],['/analytics',Analytics],['/legacy/import',LegacyImport],['/legacy/dashboard',LegacyDashboard],
      ].map(([path,Page])=><Route key={path} path={path} element={<RequireAuth><Page/></RequireAuth>}/>)}
      <Route path="*" element={<Navigate to="/" replace/>}/>
    </Routes></Suspense>{isAuthenticated&&<footer className="workspace-footer">AgriStat · Your records, your decisions. <span>Times shown in East Africa Time where indicated.</span></footer>}</main>
  </div>
}
export default function App(){return <BrowserRouter><AuthProvider><Shell/></AuthProvider></BrowserRouter>}
