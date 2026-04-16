--- Seleccion de los datos de parties 

SELECT id,
        case_id,
        party_number,
        party_sobriety,
        party_type,
        party_drug_physical,
        movement_preceding_collision,
        at_fault,
        vehicle_make,
        vehicle_year,
        cellphone_in_use,
        statewide_vehicle_type,
        party_safety_equipment_1,
        party_safety_equipment_2
        FROM parties;