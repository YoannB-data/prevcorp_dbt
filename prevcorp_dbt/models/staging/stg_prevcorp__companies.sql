select
    company_id,
    siret,
    trim(nom_entreprise)             as company_name,
    cast(dt_debut as date)           as start_date,
    cast(nullif(dt_fin, '') as date) as end_date,
    case
        when dt_fin is null or dt_fin = '' then true
        else false
    end                              as is_active
from {{ ref('raw_companies') }}
