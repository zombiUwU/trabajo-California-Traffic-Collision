--- la seleccion de las dos bases de datos con los años mas recientes
  SELECT * FROM case_ids
        where db_year IN ("2020", "2021");
--- la seleccion de la linea del tiempo y de las variables de interes de la tabla collissions
SELECT 
         case_id, 
         collision_severity,
         primary_collision_factor,
         killed_victims,
         injured_victims,
         injured_victims,
         pcf_violation_category,
         weather_1,
         lighting,
         type_of_collision,
         longitude,
         latitude,
         party_count,
         collision_date,
         collision_time,
         road_surface,
         location_type
         FROM collisions
         WHERE collision_date BETWEEN '2018-01-01' AND '2021-12-31';