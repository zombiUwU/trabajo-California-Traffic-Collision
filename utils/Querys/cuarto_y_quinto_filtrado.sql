--- seleccion de las variables de victims
SELECT id, 
case_id, 
party_number, 
victim_role, 
victim_sex, 
victim_age, 
victim_degree_of_injury, 
victim_seating_position, 
victim_safety_equipment_1, 
victim_safety_equipment_2, 
victim_ejected FROM victims;


--- creacion de la tabla involved_victims

WITH biometria_maestra AS (
        SELECT v.id,
            (SELECT v2.victim_sex FROM victims v2 WHERE v2.id = v.id AND v2.victim_sex IS NOT NULL AND v2.victim_sex NOT IN ('', 'UNKNOWN', 'NOT_SPECIFIED') GROUP BY 1 ORDER BY COUNT(*) DESC LIMIT 1) AS sexo_real,
            (SELECT (CAST(SUBSTR(c2.collision_date, 1, 4) AS INT) - v3.victim_age) FROM victims v3 JOIN collisions c2 ON v3.case_id = c2.case_id WHERE v3.id = v.id AND v3.victim_age > 0 AND v3.victim_age < 110 GROUP BY 1 ORDER BY COUNT(*) DESC LIMIT 1) AS anio_nac_real
        FROM victims v WHERE v.id IS NOT NULL GROUP BY v.id
    )
    SELECT v.id, v.case_id, bm.sexo_real,
        CASE 
            WHEN bm.anio_nac_real IS NULL THEN NULL
            WHEN (CAST(SUBSTR(c.collision_date, 1, 4) AS INT) - bm.anio_nac_real) NOT BETWEEN 0 AND 110 THEN NULL
            ELSE (CAST(SUBSTR(c.collision_date, 1, 4) AS INT) - bm.anio_nac_real)
        END AS victim_age
    FROM victims v JOIN collisions c ON v.case_id = c.case_id LEFT JOIN biometria_maestra bm ON v.id = bm.id;