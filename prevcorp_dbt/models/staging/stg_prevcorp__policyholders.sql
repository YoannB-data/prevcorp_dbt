select
    policyholder_id,
    trim(nom)                  as last_name,
    trim(prenom)               as first_name,
    cast(dt_naissance as date) as birth_date,
    trim(adresse)              as address,
    cod_pays                   as country_code,
    attest_fisc_etr            as has_foreign_tax_certificate
from {{ ref('raw_policyholders') }}
