select
    beneficiary_id as beneficiaire_id,
    claim_id as dossier_id,
    trim(nom)  as nom,
    trim(prenom) as prenom,
    cast(dt_naissance as date) as naissance_date
    
from {{ ref('raw_beneficiaries') }}
