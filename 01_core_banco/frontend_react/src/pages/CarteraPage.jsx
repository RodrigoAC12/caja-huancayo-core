import { useEffect, useState } from 'react'
import api from '../services/api.js'

export default function CarteraPage() {
  const [items, setItems] = useState([])
  const load = () => api.get('/cartera').then(r => setItems(r.data))
  useEffect(() => { load() }, [])

  async function marcar(id) {
    await api.post(`/cartera/${id}/visita`, {
      resultado: 'visitado',
      observacion: 'Visita registrada desde portal core sin GPS móvil'
    })
    load()
  }

  function mapsLink(x) {
    if (!x.lat_negocio || !x.lng_negocio) return null
    return `https://www.google.com/maps/search/?api=1&query=${x.lat_negocio},${x.lng_negocio}`
  }

  return <section>
    <div className="page-head"><h1>Cartera diaria</h1><p>Asignaciones de asesores, negocio, ubicación y estado de visita.</p></div>
    <div className="panel"><table><thead><tr><th>Cliente</th><th>Negocio / ubicación</th><th>Gestión</th><th>Prioridad</th><th>Monto ref.</th><th>Estado</th><th>GPS visita</th><th>Asesor</th><th></th></tr></thead><tbody>
      {items.map(x => <tr key={x.id}>
        <td><b>{x.cliente_nombre}</b><br/><small>DNI {x.numero_documento}</small></td>
        <td>
          <b>{x.nombre_negocio || 'Sin negocio'}</b><br/>
          <small>{x.direccion_negocio || x.direccion_domicilio || 'Sin dirección'}</small><br/>
          <small>{x.referencia_negocio || x.referencia_direccion || ''}</small><br/>
          {mapsLink(x) ? <a href={mapsLink(x)} target="_blank" rel="noreferrer">Ver mapa</a> : <small>Sin coordenadas</small>}
        </td>
        <td>{x.tipo_gestion}</td>
        <td>{x.prioridad}</td>
        <td>S/ {Number(x.monto_referencial).toLocaleString('es-PE')}</td>
        <td><span className="badge">{x.estado_visita}</span></td>
        <td><small>{x.lat_visita && x.lng_visita ? `${Number(x.lat_visita).toFixed(6)}, ${Number(x.lng_visita).toFixed(6)}` : 'Pendiente'}</small><br/><small>{x.precision_gps ? `Precisión ${x.precision_gps} m` : ''}</small></td>
        <td>{x.asesor_nombre}</td>
        <td><button className="small" onClick={() => marcar(x.id)}>Marcar visitado</button></td>
      </tr>)}
    </tbody></table></div>
  </section>
}
