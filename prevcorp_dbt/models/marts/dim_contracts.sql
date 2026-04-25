select
    contract_id,
    contract_number,
    contract_type,
    segment_name,
    start_date,
    end_date,
    is_active,
    company_count
from {{ ref('int_contracts_enriched') }}
