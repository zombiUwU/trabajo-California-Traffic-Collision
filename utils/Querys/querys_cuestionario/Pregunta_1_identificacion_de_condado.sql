--- consultas que pidio el prof jesus

WITH metricas_por_accidente AS (
    SELECT 
        c.case_id,
        c.location_type AS condado, 
        CASE WHEN (
            (LOWER(p.party_sobriety) LIKE '%had been drinking%') 
            AND (p.cellphone_in_use IN ('Y', '1', 'Yes')) 
            AND (LOWER(c.lighting) LIKE '%dark%' OR LOWER(c.lighting) LIKE '%dusk%' OR LOWER(c.lighting) LIKE '%dawn%')
        ) THEN 1 ELSE 0 END AS cumple_factores
    FROM collisions c
    JOIN parties p ON c.case_id = p.case_id
),
estadisticas_condado AS (
    SELECT 
        condado,
        COUNT(*) AS total_accidentes,
        SUM(cumple_factores) AS accidentes_con_factores,
        (CAST(SUM(cumple_factores) AS FLOAT) / NULLIF(COUNT(*), 0)) AS proporcion_condado
    FROM metricas_por_accidente
    GROUP BY condado
),
promedio_estatal AS (
    SELECT 
        AVG(proporcion_condado) AS media_estatal,
        SQRT(AVG(proporcion_condado * proporcion_condado) - (AVG(proporcion_condado) * AVG(proporcion_condado))) AS desv_estatal
    FROM estadisticas_condado
)
SELECT 
    e.condado,
    e.total_accidentes,
    e.accidentes_con_factores,
    ROUND(e.proporcion_condado, 5) AS proporcion,
    ROUND(p.media_estatal, 5) AS promedio_estatal,
    ROUND((e.proporcion_condado - p.media_estatal) / NULLIF(p.desv_estatal, 0), 2) AS desviaciones_estandar
FROM estadisticas_condado e, promedio_estatal p
WHERE (e.proporcion_condado - p.media_estatal) > (2 * p.desv_estatal) 
ORDER BY desviaciones_estandar DESC;

---- segunda consulta con una sola desviacion


  WITH metricas_por_accidente AS (
   -- usamos las variables party_sobriety, condado y lighting como filtro he indicador 
    SELECT 
        c.case_id,
        c.location_type AS condado, 
        CASE WHEN (
            (LOWER(p.party_sobriety) LIKE '%had been drinking%') 
            AND (p.cellphone_in_use = '1') 
            AND (LOWER(c.lighting) LIKE '%dark%' OR LOWER(c.lighting) LIKE '%dusk%' OR LOWER(c.lighting) LIKE '%dawn%')
        ) THEN 1 ELSE 0 END AS cumple_factores
    FROM collisions c
    JOIN parties p ON c.case_id = p.case_id
),
estadisticas_condado AS (
    -- Agrupamos por condado para obtener totales y proporciones
    SELECT 
        condado,
        COUNT(*) AS total_accidentes,
        SUM(cumple_factores) AS accidentes_con_factores,
        (CAST(SUM(cumple_factores) AS FLOAT) / NULLIF(COUNT(*), 0)) AS proporcion_condado
    FROM metricas_por_accidente
    GROUP BY condado
),
promedio_estatal AS (
    SELECT 
        AVG(proporcion_condado) AS media_estatal,
        -- Fórmula: SQRT( AVG(x^2) - AVG(x)^2 )
        SQRT(AVG(proporcion_condado * proporcion_condado) - (AVG(proporcion_condado) * AVG(proporcion_condado))) AS desv_estatal
    FROM estadisticas_condado
)
SELECT 
    e.condado,
    e.total_accidentes,
    e.accidentes_con_factores,
    ROUND(e.proporcion_condado, 5) AS proporcion,
    ROUND(p.media_estatal, 5) AS promedio_estatal,
    ROUND((e.proporcion_condado - p.media_estatal) / NULLIF(p.desv_estatal, 0), 2) AS desviaciones_estandar
FROM estadisticas_condado e, promedio_estatal p
WHERE (e.proporcion_condado - p.media_estatal) > (1 * p.desv_estatal) 
ORDER BY desviaciones_estandar DESC;