WITH
accidentes AS (
    SELECT 
        case_id,
        location_type AS ruta,
        strftime('%Y', CAST(collision_date AS DATE)) AS anio,
        ROUND(latitude, 2) AS lat_celda,
        ROUND(longitude, 2) AS lon_celda,
        latitude,
        longitude,
        killed_victims,
        primary_collision_factor
    FROM collisions
    WHERE LOWER(collision_severity) IN ('fatal', 'pain')
      AND location_type IS NOT NULL
      AND latitude IS NOT NULL
      AND longitude IS NOT NULL
),
celdas AS (
    SELECT
        ruta,
        anio,
        lat_celda,
        lon_celda,
        COUNT(*) AS cantidad_accidentes,
        SUM(killed_victims) AS total_fatalidades,
        AVG(latitude) AS latitud_central,
        AVG(longitude) AS longitud_central
    FROM accidentes
    GROUP BY ruta, anio, lat_celda, lon_celda
    HAVING COUNT(*) >= 3
),
factor_moda AS (
    SELECT
        a.ruta,
        a.anio,
        a.lat_celda,
        a.lon_celda,
        a.primary_collision_factor,
        COUNT(*) AS freq,
        ROW_NUMBER() OVER (
            PARTITION BY a.ruta, a.anio, a.lat_celda, a.lon_celda 
            ORDER BY COUNT(*) DESC
        ) AS rn
    FROM accidentes a
    JOIN celdas c 
    ON a.ruta = c.ruta 
    AND a.anio = c.anio 
    AND a.lat_celda = c.lat_celda 
    AND a.lon_celda = c.lon_celda
GROUP BY a.ruta, a.anio, a.lat_celda, a.lon_celda, a.primary_collision_factor
)
SELECT
    c.ruta AS ruta_estatal,
    c.anio,
    c.latitud_central,
    c.longitud_central,
    c.cantidad_accidentes,
    c.total_fatalidades,
    f.primary_collision_factor AS factor_colision_mas_frecuente
FROM celdas c
LEFT JOIN factor_moda f 
        ON c.ruta = f.ruta 
    AND c.anio = f.anio 
    AND c.lat_celda = f.lat_celda 
    AND c.lon_celda = f.lon_celda 
    AND f.rn = 1
ORDER BY c.cantidad_accidentes DESC;