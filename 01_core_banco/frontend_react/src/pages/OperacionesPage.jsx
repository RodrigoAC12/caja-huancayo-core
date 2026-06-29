import React from "react";
import { useEffect, useState } from 'react'
import api from '../services/api.js'

export default function OperacionesPage() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = async () => {
    try {
      setError('')
      const r = await api.get('/operaciones')
      setItems(Array.isArray(r.data) ? r.data : [])
    } catch (e) {
      setError('No se pudieron cargar las operaciones. Verifica que el Core esté activo.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    const timer = setInterval(load, 5000)
    return () => clearInterval(timer)
  }, [])

  return <section>
    <div className="page-head">
      <div>
        <h1>Operaciones</h1>
        <p>Operaciones generadas desde canales digitales.</p>
      </div>
      <button className="btn-secondary" onClick={load}>Actualizar</button>
    </div>

    <div className="panel">
      {loading && <p className="muted">Cargando operaciones...</p>}
      {error && <p className="error-text">{error}</p>}
      {!loading && !error && items.length === 0 && (
        <div className="empty-box">
          <strong>No hay operaciones registradas todavía.</strong>
          <span>Cuando un cliente realice un pago, transferencia o pago QR desde la app móvil, aparecerá aquí.</span>
        </div>
      )}
      {items.length > 0 && <table>
        <thead>
          <tr>
            <th>Código</th>
            <th>Cliente</th>
            <th>Tipo</th>
            <th>Monto</th>
            <th>Estado</th>
            <th>Fecha</th>
          </tr>
        </thead>
        <tbody>
          {items.map(x => <tr key={x.id}>
            <td>{x.codigo_operacion}</td>
            <td>{x.cliente_nombre}</td>
            <td>{String(x.tipo_operacion || '').replaceAll('_', ' ')}</td>
            <td>S/ {Number(x.monto || 0).toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
            <td><span className="badge">{x.estado}</span></td>
            <td>{x.created_at ? new Date(x.created_at).toLocaleString('es-PE') : '-'}</td>
          </tr>)}
        </tbody>
      </table>}
    </div>
  </section>
}

