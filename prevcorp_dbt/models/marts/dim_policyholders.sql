select
    policyholder_id,
    last_name,
    first_name,
    birth_date,
    address,
    country_code,
    has_foreign_tax_certificate
from {{ ref('stg_prevcorp__policyholders') }}
