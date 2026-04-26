select
    assure_id,
    nom,
    prenom,
    naissance_date,
    adresse,
    pays_code,
    attestation_fiscale_etranger
    
from {{ ref('stg_prevcorp__assures') }}
