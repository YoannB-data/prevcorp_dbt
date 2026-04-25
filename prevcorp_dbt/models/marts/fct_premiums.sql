select
    premium_id,
    contract_id,
    contract_number,
    contract_type,
    contract_is_active,
    segment_name,
    premium_amount,
    collection_date,
    due_date
from {{ ref('int_premiums_enriched') }}
