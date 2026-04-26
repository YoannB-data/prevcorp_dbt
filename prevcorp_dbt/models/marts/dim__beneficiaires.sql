select
    beneficiaire_id,
    dossier_id,
    nom,
    prenom,
    naissance_date,
    date_diff('year', naissance_date, current_date) as age
    
from {{ ref('stg_prevcorp__beneficiaires') }}
