select
    ct.contract_id,
    ct.contract_number,
    ct.contract_type,
    ct.start_date,
    ct.end_date,
    ct.is_active,

    -- Segment
    s.segment_name,

    -- Nombre d'entreprises rattachées
    count(cc.company_id) as company_count

from {{ ref('stg_prevcorp__contracts') }} ct
left join {{ ref('stg_prevcorp__segments') }} s
    on ct.segment_id = s.segment_id
left join {{ ref('stg_prevcorp__contract_companies') }} cc
    on ct.contract_id = cc.contract_id
group by
    ct.contract_id,
    ct.contract_number,
    ct.contract_type,
    ct.start_date,
    ct.end_date,
    ct.is_active,
    s.segment_name
