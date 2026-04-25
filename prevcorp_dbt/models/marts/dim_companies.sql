select
    company_id,
    siret,
    company_name,
    start_date,
    end_date,
    is_active
from {{ ref('stg_prevcorp__companies') }}
