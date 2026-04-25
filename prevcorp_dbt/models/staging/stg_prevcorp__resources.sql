select
    resource_id,
    claim_id,
    typ_ressource                      as resource_type,
    cast(montant as decimal)           as monthly_amount,
    cast(dt_debut as date)             as start_date,
    cast(nullif(dt_fin, '') as date)   as end_date,
    case
        when dt_fin is null or dt_fin = '' then true
        else false
    end                                as is_active
from {{ ref('raw_resources') }}
