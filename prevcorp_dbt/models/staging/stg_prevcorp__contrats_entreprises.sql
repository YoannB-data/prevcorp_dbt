select
    contract_id as contrat_id,
    company_id  as entreprise_id
    
from {{ ref('raw_contract_companies') }}
