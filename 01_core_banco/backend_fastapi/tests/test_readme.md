# Pruebas manuales rápidas

```bash
curl http://localhost:8003/health

curl -X POST http://localhost:8003/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

curl -X POST http://localhost:8003/cliente/login \
  -H "Content-Type: application/json" \
  -d '{"numero_documento":"12345678","password":"1234"}'
```
