select
    company_id as entreprise_id,
    siret,
    trim(nom_entreprise) as entreprise_nom,
    cast(dt_debut as date) as debut_date,
    cast(nullif(dt_fin, '') as date)  as fin_date,
    case
        when dt_fin is null or dt_fin = '' then true
        else false
    end as est_en_cours
    
from {{ ref('raw_companies') }}
