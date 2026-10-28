
USE BarberManagerDB;



ALTER PROCEDURE SP_RegistrarCompra
    @IdProveedor INT,
    @IdUsuario INT,
    @IdProducto INT,
    @Cantidad INT,
    @PrecioCompra DECIMAL(10,2)
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
		
    	COMMIT TRANSACTION;
    	
        -- Validar los datos
        IF @Cantidad <= 0 OR @PrecioCompra <= 0
        BEGIN
            THROW 50001, 'Cantidad o precio incorrecto', 1;
        END;

        IF NOT EXISTS (
            SELECT 1 FROM Proveedor
            WHERE IdProveedor = @IdProveedor
        )
        BEGIN
            THROW 50002, 'El proveedor no existe', 1;
        END;

        IF NOT EXISTS (
            SELECT 1 FROM Usuario
            WHERE IdUsuario = @IdUsuario
        )
        BEGIN
            THROW 50003, 'El usuario no existe', 1;
        END;

        IF NOT EXISTS (
            SELECT 1 FROM Producto
            WHERE IdProducto = @IdProducto
        )
        BEGIN
            THROW 50004, 'El producto no existe', 1;
        END;

        BEGIN TRANSACTION;

        -- Registrar la compra
        INSERT INTO Compra
        (IdProveedor, IdUsuario, FechaCompra, Total)
        VALUES
        (@IdProveedor, @IdUsuario, GETDATE(),
         @Cantidad * @PrecioCompra);

        -- Obtener el ID de la compra
        DECLARE @IdCompra INT;
        SET @IdCompra = SCOPE_IDENTITY();

        -- PRUEBA DE ROLLBACK
        -- Quitar los dos guiones para provocar el error
        --THROW 50006, 'Error de prueba para ROLLBACK', 1;

        -- Registrar el detalle
        INSERT INTO DetalleCompra
        (IdCompra, IdProducto, Cantidad, PrecioCompra)
        VALUES
        (@IdCompra, @IdProducto, @Cantidad, @PrecioCompra);

        -- Aumentar las existencias
        UPDATE Producto
        SET Existencia = Existencia + @Cantidad
        WHERE IdProducto = @IdProducto;

        -- Registrar el movimiento
        INSERT INTO MovimientoInventario
        (IdProducto, IdCompra, TipoMovimiento, Cantidad)
        VALUES
        (@IdProducto, @IdCompra, 'Entrada', @Cantidad);

        

        PRINT 'Compra registrada correctamente';

    END TRY
    BEGIN CATCH

        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;

        THROW;

    END CATCH
END;




SELECT
    p.name AS Parametro,
    TYPE_NAME(p.user_type_id) AS TipoDato,
    p.max_length AS Longitud
FROM sys.parameters AS p
INNER JOIN sys.procedures AS sp
    ON p.object_id = sp.object_id
WHERE sp.name = 'SP_RegistrarVenta'
ORDER BY p.parameter_id;


SELECT IdProducto, Nombre, Existencia
FROM Producto
WHERE IdProducto = 1;


EXEC SP_RegistrarCompra
    @IdProveedor = 1,
    @IdUsuario = 1,
    @IdProducto = 1,
    @Cantidad = 5,
    @PrecioCompra = 20.00;



