import { useEffect, useState } from 'react'
import api from '../services/api.js'

export default function ClientesPage() {
  const [q, setQ] = useState('')
  const [items, setItems] = useState([])
  const load = () => api.get('/clientes', { params: { q: q || undefined } }).then(r => setItems(r.data))
  useEffect(() => { load() }, [])
  return <section>
    <div className="page-head"><h1>Clientes</h1><p>Consulta de clientes y negocios vinculados.</p></div>
    <div className="toolbar"><input placeholder="Buscar por DNI o nombre" value={q} onChange={e => setQ(e.target.value)} /><button onClick={load}>Buscar</button></div>
    <div className="panel"><table><thead><tr><th>DNI</th><th>Cliente</th><th>Teléfono</th><th>Negocio</th><th>Ingresos</th></tr></thead><tbody>
      {items.map(c => <tr key={c.id}><td>{c.numero_documento}</td><td>{c.nombres} {c.apellidos}</td><td>{c.telefono}</td><td>{c.nombre_negocio || '-'}</td><td>S/ {Number(c.ingresos_estimados || 0).toLocaleString('es-PE')}</td></tr>)}
    </tbody></table></div>
  </section>
}
