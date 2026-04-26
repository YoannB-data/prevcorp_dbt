select
    entreprise_id,
    siret,
    entreprise_nom,
    debut_date,
    fin_date,
    est_en_cours
    
from {{ ref('stg_prevcorp__entreprises') }}
