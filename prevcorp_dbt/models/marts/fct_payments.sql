select
    payment_id,
    claim_id,
    policyholder_id,
    contract_id,
    company_id,
    risk_type,
    gross_amount,
    net_amount,
    tax_amount,
    payment_date,
    policyholder_last_name,
    policyholder_first_name
from {{ ref('int_payments_enriched') }}
