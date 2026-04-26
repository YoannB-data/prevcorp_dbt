select
    cotisation_id,
    contrat_id,
    contrat_numero,
    contrat_type,
    contrat_est_en_cours,
    segment_nom,
    cotisation_montant,
    encaissement_date,
    echeance_date
    
from {{ ref('int__cotisations_enrichies') }}
