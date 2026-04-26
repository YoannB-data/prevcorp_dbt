select
    payment_id as paiement_id,
    claim_id as dossier_id,
    cast(mnt_brut as decimal) as brut_montant,
    cast(mnt_pas as decimal) as pas_montant,
    cast(mnt_net as decimal) as net_montant,
    cast(dt_paiement as date) as paiement_date

from {{ ref('raw_payments') }}
