select
    paiement_id,
    dossier_id,
    assure_id,
    contrat_id,
    entreprise_id,
    risque,
    brut_montant,
    net_montant,
    pas_montant,
    paiement_date,
    assure_nom,
    assure_prenom
from {{ ref('int__paiements_enrichis') }}
