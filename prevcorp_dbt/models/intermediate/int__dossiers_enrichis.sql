select
    d.dossier_id,
    d.dossier_numero,
    d.risque,
    d.nature_arret,
    d.fait_generateur_date,

    -- Assuré
    d.assure_id,
    a.nom as assure_nom,
    a.prenom as assure_prenom,
    a.naissance_date,
    a.adresse,
    a.pays_code,

    -- Contrat et segment
    d.contrat_id,
    c.contrat_numero,
    c.contrat_type,
    s.segment_nom,

    -- Entreprise
    d.entreprise_id,
    e.siret,
    e.entreprise_nom,
    e.est_en_cours   as entreprise_est_en_cours,

    d.salaire_montant,
    d.creation_date,
    d.etat_date,
    d.etat_motif,
    d.est_en_cours,
    d.attest_non_activite_date,
    d.justif_ss_date,

    -- Durée du dossier en jours
    case
        when d.est_en_cours then datediff('day', d.creation_date, DATE '2025-12-31')
        else datediff('day', d.creation_date, d.etat_date)
    end as duree_dossier_jours

from {{ ref('stg_prevcorp__dossiers') }} d
left join {{ ref('stg_prevcorp__assures') }} a
    on d.assure_id = a.assure_id
left join {{ ref('stg_prevcorp__entreprises') }} e
    on d.entreprise_id = e.entreprise_id
left join {{ ref('stg_prevcorp__contrats') }} c
    on d.contrat_id = c.contrat_id
left join {{ ref('stg_prevcorp__segments') }} s
    on c.segment_id = s.segment_id
