---Respuesta de los Querys planteados
---Evolución Mensual de la Severidad y Detección de Meses Atípicos

WITH metricas_mensuales AS (
-- Extraemos año y mes de la cadena de texto y calculamos la severidad
SELECT
CAST(SUBSTR(collision_date, 1, 4) AS INT) AS anio,
CAST(SUBSTR(collision_date, 6, 2) AS INT) AS mes,
COUNT(*) AS total_accidentes_mes,
-- Calculamos la suma ponderada y dividimos entre el total del mes
(SUM(CAST((killed_victims * 3) + (injured_victims * 1) AS FLOAT)) / COUNT(*)) AS indice_mes
FROM collisions
WHERE collision_date IS NOT NULL AND collision_date != ''
GROUP BY anio, mes
),
promedio_anual AS (
-- Promedio de los índices mensuales por cada año
SELECT
anio,
AVG(indice_mes) AS promedio_anio
FROM metricas_mensuales
GROUP BY anio
)
-- Comparación final con el umbral del 30%
SELECT
m.anio,
m.mes,
ROUND(m.indice_mes, 4) AS indice_del_mes,
ROUND(a.promedio_anio, 4) AS promedio_anual,
ROUND(((m.indice_mes - a.promedio_anio) / a.promedio_anio) * 100, 2) AS variacion_porcentual
FROM metricas_mensuales m
JOIN promedio_anual a ON m.anio = a.anio
WHERE m.indice_mes > (a.promedio_anio * 1.30)
ORDER BY m.anio DESC, m.mes ASC;


---Este query ejecuta la misma lógica pero nos permite observar cualquier mes que este ligeramente por encima de la media. (Una opcion extra para mostrar)

WITH metricas_mensuales AS (
SELECT
CAST(SUBSTR(TRIM(collision_date), 1, 4) AS INT) AS anio,
CAST(SUBSTR(TRIM(collision_date), 6, 2) AS INT) AS mes,
COUNT(*) AS total_accidentes_mes,
-- Usamos COALESCE para que si una columna es NULL la trate como 0
(SUM(CAST((COALESCE(killed_victims,0) * 3) + (COALESCE(injured_victims,0) * 1) AS FLOAT)) / COUNT(*)) AS indice_mes
FROM collisions
WHERE collision_date IS NOT NULL AND collision_date != ''
GROUP BY anio, mes
),
promedio_anual AS (
SELECT
anio,
AVG(indice_mes) AS promedio_anio
FROM metricas_mensuales
GROUP BY anio
)
SELECT
m.anio,
m.mes,
ROUND(m.indice_mes, 4) AS indice_del_mes,
ROUND(a.promedio_anio, 4) AS promedio_anual,
ROUND(((m.indice_mes - a.promedio_anio) / NULLIF(a.promedio_anio, 0)) * 100, 2) AS variacion_porcentual
FROM metricas_mensuales m
JOIN promedio_anual a ON m.anio = a.anio
-- Bajamos al 5% (1.05)
WHERE m.indice_mes > (a.promedio_anio * 1.05)
ORDER BY m.anio DESC, m.mes ASC;