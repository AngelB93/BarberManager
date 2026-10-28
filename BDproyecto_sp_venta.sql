
USE BarberManagerDB;


ALTER PROCEDURE SP_RegistrarVenta
    @IdCliente INT,
    @IdUsuario INT,
    @IdProducto INT,
    @Cantidad INT
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
    
    	COMMIT TRANSACTION;

        -- Validar que la cantidad sea correcta
        IF @Cantidad <= 0
        BEGIN
            THROW 50001, 'La cantidad debe ser mayor a cero', 1;
        END;

        -- Verificar que exista el cliente
        IF NOT EXISTS (
            SELECT 1 FROM Cliente
            WHERE IdCliente = @IdCliente
        )
        BEGIN
            THROW 50002, 'El cliente no existe', 1;
        END;

        -- Verificar que exista el usuario
        IF NOT EXISTS (
            SELECT 1 FROM Usuario
            WHERE IdUsuario = @IdUsuario
        )
        BEGIN
            THROW 50003, 'El usuario no existe', 1;
        END;

        -- Verificar que exista el producto
        IF NOT EXISTS (
            SELECT 1 FROM Producto
            WHERE IdProducto = @IdProducto
        )
        BEGIN
            THROW 50004, 'El producto no existe', 1;
        END;

        BEGIN TRANSACTION;

        -- Obtener el precio del producto
        DECLARE @Precio DECIMAL(10,2);

        SELECT @Precio = Precio
        FROM Producto
        WHERE IdProducto = @IdProducto;

        -- Verificar existencia y descontar
        UPDATE Producto
        SET Existencia = Existencia - @Cantidad
        WHERE IdProducto = @IdProducto
        AND Existencia >= @Cantidad;

        IF @@ROWCOUNT = 0
        BEGIN
            THROW 50005, 'No hay suficientes productos', 1;
        END;

        -- Registrar la venta
        INSERT INTO Venta
        (IdCliente, IdUsuario, FechaVenta, Total)
        VALUES
        (@IdCliente, @IdUsuario, GETDATE(),
         @Cantidad * @Precio);

        -- Obtener el ID de la venta
        DECLARE @IdVenta INT;
        SET @IdVenta = SCOPE_IDENTITY();

        -- PRUEBA DE ROLLBACK
        -- Quitar los dos guiones para provocar el error
        --THROW 50006, 'Error de prueba para ROLLBACK', 1;

        -- Registrar el detalle de venta
        INSERT INTO DetalleVentaProducto
        (IdVenta, IdProducto, Cantidad, PrecioUnitario)
        VALUES
        (@IdVenta, @IdProducto, @Cantidad, @Precio);

        -- Registrar la salida del inventario
        INSERT INTO MovimientoInventario
        (IdProducto, IdVenta, TipoMovimiento, Cantidad)
        VALUES
        (@IdProducto, @IdVenta, 'Salida', @Cantidad);

        

        PRINT 'Venta registrada correctamente';

    END TRY
    BEGIN CATCH

        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;

        THROW;

    END CATCH
END;

SELECT IdProducto, Nombre, Precio, Existencia
FROM Producto
WHERE IdProducto = 1;

EXEC SP_RegistrarVenta
    @IdCliente = 1,
    @IdUsuario = 1,
    @IdProducto = 1,
    @Cantidad = 1;

