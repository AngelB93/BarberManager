from fastapi import FastAPI, HTTPException
from conexion import conectar

app = FastAPI(title="BarberManager API")


@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido a BarberManager"}


@app.get("/clientes")
def obtener_clientes():
    conexion = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT IdCliente, Nombre, Apellido, Telefono, Correo
            FROM Cliente
        """)

        clientes = []

        for fila in cursor.fetchall():
            clientes.append({
                "IdCliente": fila[0],
                "Nombre": fila[1],
                "Apellido": fila[2],
                "Telefono": fila[3],
                "Correo": fila[4]
            })

        return clientes

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al consultar los clientes"
        )

    finally:
        if conexion is not None:
            conexion.close()




from pydantic import BaseModel

class ClienteNuevo(BaseModel):
    Nombre: str
    Apellido: str
    Telefono: str
    Correo: str

@app.get("/clientes/{id}")
def buscar_cliente(id: int):
    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT IdCliente, Nombre, Apellido, Telefono, Correo
            FROM Cliente
            WHERE IdCliente = %s
        """, (id,))

        fila = cursor.fetchone()

        if fila is None:
            raise HTTPException(
                status_code=404,
                detail="Cliente no encontrado"
            )

        return {
            "IdCliente": fila[0],
            "Nombre": fila[1],
            "Apellido": fila[2],
            "Telefono": fila[3],
            "Correo": fila[4]
        }

    finally:
        conexion.close()            

@app.post("/clientes")
def crear_cliente(cliente: ClienteNuevo):
    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO Cliente
            (Nombre, Apellido, Telefono, Correo)
            VALUES (%s, %s, %s, %s)
        """, (
            cliente.Nombre,
            cliente.Apellido,
            cliente.Telefono,
            cliente.Correo
        ))

        conexion.commit()

        return {"mensaje": "Cliente registrado correctamente"}

    except Exception:
        conexion.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error al registrar cliente"
        )

    finally:
        conexion.close()
        
@app.put("/clientes/{id}")
def actualizar_cliente(id: int, cliente: ClienteNuevo):
    conexion = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE Cliente
            SET Nombre = %s,
                Apellido = %s,
                Telefono = %s,
                Correo = %s
            WHERE IdCliente = %s
        """, (
            cliente.Nombre,
            cliente.Apellido,
            cliente.Telefono,
            cliente.Correo,
            id
        ))

        if cursor.rowcount == 0:
            conexion.rollback()
            raise HTTPException(
                status_code=404,
                detail="Cliente no encontrado"
            )

        conexion.commit()

        return {"mensaje": "Cliente actualizado correctamente"}

    except HTTPException:
        raise

    except Exception:
        if conexion is not None:
            conexion.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error al actualizar cliente"
        )

    finally:
        if conexion is not None:
            conexion.close()    
@app.delete("/clientes/{id}")
def eliminar_cliente(id: int):
    conexion = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        # Verificar que el cliente exista
        cursor.execute(
            "SELECT IdCliente FROM Cliente WHERE IdCliente = %s",
            (id,)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Cliente no encontrado"
            )

        # Verificar que no tenga citas o ventas
        cursor.execute(
            "SELECT IdCliente FROM Cita WHERE IdCliente = %s",
            (id,)
        )
        tiene_citas = cursor.fetchone() is not None

        cursor.execute(
            "SELECT IdCliente FROM Venta WHERE IdCliente = %s",
            (id,)
        )
        tiene_ventas = cursor.fetchone() is not None

        if tiene_citas or tiene_ventas:
            raise HTTPException(
                status_code=409,
                detail="No se puede eliminar porque tiene citas o ventas"
            )

        # Eliminar el cliente
        cursor.execute(
            "DELETE FROM Cliente WHERE IdCliente = %s",
            (id,)
        )

        conexion.commit()

        return {"mensaje": "Cliente eliminado correctamente"}

    except HTTPException:
        raise

    except Exception:
        if conexion is not None:
            conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail="Error al eliminar cliente"
        )

    finally:
        if conexion is not None:
            conexion.close()        

# CONSULTAR TODOS LOS SERVICIOS

@app.get("/servicios")
def obtener_servicios():
    conexion = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT IdServicio, IdCategoriaServicio,
                   Nombre, Precio, Duracion
            FROM Servicio
        """)

        servicios = []

        for fila in cursor.fetchall():
            servicios.append({
                "IdServicio": fila[0],
                "IdCategoriaServicio": fila[1],
                "Nombre": fila[2],
                "Precio": float(fila[3]),
                "Duracion": fila[4]
            })

        return servicios

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al consultar servicios"
        )

    finally:
        if conexion is not None:
            conexion.close()

from pydantic import BaseModel

class ServicioNuevo(BaseModel):
    IdCategoriaServicio: int
    Nombre: str
    Precio: float
    Duracion: int


@app.post("/servicios")
def crear_servicio(servicio: ServicioNuevo):

    if servicio.Precio <= 0 or servicio.Duracion <= 0:
        raise HTTPException(
            status_code=400,
            detail="El precio y la duracion deben ser mayores a cero"
        )

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO Servicio
            (IdCategoriaServicio, Nombre, Precio, Duracion)
            VALUES (%s, %s, %s, %s)
        """, (
            servicio.IdCategoriaServicio,
            servicio.Nombre,
            servicio.Precio,
            servicio.Duracion
        ))

        conexion.commit()

        return {"mensaje": "Servicio registrado correctamente"}

    except Exception:
        conexion.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error al registrar servicio"
        )

    finally:
        conexion.close()

@app.get("/servicios/{id}")
def buscar_servicio(id: int):
    conexion = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT IdServicio, IdCategoriaServicio,
                   Nombre, Precio, Duracion
            FROM Servicio
            WHERE IdServicio = %s
        """, (id,))

        fila = cursor.fetchone()

        if fila is None:
            raise HTTPException(
                status_code=404,
                detail="Servicio no encontrado"
            )

        return {
            "IdServicio": fila[0],
            "IdCategoriaServicio": fila[1],
            "Nombre": fila[2],
            "Precio": float(fila[3]),
            "Duracion": fila[4]
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al consultar servicio"
        )

    finally:
        if conexion is not None:
            conexion.close()

@app.put("/servicios/{id}")
def actualizar_servicio(id: int, servicio: ServicioNuevo):
    conexion = None

    if servicio.Precio <= 0 or servicio.Duracion <= 0:
        raise HTTPException(
            status_code=400,
            detail="Precio y duracion deben ser mayores a cero"
        )

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE Servicio
            SET IdCategoriaServicio = %s,
                Nombre = %s,
                Precio = %s,
                Duracion = %s
            WHERE IdServicio = %s
        """, (
            servicio.IdCategoriaServicio,
            servicio.Nombre,
            servicio.Precio,
            servicio.Duracion,
            id
        ))

        if cursor.rowcount == 0:
            conexion.rollback()
            raise HTTPException(
                status_code=404,
                detail="Servicio no encontrado"
            )

        conexion.commit()

        return {"mensaje": "Servicio actualizado correctamente"}

    except HTTPException:
        raise

    except Exception:
        if conexion is not None:
            conexion.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error al actualizar servicio"
        )

    finally:
        if conexion is not None:
            conexion.close()

@app.delete("/servicios/{id}")
def eliminar_servicio(id: int):
    conexion = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT IdServicio FROM Servicio WHERE IdServicio = %s",
            (id,)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Servicio no encontrado"
            )

        cursor.execute("""
            SELECT IdServicio
            FROM DetalleCita
            WHERE IdServicio = %s
        """, (id,))

        tiene_citas = cursor.fetchone() is not None

        cursor.execute("""
            SELECT IdServicio
            FROM DetalleVentaServicio
            WHERE IdServicio = %s
        """, (id,))

        tiene_ventas = cursor.fetchone() is not None

        if tiene_citas or tiene_ventas:
            raise HTTPException(
                status_code=409,
                detail="No se puede eliminar porque tiene citas o ventas"
            )

        cursor.execute(
            "DELETE FROM Servicio WHERE IdServicio = %s",
            (id,)
        )

        conexion.commit()

        return {"mensaje": "Servicio eliminado correctamente"}

    except HTTPException:
        raise

    except Exception:
        if conexion is not None:
            conexion.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error al eliminar servicio"
        )

    finally:
        if conexion is not None:
            conexion.close()


# CONSULTAR TODOS LOS PRODUCTOS

@app.get("/productos")
def obtener_productos():
    conexion = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT IdProducto, IdCategoriaProducto,
                   IdMarca, Nombre, Precio, Existencia
            FROM Producto
        """)

        productos = []

        for fila in cursor.fetchall():
            productos.append({
                "IdProducto": fila[0],
                "IdCategoriaProducto": fila[1],
                "IdMarca": fila[2],
                "Nombre": fila[3],
                "Precio": float(fila[4]),
                "Existencia": fila[5]
            })

        return productos

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al consultar productos"
        )

    finally:
        if conexion is not None:
            conexion.close()


# REGISTRAR PRODUCTOS

class ProductoNuevo(BaseModel):
    IdCategoriaProducto: int
    IdMarca: int
    Nombre: str
    Precio: float
    Existencia: int


@app.post("/productos")
def crear_producto(producto: ProductoNuevo):

    if producto.Precio <= 0 or producto.Existencia < 0:
        raise HTTPException(
            status_code=400,
            detail="Precio o existencia incorrecta"
        )

    conexion = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO Producto
            (IdCategoriaProducto, IdMarca, Nombre, Precio, Existencia)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            producto.IdCategoriaProducto,
            producto.IdMarca,
            producto.Nombre,
            producto.Precio,
            producto.Existencia
        ))

        conexion.commit()

        return {"mensaje": "Producto registrado correctamente"}

    except Exception:
        if conexion is not None:
            conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail="Error al registrar producto"
        )

    finally:
        if conexion is not None:
            conexion.close()


# CONSULTAR PRODUCTO POR ID

@app.get("/productos/{id}")
def buscar_producto(id: int):
    conexion = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT IdProducto, IdCategoriaProducto,
                   IdMarca, Nombre, Precio, Existencia
            FROM Producto
            WHERE IdProducto = %s
        """, (id,))

        fila = cursor.fetchone()

        if fila is None:
            raise HTTPException(
                status_code=404,
                detail="Producto no encontrado"
            )

        return {
            "IdProducto": fila[0],
            "IdCategoriaProducto": fila[1],
            "IdMarca": fila[2],
            "Nombre": fila[3],
            "Precio": float(fila[4]),
            "Existencia": fila[5]
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al consultar producto"
        )

    finally:
        if conexion is not None:
            conexion.close()


# ACTUALIZAR PRODUCTO

@app.put("/productos/{id}")
def actualizar_producto(id: int, producto: ProductoNuevo):
    conexion = None

    if producto.Precio <= 0 or producto.Existencia < 0:
        raise HTTPException(
            status_code=400,
            detail="Precio o existencia incorrecta"
        )

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE Producto
            SET IdCategoriaProducto = %s,
                IdMarca = %s,
                Nombre = %s,
                Precio = %s,
                Existencia = %s
            WHERE IdProducto = %s
        """, (
            producto.IdCategoriaProducto,
            producto.IdMarca,
            producto.Nombre,
            producto.Precio,
            producto.Existencia,
            id
        ))

        if cursor.rowcount == 0:
            conexion.rollback()
            raise HTTPException(
                status_code=404,
                detail="Producto no encontrado"
            )

        conexion.commit()

        return {"mensaje": "Producto actualizado correctamente"}

    except HTTPException:
        raise

    except Exception:
        if conexion is not None:
            conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail="Error al actualizar producto"
        )

    finally:
        if conexion is not None:
            conexion.close()


# ELIMINAR PRODUCTO

@app.delete("/productos/{id}")
def eliminar_producto(id: int):
    conexion = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        # Verificar que el producto exista
        cursor.execute(
            "SELECT IdProducto FROM Producto WHERE IdProducto = %s",
            (id,)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Producto no encontrado"
            )

        # Verificar si tiene compras
        cursor.execute(
            "SELECT IdProducto FROM DetalleCompra WHERE IdProducto = %s",
            (id,)
        )

        tiene_compras = cursor.fetchone() is not None

        # Verificar si tiene ventas
        cursor.execute(
            "SELECT IdProducto FROM DetalleVentaProducto WHERE IdProducto = %s",
            (id,)
        )

        tiene_ventas = cursor.fetchone() is not None

        # Verificar si tiene movimientos de inventario
        cursor.execute(
            "SELECT IdProducto FROM MovimientoInventario WHERE IdProducto = %s",
            (id,)
        )

        tiene_movimientos = cursor.fetchone() is not None

        if tiene_compras or tiene_ventas or tiene_movimientos:
            raise HTTPException(
                status_code=409,
                detail="No se puede eliminar porque tiene compras, ventas o movimientos"
            )

        # Eliminar producto
        cursor.execute(
            "DELETE FROM Producto WHERE IdProducto = %s",
            (id,)
        )

        conexion.commit()

        return {"mensaje": "Producto eliminado correctamente"}

    except HTTPException:
        raise

    except Exception:
        if conexion is not None:
            conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail="Error al eliminar producto"
        )

    finally:
        if conexion is not None:
            conexion.close()


# CONSULTAR TODOS LOS PROVEEDORES

@app.get("/proveedores")
def obtener_proveedores():
    conexion = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT IdProveedor, Nombre, Telefono,
                   Correo, Direccion
            FROM Proveedor
        """)

        proveedores = []

        for fila in cursor.fetchall():
            proveedores.append({
                "IdProveedor": fila[0],
                "Nombre": fila[1],
                "Telefono": fila[2],
                "Correo": fila[3],
                "Direccion": fila[4]
            })

        return proveedores

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al consultar proveedores"
        )

    finally:
        if conexion is not None:
            conexion.close()


# REGISTRAR PROVEEDORES

class ProveedorNuevo(BaseModel):
    Nombre: str
    Telefono: str
    Correo: str
    Direccion: str


@app.post("/proveedores")
def crear_proveedor(proveedor: ProveedorNuevo):
    conexion = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO Proveedor
            (Nombre, Telefono, Correo, Direccion)
            VALUES (%s, %s, %s, %s)
        """, (
            proveedor.Nombre,
            proveedor.Telefono,
            proveedor.Correo,
            proveedor.Direccion
        ))

        conexion.commit()

        return {"mensaje": "Proveedor registrado correctamente"}

    except Exception:
        if conexion is not None:
            conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail="Error al registrar proveedor"
        )

    finally:
        if conexion is not None:
            conexion.close()


# CONSULTAR PROVEEDOR POR ID

@app.get("/proveedores/{id}")
def buscar_proveedor(id: int):
    conexion = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT IdProveedor, Nombre, Telefono,
                   Correo, Direccion
            FROM Proveedor
            WHERE IdProveedor = %s
        """, (id,))

        fila = cursor.fetchone()

        if fila is None:
            raise HTTPException(
                status_code=404,
                detail="Proveedor no encontrado"
            )

        return {
            "IdProveedor": fila[0],
            "Nombre": fila[1],
            "Telefono": fila[2],
            "Correo": fila[3],
            "Direccion": fila[4]
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al consultar proveedor"
        )

    finally:
        if conexion is not None:
            conexion.close()


# ACTUALIZAR PROVEEDOR

@app.put("/proveedores/{id}")
def actualizar_proveedor(id: int, proveedor: ProveedorNuevo):
    conexion = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE Proveedor
            SET Nombre = %s,
                Telefono = %s,
                Correo = %s,
                Direccion = %s
            WHERE IdProveedor = %s
        """, (
            proveedor.Nombre,
            proveedor.Telefono,
            proveedor.Correo,
            proveedor.Direccion,
            id
        ))

        if cursor.rowcount == 0:
            conexion.rollback()
            raise HTTPException(
                status_code=404,
                detail="Proveedor no encontrado"
            )

        conexion.commit()

        return {"mensaje": "Proveedor actualizado correctamente"}

    except HTTPException:
        raise

    except Exception:
        if conexion is not None:
            conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail="Error al actualizar proveedor"
        )

    finally:
        if conexion is not None:
            conexion.close()


# ELIMINAR PROVEEDOR

@app.delete("/proveedores/{id}")
def eliminar_proveedor(id: int):
    conexion = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        # Verificar si existe el proveedor
        cursor.execute("""
            SELECT IdProveedor
            FROM Proveedor
            WHERE IdProveedor = %s
        """, (id,))

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Proveedor no encontrado"
            )

        # Verificar si tiene compras registradas
        cursor.execute("""
            SELECT IdCompra
            FROM Compra
            WHERE IdProveedor = %s
        """, (id,))

        if cursor.fetchone() is not None:
            raise HTTPException(
                status_code=409,
                detail="No se puede eliminar porque tiene compras registradas"
            )

        # Eliminar proveedor
        cursor.execute("""
            DELETE FROM Proveedor
            WHERE IdProveedor = %s
        """, (id,))

        conexion.commit()

        return {"mensaje": "Proveedor eliminado correctamente"}

    except HTTPException:
        raise

    except Exception:
        if conexion is not None:
            conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail="Error al eliminar proveedor"
        )

    finally:
        if conexion is not None:
            conexion.close()


# CONSULTAR TODAS LAS CITAS

@app.get("/citas")
def obtener_citas():
    conexion = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT IdCita, IdCliente, IdEstadoCita,
                   Fecha, HoraInicio, HoraFin, Observacion
            FROM Cita
        """)

        citas = []

        for fila in cursor.fetchall():
            citas.append({
                "IdCita": fila[0],
                "IdCliente": fila[1],
                "IdEstadoCita": fila[2],
                "Fecha": str(fila[3]),
                "HoraInicio": str(fila[4]),
                "HoraFin": str(fila[5]),
                "Observacion": fila[6]
            })

        return citas

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al consultar citas"
        )

    finally:
        if conexion is not None:
            conexion.close()


# REGISTRAR UNA CITA

from datetime import date, time

class CitaNueva(BaseModel):
    IdCliente: int
    IdEstadoCita: int
    Fecha: date
    HoraInicio: time
    HoraFin: time
    Observacion: str = ""


@app.post("/citas")
def crear_cita(cita: CitaNueva):
    conexion = None

    # Validar el horario
    if cita.HoraFin <= cita.HoraInicio:
        raise HTTPException(
            status_code=400,
            detail="La hora de fin debe ser mayor a la de inicio"
        )

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        # Comprobar si ya existe una cita en ese horario
        cursor.execute("""
            SELECT IdCita
            FROM Cita
            WHERE Fecha = %s
            AND HoraInicio < %s
            AND HoraFin > %s
            AND IdEstadoCita <> 3
        """, (
            cita.Fecha,
            cita.HoraFin,
            cita.HoraInicio
        ))

        if cursor.fetchone() is not None:
            raise HTTPException(
                status_code=409,
                detail="Ya existe una cita en ese horario"
            )

        # Registrar la cita
        cursor.execute("""
            INSERT INTO Cita
            (IdCliente, IdEstadoCita, Fecha,
             HoraInicio, HoraFin, Observacion)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            cita.IdCliente,
            cita.IdEstadoCita,
            cita.Fecha,
            cita.HoraInicio,
            cita.HoraFin,
            cita.Observacion
        ))

        conexion.commit()

        return {"mensaje": "Cita registrada correctamente"}

    except HTTPException:
        raise

    except Exception:
        if conexion is not None:
            conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail="Error al registrar cita"
        )

    finally:
        if conexion is not None:
            conexion.close()


# CONSULTAR CITA POR ID

@app.get("/citas/{id}")
def buscar_cita(id: int):
    conexion = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT IdCita, IdCliente, IdEstadoCita,
                   Fecha, HoraInicio, HoraFin, Observacion
            FROM Cita
            WHERE IdCita = %s
        """, (id,))

        fila = cursor.fetchone()

        if fila is None:
            raise HTTPException(
                status_code=404,
                detail="Cita no encontrada"
            )

        return {
            "IdCita": fila[0],
            "IdCliente": fila[1],
            "IdEstadoCita": fila[2],
            "Fecha": str(fila[3]),
            "HoraInicio": str(fila[4]),
            "HoraFin": str(fila[5]),
            "Observacion": fila[6]
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al consultar cita"
        )

    finally:
        if conexion is not None:
            conexion.close()


# ACTUALIZAR UNA CITA

@app.put("/citas/{id}")
def actualizar_cita(id: int, cita: CitaNueva):
    conexion = None

    if cita.HoraFin <= cita.HoraInicio:
        raise HTTPException(
            status_code=400,
            detail="La hora de fin debe ser mayor a la de inicio"
        )

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        # Verificar si existe la cita
        cursor.execute("""
            SELECT IdCita
            FROM Cita
            WHERE IdCita = %s
        """, (id,))

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Cita no encontrada"
            )

        # Verificar que el nuevo horario esté disponible
        cursor.execute("""
            SELECT IdCita
            FROM Cita
            WHERE Fecha = %s
            AND HoraInicio < %s
            AND HoraFin > %s
            AND IdEstadoCita <> 3
            AND IdCita <> %s
        """, (
            cita.Fecha,
            cita.HoraFin,
            cita.HoraInicio,
            id
        ))

        if cursor.fetchone() is not None:
            raise HTTPException(
                status_code=409,
                detail="Ya existe una cita en ese horario"
            )

        # Actualizar la cita
        cursor.execute("""
            UPDATE Cita
            SET IdCliente = %s,
                IdEstadoCita = %s,
                Fecha = %s,
                HoraInicio = %s,
                HoraFin = %s,
                Observacion = %s
            WHERE IdCita = %s
        """, (
            cita.IdCliente,
            cita.IdEstadoCita,
            cita.Fecha,
            cita.HoraInicio,
            cita.HoraFin,
            cita.Observacion,
            id
        ))

        conexion.commit()

        return {"mensaje": "Cita actualizada correctamente"}

    except HTTPException:
        raise

    except Exception:
        if conexion is not None:
            conexion.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error al actualizar cita"
        )

    finally:
        if conexion is not None:
            conexion.close()


# ELIMINAR UNA CITA

@app.delete("/citas/{id}")
def eliminar_cita(id: int):
    conexion = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        # Verificar si existe la cita
        cursor.execute("""
            SELECT IdCita
            FROM Cita
            WHERE IdCita = %s
        """, (id,))

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Cita no encontrada"
            )

        # Verificar si tiene servicios relacionados
        cursor.execute("""
            SELECT IdCita
            FROM DetalleCita
            WHERE IdCita = %s
        """, (id,))

        tiene_servicios = cursor.fetchone() is not None

        # Verificar si tiene ventas relacionadas
        cursor.execute("""
            SELECT IdCita
            FROM Venta
            WHERE IdCita = %s
        """, (id,))

        tiene_ventas = cursor.fetchone() is not None

        if tiene_servicios or tiene_ventas:
            raise HTTPException(
                status_code=409,
                detail="No se puede eliminar porque tiene servicios o ventas relacionadas"
            )

        # Eliminar cita
        cursor.execute("""
            DELETE FROM Cita
            WHERE IdCita = %s
        """, (id,))

        conexion.commit()

        return {"mensaje": "Cita eliminada correctamente"}

    except HTTPException:
        raise

    except Exception:
        if conexion is not None:
            conexion.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error al eliminar cita"
        )

    finally:
        if conexion is not None:
            conexion.close()


# REGISTRAR COMPRA CON PROCEDIMIENTO ALMACENADO

class CompraNueva(BaseModel):
    IdProveedor: int
    IdUsuario: int
    IdProducto: int
    Cantidad: int
    PrecioCompra: float


@app.post("/compras")
def registrar_compra(compra: CompraNueva):
    conexion = None

    if compra.Cantidad <= 0 or compra.PrecioCompra <= 0:
        raise HTTPException(
            status_code=400,
            detail="La cantidad y el precio deben ser mayores a cero"
        )

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            EXEC SP_RegistrarCompra
                @IdProveedor = %s,
                @IdUsuario = %s,
                @IdProducto = %s,
                @Cantidad = %s,
                @PrecioCompra = %s
        """, (
            compra.IdProveedor,
            compra.IdUsuario,
            compra.IdProducto,
            compra.Cantidad,
            compra.PrecioCompra
        ))

        conexion.commit()

        return {"mensaje": "Compra registrada correctamente"}

    except Exception:
        if conexion is not None:
            conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail="Error al registrar compra"
        )

    finally:
        if conexion is not None:
            conexion.close()


# REGISTRAR VENTA CON PROCEDIMIENTO ALMACENADO

class VentaNueva(BaseModel):
    IdCliente: int
    IdUsuario: int
    IdProducto: int
    Cantidad: int


@app.post("/ventas")
def registrar_venta(venta: VentaNueva):
    conexion = None

    if venta.Cantidad <= 0:
        raise HTTPException(
            status_code=400,
            detail="La cantidad debe ser mayor a cero"
        )

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            EXEC SP_RegistrarVenta
                @IdCliente = %s,
                @IdUsuario = %s,
                @IdProducto = %s,
                @Cantidad = %s
        """, (
            venta.IdCliente,
            venta.IdUsuario,
            venta.IdProducto,
            venta.Cantidad
        ))

        conexion.commit()

        return {"mensaje": "Venta registrada correctamente"}

    except Exception:
        if conexion is not None:
            conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail="Error al registrar venta"
        )

    finally:
        if conexion is not None:
            conexion.close()


# REPORTE DE VENTAS POR MES

@app.get("/reportes/ventas")
def reporte_ventas():
    conexion = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                YEAR(FechaVenta) AS Anio,
                MONTH(FechaVenta) AS Mes,
                COUNT(*) AS TotalVentas,
                SUM(Total) AS Ingresos
            FROM Venta
            GROUP BY
                YEAR(FechaVenta),
                MONTH(FechaVenta)
            ORDER BY Anio, Mes
        """)

        resultados = []

        for fila in cursor.fetchall():
            resultados.append({
                "Anio": fila[0],
                "Mes": fila[1],
                "TotalVentas": fila[2],
                "Ingresos": float(fila[3])
            })

        return resultados

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al generar reporte de ventas"
        )

    finally:
        if conexion is not None:
            conexion.close()


# REPORTE DE SERVICIOS MAS SOLICITADOS

@app.get("/reportes/servicios")
def reporte_servicios():
    conexion = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT
                s.Nombre AS Servicio,
                COUNT(*) AS VecesSolicitado
            FROM DetalleCita AS dc
            INNER JOIN Servicio AS s
                ON dc.IdServicio = s.IdServicio
            INNER JOIN Cita AS c
                ON dc.IdCita = c.IdCita
            INNER JOIN EstadoCita AS ec
                ON c.IdEstadoCita = ec.IdEstadoCita
            WHERE ec.Nombre = 'Completada'
            GROUP BY s.IdServicio, s.Nombre
            ORDER BY VecesSolicitado DESC
        """)

        resultados = []

        for fila in cursor.fetchall():
            resultados.append({
                "Servicio": fila[0],
                "VecesSolicitado": fila[1]
            })

        return resultados

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Error al generar reporte de servicios"
        )

    finally:
        if conexion is not None:
            conexion.close()
