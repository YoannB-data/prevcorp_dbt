select
    ce.contrat_id,
    c.contrat_numero,
    ce.entreprise_id,
    e.entreprise_nom,
    c.est_en_cours  as contrat_est_en_cours,
    e.est_en_cours  as entreprise_est_en_cours

from {{ ref('stg_prevcorp__contrats_entreprises') }} as ce
inner join {{ ref('stg_prevcorp__contrats') }} as c
    on ce.contrat_id = c.contrat_id
inner join {{ ref('stg_prevcorp__entreprises') }} as e
    on ce.entreprise_id = e.entreprise_id
