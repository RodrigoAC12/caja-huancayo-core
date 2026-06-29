import { useEffect, useState } from 'react'
import api from '../services/api.js'

export default function AuditoriaPage() {
  const [items, setItems] = useState([])
  const [error, setError] = useState('')
  useEffect(() => { api.get('/auditoria').then(r => setItems(r.data)).catch(e => setError(e?.response?.data?.detail || 'No autorizado')) }, [])
  return <section>
    <div className="page-head"><h1>Auditoría</h1><p>Trazabilidad de acciones del sistema interno.</p></div>
    {error && <div className="alert error">{error}</div>}
    <div className="panel"><table><thead><tr><th>Fecha</th><th>Usuario</th><th>Acción</th><th>Módulo</th><th>Descripción</th></tr></thead><tbody>
      {items.map(x => <tr key={x.id}><td>{new Date(x.created_at).toLocaleString('es-PE')}</td><td>{x.username || '-'}</td><td>{x.accion}</td><td>{x.modulo}</td><td>{x.descripcion}</td></tr>)}
    </tbody></table></div>
  </section>
}
