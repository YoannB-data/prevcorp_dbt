select
    c.contrat_id,
    c.contrat_numero,
    c.contrat_type,
    c.debut_date,
    c.fin_date,
    c.est_en_cours,
    c.segment_id,
    s.segment_nom,
    count(ce.entreprise_id) as entreprise_nombre

from {{ ref('stg_prevcorp__contrats') }} c
left join {{ ref('stg_prevcorp__segments') }} s
    on c.segment_id = s.segment_id
left join {{ ref('stg_prevcorp__contrats_entreprises') }} ce
    on c.contrat_id = ce.contrat_id
group by
    all
