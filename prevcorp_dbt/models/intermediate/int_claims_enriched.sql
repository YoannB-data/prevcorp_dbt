select
    c.claim_id,
    c.claim_number,
    c.risk_type,
    c.leave_type,
    c.salary_amount,
    c.created_date,
    c.event_date,
    c.status_date,
    c.status_reason,
    c.is_open,
    c.non_activity_certificate_date,
    c.ss_certificate_date,
    c.contract_id,
    c.company_id,
    c.policyholder_id,

    -- Assuré
    p.last_name        as policyholder_last_name,
    p.first_name       as policyholder_first_name,
    p.country_code,

    -- Entreprise
    co.company_name,
    co.is_active       as company_is_active,

    -- Contrat et segment
    ct.contract_number,
    ct.contract_type,
    s.segment_name,

    -- Durée du dossier en jours
    case
        when c.is_open then datediff('day', c.created_date, current_date)
        else datediff('day', c.created_date, c.status_date)
    end                as claim_duration_days

from {{ ref('stg_prevcorp__claims') }} c
left join {{ ref('stg_prevcorp__policyholders') }} p
    on c.policyholder_id = p.policyholder_id
left join {{ ref('stg_prevcorp__companies') }} co
    on c.company_id = co.company_id
left join {{ ref('stg_prevcorp__contracts') }} ct
    on c.contract_id = ct.contract_id
left join {{ ref('stg_prevcorp__segments') }} s
    on ct.segment_id = s.segment_id
