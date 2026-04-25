select
    premium_id,
    contract_id,
    cast(mnt_cotisation as decimal) as premium_amount,
    cast(dt_encaissement as date)   as collection_date,
    cast(echeance_date as date)     as due_date
from {{ ref('raw_premiums') }}
