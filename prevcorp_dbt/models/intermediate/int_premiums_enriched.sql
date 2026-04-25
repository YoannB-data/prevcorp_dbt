select
    pr.premium_id,
    pr.contract_id,
    pr.premium_amount,
    pr.collection_date,
    pr.due_date,

    -- Contrat
    ct.contract_number,
    ct.contract_type,
    ct.is_active      as contract_is_active,

    -- Segment
    s.segment_name

from {{ ref('stg_prevcorp__premiums') }} pr
left join {{ ref('stg_prevcorp__contracts') }} ct
    on pr.contract_id = ct.contract_id
left join {{ ref('stg_prevcorp__segments') }} s
    on ct.segment_id = s.segment_id
