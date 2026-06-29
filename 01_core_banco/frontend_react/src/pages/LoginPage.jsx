import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(username.trim(), password)
      navigate('/')
    } catch (err) {
      setError(err?.response?.data?.detail || 'No se pudo iniciar sesión. Verifique sus credenciales.')
    } finally {
      setLoading(false)
    }
  }

  return <div className="login-page">
    <section className="login-card enterprise-card">
      <img src="/caja-huancayo-logo.png" alt="Caja Huancayo" className="login-logo" />
      <div className="login-heading">
        <h1>Acceso al Portal Interno</h1>
        <p>Gestión operativa de clientes, cartera, créditos, solicitudes y operaciones.</p>
      </div>
      <form onSubmit={handleSubmit}>
        <label>Usuario institucional</label>
        <input value={username} onChange={e => setUsername(e.target.value)} placeholder="Ingrese su usuario o código" autoComplete="username" required />
        <label>Contraseña</label>
        <input value={password} onChange={e => setPassword(e.target.value)} type="password" placeholder="Ingrese su contraseña" autoComplete="current-password" required />
        {error && <div className="alert error">{error}</div>}
        <button disabled={loading}>{loading ? 'Validando acceso...' : 'Ingresar al sistema'}</button>
      </form>
      <div className="security-note">Acceso restringido a personal autorizado.</div>
    </section>
  </div>
}
