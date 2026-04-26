select
    p.paiement_id,
    p.dossier_id,
    d.dossier_numero,
    d.assure_id,
    d.risque,
    a.nom as assure_nom,
    a.prenom as assure_prenom,
    d.contrat_id,
    c.contrat_numero,
    d.entreprise_id,
    e.siret as entreprise_siret,
    e.entreprise_nom,
    p.brut_montant,
    p.net_montant,
    p.pas_montant,
    p.paiement_date

from {{ ref('stg_prevcorp__paiements') }} p
left join {{ ref('stg_prevcorp__dossiers') }} d
    on p.dossier_id = d.dossier_id
left join {{ ref('stg_prevcorp__assures') }} a
    on d.assure_id = a.assure_id
left join {{ ref('stg_prevcorp__contrats') }} c
    on d.contrat_id = c.contrat_id
left join {{ ref('stg_prevcorp__entreprises') }} e
    on d.entreprise_id = e.entreprise_id
