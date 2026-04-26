select
    policyholder_id as assure_id,
    trim(nom) as nom,
    trim(prenom) as prenom,
    cast(dt_naissance as date) as naissance_date,
    trim(adresse) as adresse,
    cod_pays as pays_code,
    attest_fisc_etr as attestation_fiscale_etranger
    
from {{ ref('raw_policyholders') }}
