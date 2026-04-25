select
    contract_id,
    num_contrat                              as contract_number,
    segment_id,
    typ_contrat                              as contract_type,
    cast(dt_adhesion as date)                as start_date,
    cast(nullif(dt_resiliation, '') as date) as end_date,
    case
        when dt_resiliation is null or dt_resiliation = '' then true
        else false
    end                                      as is_active
from {{ ref('raw_contracts') }}
