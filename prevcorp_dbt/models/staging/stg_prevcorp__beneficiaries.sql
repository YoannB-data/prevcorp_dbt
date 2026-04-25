select
    beneficiary_id,
    claim_id,
    trim(nom)                  as last_name,
    trim(prenom)               as first_name,
    cast(dt_naissance as date) as birth_date
from {{ ref('raw_beneficiaries') }}
