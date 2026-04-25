select
    resource_id,
    claim_id,
    resource_type,
    monthly_amount,
    start_date,
    end_date,
    is_active
from {{ ref('stg_prevcorp__resources') }}
