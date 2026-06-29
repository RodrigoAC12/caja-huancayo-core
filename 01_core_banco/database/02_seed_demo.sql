-- ============================================================
-- Seed demo Caja Huancayo Core
-- Contraseñas:
-- admin/admin123, 0001/1234, 0002/1234, 12345678/1234
-- Hash: pbkdf2_sha256 propio del backend
-- ============================================================

INSERT INTO roles (id, nombre, descripcion) VALUES
('00000000-0000-0000-0000-000000000001','admin','Administrador del core'),
('00000000-0000-0000-0000-000000000002','supervisor','Supervisor de fuerza de ventas'),
('00000000-0000-0000-0000-000000000003','asesor','Asesor de créditos'),
('00000000-0000-0000-0000-000000000004','analista','Analista de créditos'),
('00000000-0000-0000-0000-000000000005','cliente','Cliente de banca móvil');

INSERT INTO usuarios (id, rol_id, username, password_hash, tipo_usuario) VALUES
('10000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000000001','admin','pbkdf2_sha256$260000$cmac_admin_2026$ywiesjxmL5ILpYorreTLO/Lk23I8X3EmEURlUHsG5Xo=','personal'),
('10000000-0000-0000-0000-000000000002','00000000-0000-0000-0000-000000000002','0002','pbkdf2_sha256$260000$cmac_demo_1234$l42U0QaLYpMFwzpH+83n4AF1LFF7G49nNp/oLQmyX8A=','personal'),
('10000000-0000-0000-0000-000000000003','00000000-0000-0000-0000-000000000003','0001','pbkdf2_sha256$260000$cmac_demo_1234$l42U0QaLYpMFwzpH+83n4AF1LFF7G49nNp/oLQmyX8A=','personal'),
('10000000-0000-0000-0000-000000000004','00000000-0000-0000-0000-000000000005','12345678','pbkdf2_sha256$260000$cmac_demo_1234$l42U0QaLYpMFwzpH+83n4AF1LFF7G49nNp/oLQmyX8A=','cliente'),
('10000000-0000-0000-0000-000000000005','00000000-0000-0000-0000-000000000005','44455667','pbkdf2_sha256$260000$cmac_demo_1234$l42U0QaLYpMFwzpH+83n4AF1LFF7G49nNp/oLQmyX8A=','cliente');

INSERT INTO agencias (id, codigo, nombre, region, direccion, lat, lng) VALUES
('20000000-0000-0000-0000-000000000001','AG-HYO-001','Agencia Huancayo Centro','Junín','Calle Real 000, Huancayo',-12.0686000,-75.2103000),
('20000000-0000-0000-0000-000000000002','AG-TAM-001','Agencia Tambo','Junín','Av. Mariscal Castilla 000, El Tambo',-12.0505000,-75.2189000);

INSERT INTO asesores (id, usuario_id, agencia_id, codigo_empleado, nombres, apellidos, telefono, zona_asignada, perfil) VALUES
('30000000-0000-0000-0000-000000000001','10000000-0000-0000-0000-000000000003','20000000-0000-0000-0000-000000000001','0001','Carlos','Ramírez Soto','964000001','Huancayo Centro','asesor'),
('30000000-0000-0000-0000-000000000002','10000000-0000-0000-0000-000000000002','20000000-0000-0000-0000-000000000001','0002','María','Quispe Flores','964000002','Huancayo Norte','supervisor');

INSERT INTO clientes (id, usuario_id, numero_documento, nombres, apellidos, fecha_nacimiento, telefono, email, direccion, referencia_direccion, departamento, provincia, distrito, latitud_domicilio, longitud_domicilio, estado_civil) VALUES
('40000000-0000-0000-0000-000000000001','10000000-0000-0000-0000-000000000004','12345678','Rodrigo','Arce Curi','2002-05-12','964111222','rodrigo.demo@mail.com','Av. Ferrocarril 123','A una cuadra del mercado Modelo','Junín','Huancayo','Huancayo',-12.0700200,-75.2108900,'soltero'),
('40000000-0000-0000-0000-000000000002','10000000-0000-0000-0000-000000000005','44455667','María','Quispe Huamán','1988-03-10','964222333','maria.demo@mail.com','Jr. Arequipa 456','Casa color crema, segundo piso','Junín','Huancayo','El Tambo',-12.0514200,-75.2192400,'casada'),
('40000000-0000-0000-0000-000000000003',NULL,'41112233','José','Mamani Flores','1980-08-15','964333444','jose.demo@mail.com','Av. Giráldez 789','Frente a galería comercial','Junín','Huancayo','Huancayo',-12.0677100,-75.2097200,'casado'),
('40000000-0000-0000-0000-000000000004',NULL,'42778899','Rosa','Condori Apaza','1992-01-21','964444555','rosa.demo@mail.com','Jr. Ica 234','Al costado de farmacia','Junín','Huancayo','Chilca',-12.0732600,-75.2052100,'soltera'),
('40000000-0000-0000-0000-000000000005',NULL,'43223344','Pedro','Ccahua Ramos','1975-11-02','964555666','pedro.demo@mail.com','Av. Huancavelica 345','Portón azul, taller mecánico','Junín','Huancayo','El Tambo',-12.0452600,-75.2153600,'casado');

INSERT INTO cliente_negocios (cliente_id, nombre_negocio, tipo_negocio, actividad_economica, antiguedad_meses, direccion_negocio, referencia_negocio, departamento, provincia, distrito, lat, lng, ingresos_estimados, gastos_estimados) VALUES
('40000000-0000-0000-0000-000000000001','Bodega Rodrigo','Comercio minorista','Bodega',24,'Av. Ferrocarril 123','A una cuadra del mercado Modelo','Junín','Huancayo','Huancayo',-12.0701000,-75.2110000,4200,2600),
('40000000-0000-0000-0000-000000000002','Textiles María','Comercio textil','Textiles',60,'Jr. Arequipa 456','Galería textil, stand 12','Junín','Huancayo','El Tambo',-12.0510000,-75.2191000,8500,5100),
('40000000-0000-0000-0000-000000000003','Ferretería Mamani','Ferretería','Comercio',72,'Av. Giráldez 789','Frente a galería comercial','Junín','Huancayo','Huancayo',-12.0679000,-75.2095000,12000,7800),
('40000000-0000-0000-0000-000000000004','Juguería Rosa','Alimentos','Restaurante',18,'Jr. Ica 234','Al costado de farmacia','Junín','Huancayo','Chilca',-12.0730000,-75.2050000,3800,2300),
('40000000-0000-0000-0000-000000000005','Taller Pedro','Servicios','Mecánica',96,'Av. Huancavelica 345','Portón azul, taller mecánico','Junín','Huancayo','El Tambo',-12.0450000,-75.2150000,6500,4200);

INSERT INTO cuentas_ahorro (id, cliente_id, numero_cuenta, tipo_cuenta, moneda, saldo_disponible, saldo_contable, tea, estado) VALUES
('50000000-0000-0000-0000-000000000001','40000000-0000-0000-0000-000000000001','001-110-000123456','Ahorro Simple','PEN',1850.50,1850.50,1.20,'activa'),
('50000000-0000-0000-0000-000000000002','40000000-0000-0000-0000-000000000001','001-110-000123457','Ahorro Emprendedor','PEN',5200.00,5200.00,1.80,'activa'),
('50000000-0000-0000-0000-000000000003','40000000-0000-0000-0000-000000000002','001-110-000444556','Ahorro Simple','PEN',3200.80,3200.80,1.20,'activa');

INSERT INTO movimientos_cuenta (cuenta_id, cliente_id, tipo_movimiento, concepto, canal, monto, saldo_resultante, fecha_operacion) VALUES
('50000000-0000-0000-0000-000000000001','40000000-0000-0000-0000-000000000001','DEPOSITO','Depósito en agencia','AGENCIA',1000,1850.50,now() - interval '3 days'),
('50000000-0000-0000-0000-000000000001','40000000-0000-0000-0000-000000000001','TRANSFERENCIA','Transferencia recibida','APP',250,850.50,now() - interval '2 days'),
('50000000-0000-0000-0000-000000000002','40000000-0000-0000-0000-000000000001','PAGO_CREDITO','Pago de cuota','APP',-350,5200.00,now() - interval '1 day');

INSERT INTO creditos (id, cliente_id, numero_credito, producto, monto_desembolsado, monto_aprobado, saldo_capital, saldo_total, tea, plazo_meses, cuotas_total, cuotas_pagadas, dias_mora, estado, fecha_desembolso) VALUES
('60000000-0000-0000-0000-000000000001','40000000-0000-0000-0000-000000000001','CR-2026-0001','Crédito Pyme',8000,8000,5400,6100,42.00,18,18,6,0,'vigente','2026-01-15'),
('60000000-0000-0000-0000-000000000002','40000000-0000-0000-0000-000000000002','CR-2026-0002','Crédito Capital de Trabajo',15000,15000,12500,13700,38.50,24,24,4,12,'vigente','2026-02-10');

INSERT INTO cronograma_credito (credito_id, nro_cuota, fecha_vencimiento, monto_cuota, monto_capital, monto_interes, saldo, estado_cuota, fecha_pago) VALUES
('60000000-0000-0000-0000-000000000001',1,'2026-02-15',520,380,140,7620,'pagada','2026-02-15'),
('60000000-0000-0000-0000-000000000001',2,'2026-03-15',520,390,130,7230,'pagada','2026-03-15'),
('60000000-0000-0000-0000-000000000001',3,'2026-04-15',520,400,120,6830,'pagada','2026-04-15'),
('60000000-0000-0000-0000-000000000001',7,'2026-08-15',520,430,90,5400,'pendiente',NULL),
('60000000-0000-0000-0000-000000000001',8,'2026-09-15',520,440,80,4960,'pendiente',NULL);

INSERT INTO tarjetas (cliente_id, numero_enmascarado, marca, tipo_tarjeta, linea_credito, saldo_utilizado, fecha_corte, fecha_pago, compras_internet, estado) VALUES
('40000000-0000-0000-0000-000000000001','**** **** **** 4589','VISA','debito',0,0,NULL,NULL,TRUE,'activa'),
('40000000-0000-0000-0000-000000000001','**** **** **** 9021','VISA','credito',5000,1250,'2026-07-10','2026-07-25',TRUE,'activa');

INSERT INTO cartera_diaria (id, asesor_id, cliente_id, fecha_asignacion, tipo_gestion, prioridad, score_prioridad, monto_referencial, estado_visita, orden_manual) VALUES
('70000000-0000-0000-0000-000000000001','30000000-0000-0000-0000-000000000001','40000000-0000-0000-0000-000000000002',current_date,'RECUPERACION_MORA','alta',88,8500,'pendiente',1),
('70000000-0000-0000-0000-000000000002','30000000-0000-0000-0000-000000000001','40000000-0000-0000-0000-000000000003',current_date,'RENOVACION','alta',72,12000,'pendiente',2),
('70000000-0000-0000-0000-000000000003','30000000-0000-0000-0000-000000000001','40000000-0000-0000-0000-000000000004',current_date,'NUEVA_SOLICITUD','media',55,5000,'pendiente',3),
('70000000-0000-0000-0000-000000000004','30000000-0000-0000-0000-000000000001','40000000-0000-0000-0000-000000000005',current_date,'SEGUIMIENTO','normal',30,3000,'pendiente',4);

INSERT INTO solicitudes_credito (id, cliente_id, asesor_id, agencia_id, canal, numero_expediente, monto_solicitado, monto_aprobado, plazo_meses, destino_credito, cuota_estimada, tea_referencial, estado) VALUES
('80000000-0000-0000-0000-000000000001','40000000-0000-0000-0000-000000000001','30000000-0000-0000-0000-000000000001','20000000-0000-0000-0000-000000000001','cliente','EXP-CLI-0001',5000,NULL,12,'Capital de trabajo',510,42.00,'en_evaluacion'),
('80000000-0000-0000-0000-000000000002','40000000-0000-0000-0000-000000000002','30000000-0000-0000-0000-000000000001','20000000-0000-0000-0000-000000000001','asesor','EXP-ASE-0002',8500,8500,18,'Compra de mercadería',620,38.50,'aprobado');

INSERT INTO solicitud_estado_historial (solicitud_id, estado_anterior, estado_nuevo, usuario_id, comentario) VALUES
('80000000-0000-0000-0000-000000000001',NULL,'enviado','10000000-0000-0000-0000-000000000004','Solicitud creada desde app cliente'),
('80000000-0000-0000-0000-000000000001','enviado','en_evaluacion','10000000-0000-0000-0000-000000000002','Derivada a evaluación'),
('80000000-0000-0000-0000-000000000002','en_evaluacion','aprobado','10000000-0000-0000-0000-000000000002','Aprobación demo');

INSERT INTO notificaciones (usuario_id, cliente_id, titulo, mensaje, tipo, canal) VALUES
('10000000-0000-0000-0000-000000000004','40000000-0000-0000-0000-000000000001','Solicitud recibida','Tu solicitud EXP-CLI-0001 fue recibida y está en evaluación.','solicitud','APP'),
('10000000-0000-0000-0000-000000000005','40000000-0000-0000-0000-000000000002','Crédito aprobado','Tu crédito fue aprobado por S/ 8,500.','credito','APP');

INSERT INTO auditoria (usuario_id, accion, modulo, entidad, entidad_id, descripcion) VALUES
('10000000-0000-0000-0000-000000000001','SEED','sistema',NULL,NULL,'Datos demo cargados correctamente');
