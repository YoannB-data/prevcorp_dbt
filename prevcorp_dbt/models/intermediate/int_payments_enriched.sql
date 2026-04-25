select
    p.payment_id,
    p.claim_id,
    p.gross_amount,
    p.net_amount,
    p.tax_amount,
    p.payment_date,

    -- Infos dossier
    c.risk_type,
    c.contract_id,
    c.company_id,
    c.policyholder_id,

    -- Assuré
    pol.last_name  as policyholder_last_name,
    pol.first_name as policyholder_first_name

from {{ ref('stg_prevcorp__payments') }} p
left join {{ ref('stg_prevcorp__claims') }} c
    on p.claim_id = c.claim_id
left join {{ ref('stg_prevcorp__policyholders') }} pol
    on c.policyholder_id = pol.policyholder_id
