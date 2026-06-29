import { useEffect, useState } from 'react'
import api from '../services/api.js'

export default function SolicitudesPage() {
  const [items, setItems] = useState([])
  const [estado, setEstado] = useState('')
  const load = () => api.get('/solicitudes', { params: { estado: estado || undefined } }).then(r => setItems(r.data))
  useEffect(() => { load() }, [])
  async function cambiar(id, estado) {
    await api.patch(`/solicitudes/${id}/estado`, { estado, comentario: `Cambio a ${estado} desde portal interno`, monto_aprobado: estado === 'aprobado' ? 5000 : undefined })
    load()
  }
  return <section>
    <div className="page-head"><h1>Solicitudes de crédito</h1><p>Evaluación y seguimiento de expedientes.</p></div>
    <div className="toolbar"><select value={estado} onChange={e => setEstado(e.target.value)}><option value="">Todos</option><option>enviado</option><option>en_evaluacion</option><option>aprobado</option><option>rechazado</option></select><button onClick={load}>Filtrar</button></div>
    <div className="panel"><table><thead><tr><th>Expediente</th><th>Cliente</th><th>Monto</th><th>Estado</th><th>Canal</th><th>Asesor</th><th>Acciones</th></tr></thead><tbody>
      {items.map(x => <tr key={x.id}><td>{x.numero_expediente}</td><td>{x.cliente_nombre}</td><td>S/ {Number(x.monto_solicitado).toLocaleString('es-PE')}</td><td><span className="badge">{x.estado}</span></td><td>{x.canal}</td><td>{x.asesor_nombre || '-'}</td><td><button className="small" onClick={() => cambiar(x.id, 'en_evaluacion')}>Evaluar</button><button className="small ok" onClick={() => cambiar(x.id, 'aprobado')}>Aprobar</button><button className="small danger" onClick={() => cambiar(x.id, 'rechazado')}>Rechazar</button></td></tr>)}
    </tbody></table></div>
  </section>
}
