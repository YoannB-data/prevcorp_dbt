select
    premium_id as cotisation_id,
    contract_id as contrat_id,
    cast(echeance_date as date) as echeance_date,
    cast(mnt_cotisation as decimal) as cotisation_montant,
    cast(dt_encaissement as date) as encaissement_date

from {{ ref('raw_premiums') }}
