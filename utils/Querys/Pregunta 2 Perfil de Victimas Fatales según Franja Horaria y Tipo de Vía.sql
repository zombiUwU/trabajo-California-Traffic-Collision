/* RESPUESTA DE LA PREGUNTA DE QUERY 2: Top 3 de Riesgo Demográfico por Franja*/

WITH Pre_Analisis AS (
    SELECT 
        -- Clasificación Horaria (Basada en HH:MM:SS)
        CASE 
            WHEN CAST(substr(c.collision_time, 1, 2) AS INT) BETWEEN 0 AND 5 THEN '00-06 (Madrugada)'
            WHEN CAST(substr(c.collision_time, 1, 2) AS INT) BETWEEN 6 AND 11 THEN '06-12 (Mañana)'
            WHEN CAST(substr(c.collision_time, 1, 2) AS INT) BETWEEN 12 AND 17 THEN '12-18 (Tarde)'
            ELSE '18-24 (Noche)'
        END AS Franja_Horaria,

        -- Rangos Etarios Exactos
        CASE 
            WHEN v.victim_age < 18 THEN 'a_Menor <18'
            WHEN v.victim_age BETWEEN 18 AND 30 THEN 'b_18-30'
            WHEN v.victim_age BETWEEN 31 AND 50 THEN 'c_31-50'
            WHEN v.victim_age BETWEEN 51 AND 65 THEN 'd_51-65'
            ELSE 'e_Mayor >65'
        END AS Rango_Etario,

        -- Tipo de Vía
        COALESCE(c.location_type, 'Vía Local/Calle') AS Tipo_Via,

        -- Cantidad de víctimas en esta combinación
        SUM(c.killed_victims) AS Cantidad_Fallecidos
    FROM collisions c
    INNER JOIN victims v ON c.case_id = v.case_id
    WHERE c.killed_victims > 0 
    GROUP BY 1, 2, 3
),
Calculo_Rankings AS (
    SELECT 
        Franja_Horaria,
        Rango_Etario,
        Tipo_Via,
        Cantidad_Fallecidos,
        -- TOTAL ACUMULADO: Se repite en la franja para poder calcular el %
        SUM(Cantidad_Fallecidos) OVER (PARTITION BY Franja_Horaria) AS Total_Franja,
        -- TOP 3: Ranking por cantidad de muertos en la franja
        DENSE_RANK() OVER (PARTITION BY Franja_Horaria ORDER BY Cantidad_Fallecidos DESC) AS Ranking
    FROM Pre_Analisis
)
SELECT 
    Franja_Horaria,
    substr(Rango_Etario, 3) as Rango_Etario, -- Quitamos el prefijo 'a_', 'b_'...
    Tipo_Via,
    Cantidad_Fallecidos,
    Total_Franja as Total_Fallecidos_Franja,
    ROUND((CAST(Cantidad_Fallecidos AS FLOAT) / Total_Franja) * 100, 2) || '%' AS Porcentaje_Impacto
FROM Calculo_Rankings
WHERE Ranking <= 3
ORDER BY Franja_Horaria ASC, Cantidad_Fallecidos DESC;

/* 
-------------------------------------------------------
NOTAS DE INTERPRETACIÓN DEL RESULTADO:
--------------------------------------------------------

1. LA "TRAMPA" DE LA VÍA LOCAL:
   Los datos revelan que el 100% de los accidentes fatales en el Top 3 de cada 
   franja horaria ocurren en 'Vía Local/Calle'. Esto demuestra que las 
   autopistas no son el escenario principal de muerte, sino las calles internas 
   donde el conductor suele bajar la guardia, o sea la muerte casi siempre esta en 
   las calles comunes de california

2. GRUPO CRÍTICO (18-30 AÑOS):
   Este rango etario es el más afectado, especialmente en la madrugada (00-06), 
   donde representan el 42.9% del impacto total de esa franja. Es el grupo 
   con mayor riesgo de accidentes fatales nocturnos.

3. ESTABILIDAD DEL RIESGO EN ADULTOS (31-60):
   A diferencia de los jóvenes, los adultos mantienen una presencia constante y 
   elevada (segundo lugar en el ranking) durante TODO el día, lo que sugiere 
   exposición por motivos laborales o de rutina diaria.

4. CONCLUSIÓN ESTRATÉGICA:
   La seguridad vial en California debe priorizar el control de velocidad y 
   vigilancia en calles residenciales/locales durante la noche, ya que es 
   donde se concentra la pérdida de vidas de la población joven.
--------------------------------------------------------------------------
*/