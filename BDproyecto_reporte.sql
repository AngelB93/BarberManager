
USE BarberManagerDB;


-- REPORTE 1: VENTAS POR MES

SELECT
    YEAR(FechaVenta) AS Anio,
    MONTH(FechaVenta) AS Mes,
    COUNT(IdVenta) AS TotalVentas,
    SUM(Total) AS IngresosTotales
FROM Venta
GROUP BY
    YEAR(FechaVenta),
    MONTH(FechaVenta)
ORDER BY Anio, Mes;



USE BarberManagerDB;


-- REPORTE 2: SERVICIOS MAS SOLICITADOS

SELECT
    S.Nombre AS Servicio,
    COUNT(D.IdDetalleCita) AS VecesSolicitado,
    SUM(D.Precio) AS ValorTotal
FROM DetalleCita D
INNER JOIN Servicio S
    ON D.IdServicio = S.IdServicio
INNER JOIN Cita C
    ON D.IdCita = C.IdCita
INNER JOIN EstadoCita E
    ON C.IdEstadoCita = E.IdEstadoCita
WHERE E.Nombre = 'Completada'
GROUP BY S.Nombre
ORDER BY VecesSolicitado DESC;
