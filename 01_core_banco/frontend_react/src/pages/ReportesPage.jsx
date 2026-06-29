import React from "react";
import { useEffect, useState } from 'react'
import api from '../services/api.js'

export default function ReportesPage() {
  const [items, setItems] = useState([])
  useEffect(() => { api.get('/reportes/productividad').then(r => setItems(r.data)) }, [])
  return <section>
    <div className="page-head"><h1>Reportes</h1><p>Productividad comercial, visitas y control GPS por asesor.</p></div>
    <div className="panel"><table><thead><tr><th>Asesor</th><th>Enviadas</th><th>Aprobadas</th><th>Monto total</th><th>Tasa aprobación</th><th>Visitas</th><th>Con GPS</th><th>Dist. prom.</th></tr></thead><tbody>
      {items.map((x, i) => <tr key={i}>
        <td>{x.asesor_nombre}</td>
        <td>{x.enviadas}</td>
        <td>{x.aprobadas}</td>
        <td>S/ {Number(x.monto_total).toLocaleString('es-PE')}</td>
        <td>{x.tasa_aprobacion}%</td>
        <td>{x.visitas_registradas || 0}</td>
        <td>{x.visitas_con_gps || 0}</td>
        <td>{x.distancia_promedio_metros ? `${x.distancia_promedio_metros} m` : '-'}</td>
      </tr>)}
    </tbody></table></div>
  </section>
}

