/* --------------------------------------------------------------------
   PREGUNTA 5: IDENTIFICACIÓN DE GRUPOS DEMOGRÁFICOS CON TENDENCIA CRÍTICA
   ---------------------------------------------------------------------
*/
-- capa 1: limpieza y preparación de los datos 
WITH Datos_Base AS (
    SELECT 
        strftime('%Y', c.collision_date) AS año,
        v.victim_sex AS genero,
        CASE 
            WHEN v.victim_age BETWEEN 18 AND 30 THEN '18-30'
            WHEN v.victim_age BETWEEN 31 AND 50 THEN '31-50'
            WHEN v.victim_age BETWEEN 51 AND 65 THEN '51-65'
            ELSE 'Otros'
        END AS rango_etario,
        -- detectamos alcohol según el estándar de la DB
        CASE WHEN p.party_sobriety LIKE 'had been drinking%' THEN 1 ELSE 0 END AS con_alcohol
    FROM parties p
    JOIN collisions c ON p.case_id = c.case_id
    JOIN victims v ON p.case_id = v.case_id AND p.party_number = v.party_number
    -- filtro At_Fault: excluimos vehículos no involucrados o sin culpa aparente
    WHERE p.at_fault NOT IN ('none apparent', 'uninvolved vehicle')
      AND v.victim_sex IN ('male', 'female')
),
-- capa 2: agrego y calculo las tasas
-- calculando la tasa de alcohol sobre el total de responsables de cada grupo
Metricas_Anuales AS (
    SELECT 
        año, genero, rango_etario,
        COUNT(*) AS total_accidentes,
        SUM(con_alcohol) AS total_alcohol
    FROM Datos_Base
    GROUP BY 1, 2, 3
    HAVING total_accidentes > 100 -- requerimiento para responder el query
),
-- capa 3: análisis y tendencias 
-- comparamos la tasa actual con los dos años anteriores para detectar la tendencia creciente 
Analisis_Tendencia AS (
    SELECT 
        *,
        ROUND((CAST(total_alcohol AS FLOAT) / total_accidentes) * 100, 2) AS tasa,
        -- tasa del año anterior (T-1)
        LAG(ROUND((CAST(total_alcohol AS FLOAT) / total_accidentes) * 100, 2)) 
            OVER (PARTITION BY genero, rango_etario ORDER BY año) AS tasa_T1,
        -- tasa de hace dos años (T-2)
        LAG(ROUND((CAST(total_alcohol AS FLOAT) / total_accidentes) * 100, 2), 2) 
            OVER (PARTITION BY genero, rango_etario ORDER BY año) AS tasa_T2
    FROM Metricas_Anuales
)
-- capa 4: REPORTE con filtro de la tendecia creciente y mostramos registros que superen 2 años previos
SELECT 
    año,
    genero AS "Género",
    rango_etario AS "Rango Etario",
    tasa || '%' AS "Tasa Alcohol",
    ROUND(tasa - tasa_T1, 2) || '%' AS "Variación Anual",
    -- ranking de peligrosidad por alcohol dentro de su mismo género
    DENSE_RANK() OVER (PARTITION BY año, genero ORDER BY tasa DESC) AS "Rank_en_Género"
FROM Analisis_Tendencia
WHERE tasa > tasa_T1      -- crecimiento año actual
  AND tasa_T1 > tasa_T2   -- crecimiento año anterior (tendecia de 2 años)
ORDER BY año DESC, tasa DESC;