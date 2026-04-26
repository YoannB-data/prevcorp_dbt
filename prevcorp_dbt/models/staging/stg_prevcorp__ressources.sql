select
    resource_id as ressource_id,
    claim_id as dossier_id,
    typ_ressource as ressource_type,
    cast(montant as decimal) as montant_mensuel,
    cast(dt_debut as date) as debut_date,
    cast(nullif(dt_fin, '') as date) as fin_date,
    case
        when dt_fin is null or dt_fin = '' then true
        else false
    end as est_en_cours
    
from {{ ref('raw_resources') }}
