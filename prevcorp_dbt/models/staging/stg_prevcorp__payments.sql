select
    payment_id,
    claim_id,
    cast(mnt_brut as decimal)  as gross_amount,
    cast(mnt_net as decimal)   as net_amount,
    cast(mnt_pas as decimal)   as tax_amount,
    cast(dt_paiement as date)  as payment_date
from {{ ref('raw_payments') }}
