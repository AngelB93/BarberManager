
CREATE DATABASE BarberManagerDB;


USE BarberManagerDB;

select * from Usuario;


-- Guarda los datos del propietario

CREATE TABLE Usuario (
    IdUsuario INT IDENTITY PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Correo VARCHAR(100) NOT NULL UNIQUE,
    Contrasena VARCHAR(255) NOT NULL
);



-- Guarda los dias y horarios de la barberia

CREATE TABLE HorarioAtencion (
    IdHorario INT IDENTITY PRIMARY KEY,
    DiaSemana VARCHAR(15) NOT NULL UNIQUE,
    HoraApertura TIME NOT NULL,
    HoraCierre TIME NOT NULL,

    CHECK (HoraCierre > HoraApertura)
);



-- Guarda la informacion de los clientes

CREATE TABLE Cliente (
    IdCliente INT IDENTITY PRIMARY KEY,
    Nombre VARCHAR(50) NOT NULL,
    Apellido VARCHAR(50) NOT NULL,
    Telefono VARCHAR(15),
    Correo VARCHAR(100),
    FechaRegistro DATE DEFAULT GETDATE()
);



-- Define si la cita esta pendiente, completada o cancelada

CREATE TABLE EstadoCita (
    IdEstadoCita INT IDENTITY PRIMARY KEY,
    Nombre VARCHAR(30) NOT NULL UNIQUE
);



-- Clasifica los servicios de la barberia

CREATE TABLE CategoriaServicio (
    IdCategoriaServicio INT IDENTITY PRIMARY KEY,
    Nombre VARCHAR(50) NOT NULL UNIQUE,
    Descripcion VARCHAR(150)
);



-- Guarda los servicios y sus precios

CREATE TABLE Servicio (
    IdServicio INT IDENTITY PRIMARY KEY,
    IdCategoriaServicio INT NOT NULL,
    Nombre VARCHAR(80) NOT NULL,
    Precio DECIMAL(10,2) NOT NULL,
    Duracion INT NOT NULL,

    FOREIGN KEY (IdCategoriaServicio)
    REFERENCES CategoriaServicio(IdCategoriaServicio),

    CHECK (Precio > 0),
    CHECK (Duracion > 0)
);



-- Guarda las citas reservadas por los clientes

CREATE TABLE Cita (
    IdCita INT IDENTITY PRIMARY KEY,
    IdCliente INT NOT NULL,
    IdEstadoCita INT NOT NULL,
    Fecha DATE NOT NULL,
    HoraInicio TIME NOT NULL,
    HoraFin TIME NOT NULL,
    Observacion VARCHAR(200),

    FOREIGN KEY (IdCliente)
    REFERENCES Cliente(IdCliente),

    FOREIGN KEY (IdEstadoCita)
    REFERENCES EstadoCita(IdEstadoCita),

    CHECK (HoraFin > HoraInicio)
);



-- Relaciona cada cita con los servicios solicitados

CREATE TABLE DetalleCita (
    IdDetalleCita INT IDENTITY PRIMARY KEY,
    IdCita INT NOT NULL,
    IdServicio INT NOT NULL,
    Precio DECIMAL(10,2) NOT NULL,

    FOREIGN KEY (IdCita)
    REFERENCES Cita(IdCita),

    FOREIGN KEY (IdServicio)
    REFERENCES Servicio(IdServicio),

    CHECK (Precio > 0)
);



-- Clasifica los productos

CREATE TABLE CategoriaProducto (
    IdCategoriaProducto INT IDENTITY PRIMARY KEY,
    Nombre VARCHAR(50) NOT NULL UNIQUE,
    Descripcion VARCHAR(150)
);



-- Guarda las marcas de productos

CREATE TABLE Marca (
    IdMarca INT IDENTITY PRIMARY KEY,
    Nombre VARCHAR(60) NOT NULL UNIQUE
);



-- Guarda los productos de la barberia

CREATE TABLE Producto (
    IdProducto INT IDENTITY PRIMARY KEY,
    IdCategoriaProducto INT NOT NULL,
    IdMarca INT NOT NULL,
    Nombre VARCHAR(100) NOT NULL,
    Precio DECIMAL(10,2) NOT NULL,
    Existencia INT NOT NULL DEFAULT 0,

    FOREIGN KEY (IdCategoriaProducto)
    REFERENCES CategoriaProducto(IdCategoriaProducto),

    FOREIGN KEY (IdMarca)
    REFERENCES Marca(IdMarca),

    CHECK (Precio > 0),
    CHECK (Existencia >= 0)
);



-- Guarda informacion de los proveedores

CREATE TABLE Proveedor (
    IdProveedor INT IDENTITY PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL,
    Telefono VARCHAR(15),
    Correo VARCHAR(100),
    Direccion VARCHAR(150)
);



-- Registra compras realizadas a proveedores

CREATE TABLE Compra (
    IdCompra INT IDENTITY PRIMARY KEY,
    IdProveedor INT NOT NULL,
    IdUsuario INT NOT NULL,
    FechaCompra DATE DEFAULT GETDATE(),
    Total DECIMAL(10,2) NOT NULL,

    FOREIGN KEY (IdProveedor)
    REFERENCES Proveedor(IdProveedor),

    FOREIGN KEY (IdUsuario)
    REFERENCES Usuario(IdUsuario),

    CHECK (Total >= 0)
);



-- Guarda los productos y cantidades compradas

CREATE TABLE DetalleCompra (
    IdDetalleCompra INT IDENTITY PRIMARY KEY,
    IdCompra INT NOT NULL,
    IdProducto INT NOT NULL,
    Cantidad INT NOT NULL,
    PrecioCompra DECIMAL(10,2) NOT NULL,

    FOREIGN KEY (IdCompra)
    REFERENCES Compra(IdCompra),

    FOREIGN KEY (IdProducto)
    REFERENCES Producto(IdProducto),

    CHECK (Cantidad > 0),
    CHECK (PrecioCompra > 0)
);



-- Guarda los tipos de pago aceptados

CREATE TABLE MetodoPago (
    IdMetodoPago INT IDENTITY PRIMARY KEY,
    Nombre VARCHAR(50) NOT NULL UNIQUE
);



-- Guarda las ventas realizadas

CREATE TABLE Venta (
    IdVenta INT IDENTITY PRIMARY KEY,
    IdCliente INT NULL,
    IdUsuario INT NOT NULL,
    IdCita INT NULL,
    FechaVenta DATE DEFAULT GETDATE(),
    Total DECIMAL(10,2) NOT NULL,

    FOREIGN KEY (IdCliente)
    REFERENCES Cliente(IdCliente),

    FOREIGN KEY (IdUsuario)
    REFERENCES Usuario(IdUsuario),

    FOREIGN KEY (IdCita)
    REFERENCES Cita(IdCita),

    CHECK (Total >= 0)
);



-- Registra los productos vendidos

CREATE TABLE DetalleVentaProducto (
    IdDetalleVentaProducto INT IDENTITY PRIMARY KEY,
    IdVenta INT NOT NULL,
    IdProducto INT NOT NULL,
    Cantidad INT NOT NULL,
    PrecioUnitario DECIMAL(10,2) NOT NULL,

    FOREIGN KEY (IdVenta)
    REFERENCES Venta(IdVenta),

    FOREIGN KEY (IdProducto)
    REFERENCES Producto(IdProducto),

    CHECK (Cantidad > 0),
    CHECK (PrecioUnitario > 0)
);



-- Registra los servicios cobrados

CREATE TABLE DetalleVentaServicio (
    IdDetalleVentaServicio INT IDENTITY PRIMARY KEY,
    IdVenta INT NOT NULL,
    IdServicio INT NOT NULL,
    Precio DECIMAL(10,2) NOT NULL,

    FOREIGN KEY (IdVenta)
    REFERENCES Venta(IdVenta),

    FOREIGN KEY (IdServicio)
    REFERENCES Servicio(IdServicio),

    CHECK (Precio > 0)
);



-- Guarda los pagos realizados por los clientes

CREATE TABLE Pago (
    IdPago INT IDENTITY PRIMARY KEY,
    IdVenta INT NOT NULL,
    IdMetodoPago INT NOT NULL,
    FechaPago DATE DEFAULT GETDATE(),
    Monto DECIMAL(10,2) NOT NULL,

    FOREIGN KEY (IdVenta)
    REFERENCES Venta(IdVenta),

    FOREIGN KEY (IdMetodoPago)
    REFERENCES MetodoPago(IdMetodoPago),

    CHECK (Monto > 0)
);



-- Registra entradas y salidas de productos

CREATE TABLE MovimientoInventario (
    IdMovimiento INT IDENTITY PRIMARY KEY,
    IdProducto INT NOT NULL,
    IdCompra INT NULL,
    IdVenta INT NULL,
    TipoMovimiento VARCHAR(10) NOT NULL,
    Cantidad INT NOT NULL,
    FechaMovimiento DATE DEFAULT GETDATE(),

    FOREIGN KEY (IdProducto)
    REFERENCES Producto(IdProducto),

    FOREIGN KEY (IdCompra)
    REFERENCES Compra(IdCompra),

    FOREIGN KEY (IdVenta)
    REFERENCES Venta(IdVenta),

    CHECK (TipoMovimiento IN ('Entrada', 'Salida')),
    CHECK (Cantidad > 0)
);


USE BarberManagerDB;


-- 1. USUARIO
INSERT INTO Usuario (Nombre, Correo, Contrasena)
VALUES ('Carlos Lopez', 'carlos@gmail.com', 'demo123');

-- 2. HORARIO DE ATENCION
INSERT INTO HorarioAtencion
(DiaSemana, HoraApertura, HoraCierre)
VALUES
('Lunes', '08:00', '18:00'),
('Martes', '08:00', '18:00'),
('Miercoles', '08:00', '18:00'),
('Jueves', '08:00', '18:00'),
('Viernes', '08:00', '18:00'),
('Sabado', '08:00', '16:00');



-- 3. CLIENTE
INSERT INTO Cliente (Nombre, Apellido, Telefono, Correo)
VALUES
('Juan', 'Perez', '55551234', 'juan@gmail.com'),
('Pedro', 'Ramirez', '55552345', 'pedro@gmail.com'),
('Luis', 'Garcia', '55553456', 'luis@gmail.com'),
('Mario', 'Lopez', '55554567', 'mario@gmail.com'),
('Jose', 'Morales', '55555678', 'jose@gmail.com');

-- 4. ESTADO DE CITA
INSERT INTO EstadoCita (Nombre)
VALUES
('Pendiente'),
('Completada'),
('Cancelada');

-- 5. CATEGORIA DE SERVICIO
INSERT INTO CategoriaServicio (Nombre, Descripcion)
VALUES
('Cabello', 'Servicios de corte de cabello'),
('Barba', 'Servicios para el cuidado de barba'),
('Facial', 'Servicios de cuidado facial');

-- 6. SERVICIO
INSERT INTO Servicio
(IdCategoriaServicio, Nombre, Precio, Duracion)
VALUES
(1, 'Corte clasico', 35.00, 30),
(1, 'Corte degradado', 45.00, 45),
(2, 'Arreglo de barba', 25.00, 20),
(2, 'Afeitado completo', 30.00, 30),
(3, 'Perfilado de cejas', 15.00, 15);




-- 7. CITA
INSERT INTO Cita
(IdCliente, IdEstadoCita, Fecha, HoraInicio, HoraFin, Observacion)
VALUES
(1, 2, '2026-10-20', '08:00', '08:30', 'Corte normal'),
(2, 2, '2026-10-20', '09:00', '09:45', 'Corte degradado'),
(3, 2, '2026-10-21', '10:00', '10:30', 'Arreglo de barba'),
(4, 1, '2026-10-28', '11:00', '11:45', 'Corte degradado'),
(5, 3, '2026-10-22', '14:00', '14:30', 'Cliente cancelo');

-- 8. DETALLE DE CITA
INSERT INTO DetalleCita (IdCita, IdServicio, Precio)
VALUES
(1, 1, 35.00),
(2, 2, 45.00),
(3, 3, 25.00),
(4, 2, 45.00),
(5, 1, 35.00);

-- 9. CATEGORIA DE PRODUCTO
INSERT INTO CategoriaProducto (Nombre, Descripcion)
VALUES
('Cabello', 'Productos para el cabello'),
('Barba', 'Productos para el cuidado de barba'),
('Higiene', 'Productos de limpieza personal');

-- 10. MARCA
INSERT INTO Marca (Nombre)
VALUES
('Gatsby'),
('Gillette'),
('Old Spice');

-- 11. PRODUCTO
INSERT INTO Producto
(IdCategoriaProducto, IdMarca, Nombre, Precio, Existencia)
VALUES
(1, 1, 'Cera para cabello', 45.00, 20),
(1, 1, 'Gel fijador', 30.00, 15),
(2, 2, 'Espuma de afeitar', 40.00, 12),
(2, 2, 'Crema para barba', 35.00, 10),
(3, 3, 'Shampoo', 50.00, 18);

-- 12. PROVEEDOR
INSERT INTO Proveedor
(Nombre, Telefono, Correo, Direccion)
VALUES
('Distribuidora Central', '55556677',
'central@gmail.com', 'Guatemala'),
('Productos Profesionales', '55557788',
'productos@gmail.com', 'Quetzaltenango'),
('Distribuidora del Sur', '55558899',
'distribuidora@gmail.com', 'Escuintla');


-- 13. COMPRA
INSERT INTO Compra
(IdProveedor, IdUsuario, FechaCompra, Total)
VALUES
(1, 1, '2026-10-15', 600.00),
(2, 1, '2026-10-16', 360.00),
(3, 1, '2026-10-17', 450.00);

-- 14. DETALLE DE COMPRA
INSERT INTO DetalleCompra
(IdCompra, IdProducto, Cantidad, PrecioCompra)
VALUES
(1, 1, 20, 20.00),
(1, 2, 10, 20.00),
(2, 3, 12, 20.00),
(2, 4, 6, 20.00),
(3, 5, 18, 25.00);

-- 15. METODO DE PAGO
INSERT INTO MetodoPago (Nombre)
VALUES
('Efectivo'),
('Transferencia'),
('Tarjeta');

-- 16. VENTA
INSERT INTO Venta
(IdCliente, IdUsuario, IdCita, FechaVenta, Total)
VALUES
(1, 1, 1, '2026-10-20', 80.00),
(2, 1, 2, '2026-10-20', 45.00),
(3, 1, 3, '2026-10-21', 25.00),
(4, 1, NULL, '2026-10-22', 30.00),
(5, 1, NULL, '2026-10-23', 50.00);

-- 17. DETALLE DE VENTA PRODUCTO
INSERT INTO DetalleVentaProducto
(IdVenta, IdProducto, Cantidad, PrecioUnitario)
VALUES
(1, 1, 1, 45.00),
(4, 2, 1, 30.00),
(5, 5, 1, 50.00);

-- 18. DETALLE DE VENTA SERVICIO
INSERT INTO DetalleVentaServicio
(IdVenta, IdServicio, Precio)
VALUES
(1, 1, 35.00),
(2, 2, 45.00),
(3, 3, 25.00);


-- 19. PAGO
INSERT INTO Pago
(IdVenta, IdMetodoPago, FechaPago, Monto)
VALUES
(1, 1, '2026-10-20', 80.00),
(2, 1, '2026-10-20', 45.00),
(3, 2, '2026-10-21', 25.00),
(4, 1, '2026-10-22', 30.00),
(5, 2, '2026-10-23', 50.00);

-- 20. MOVIMIENTO DE INVENTARIO
INSERT INTO MovimientoInventario
(IdProducto, IdCompra, IdVenta, TipoMovimiento, Cantidad)
VALUES
(1, 1, NULL, 'Entrada', 20),
(2, 1, NULL, 'Entrada', 10),
(3, 2, NULL, 'Entrada', 12),
(4, 2, NULL, 'Entrada', 6),
(5, 3, NULL, 'Entrada', 18),
(1, NULL, 1, 'Salida', 1),
(2, NULL, 4, 'Salida', 1),
(5, NULL, 5, 'Salida', 1);

SELECT * FROM Usuario;
SELECT * FROM HorarioAtencion;
SELECT * FROM Cliente;
SELECT * FROM EstadoCita;
SELECT * FROM CategoriaServicio;
SELECT * FROM Servicio;
SELECT * FROM Cita;
SELECT * FROM DetalleCita;
SELECT * FROM CategoriaProducto;
SELECT * FROM Marca;
SELECT * FROM Producto;
SELECT * FROM Proveedor;
SELECT * FROM Compra;
SELECT * FROM DetalleCompra;
SELECT * FROM MetodoPago;
SELECT * FROM Venta;
SELECT * FROM DetalleVentaProducto;
SELECT * FROM DetalleVentaServicio;
SELECT * FROM Pago;
SELECT * FROM MovimientoInventario;