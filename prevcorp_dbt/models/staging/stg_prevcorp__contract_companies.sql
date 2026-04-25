select
    contract_id,
    company_id
from {{ ref('raw_contract_companies') }}
