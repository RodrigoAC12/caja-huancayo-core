import { Routes, Route, Navigate, NavLink, useNavigate } from 'react-router-dom'
import { LayoutDashboard, Users, ClipboardList, BriefcaseBusiness, Landmark, ReceiptText, BarChart3, ShieldCheck, LogOut } from 'lucide-react'
import { useAuth } from './context/AuthContext.jsx'
import LoginPage from './pages/LoginPage.jsx'
import DashboardPage from './pages/DashboardPage.jsx'
import ClientesPage from './pages/ClientesPage.jsx'
import CarteraPage from './pages/CarteraPage.jsx'
import SolicitudesPage from './pages/SolicitudesPage.jsx'
import OperacionesPage from './pages/OperacionesPage.jsx'
import ReportesPage from './pages/ReportesPage.jsx'
import AuditoriaPage from './pages/AuditoriaPage.jsx'

function PrivateRoute({ children }) {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? children : <Navigate to="/login" replace />
}

function Shell({ children }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const nav = [
    ['/', LayoutDashboard, 'Inicio'],
    ['/clientes', Users, 'Clientes'],
    ['/cartera', BriefcaseBusiness, 'Cartera comercial'],
    ['/solicitudes', ClipboardList, 'Solicitudes'],
    ['/operaciones', ReceiptText, 'Operaciones'],
    ['/reportes', BarChart3, 'Reportes'],
    ['/auditoria', ShieldCheck, 'Auditoría'],
  ]
  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand-panel">
        <img src="/caja-huancayo-logo.png" className="brand-logo" alt="Caja Huancayo" />
        <div className="brand-caption">
          <strong>Portal Interno</strong>
          <span>Gestión operativa y comercial</span>
        </div>
      </div>
      <nav className="sidebar-nav">
        {nav.map(([to, Icon, label]) => (
          <NavLink key={to} to={to} end={to === '/'}>
            <Icon size={18}/><span>{label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
    <main className="content">
      <header className="topbar">
        <div className="topbar-title">
          <b>Core Operativo Caja Huancayo</b>
          <span>Control interno de clientes, créditos, cartera, operaciones y auditoría</span>
        </div>
        <div className="userbox">
          <Landmark size={18}/>
          <span>{user?.nombres || user?.username || 'Usuario'} · {user?.rol || 'perfil interno'}</span>
          <button onClick={() => { logout(); navigate('/login') }}><LogOut size={16}/> Salir</button>
        </div>
      </header>
      {children}
    </main>
  </div>
}

export default function App() {
  return <Routes>
    <Route path="/login" element={<LoginPage />} />
    <Route path="/" element={<PrivateRoute><Shell><DashboardPage /></Shell></PrivateRoute>} />
    <Route path="/clientes" element={<PrivateRoute><Shell><ClientesPage /></Shell></PrivateRoute>} />
    <Route path="/cartera" element={<PrivateRoute><Shell><CarteraPage /></Shell></PrivateRoute>} />
    <Route path="/solicitudes" element={<PrivateRoute><Shell><SolicitudesPage /></Shell></PrivateRoute>} />
    <Route path="/operaciones" element={<PrivateRoute><Shell><OperacionesPage /></Shell></PrivateRoute>} />
    <Route path="/reportes" element={<PrivateRoute><Shell><ReportesPage /></Shell></PrivateRoute>} />
    <Route path="/auditoria" element={<PrivateRoute><Shell><AuditoriaPage /></Shell></PrivateRoute>} />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>
}
