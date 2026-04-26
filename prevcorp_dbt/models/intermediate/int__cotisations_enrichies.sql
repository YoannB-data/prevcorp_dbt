select
    co.cotisation_id,
    co.contrat_id,
    c.contrat_numero,
    c.contrat_type,
    c.est_en_cours as contrat_est_en_cours,
    s.segment_nom,
    co.echeance_date,
    year(co.echeance_date)::varchar || ' ' || quarter(co.echeance_date)::varchar || 'T' as trimestre,
    co.cotisation_montant,
    co.encaissement_date

from {{ ref('stg_prevcorp__cotisations') }} co
left join {{ ref('stg_prevcorp__contrats') }} c
    on co.contrat_id = c.contrat_id
left join {{ ref('stg_prevcorp__segments') }} s
    on c.segment_id = s.segment_id
