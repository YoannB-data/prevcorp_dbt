select
    ressource_id,
    dossier_id,
    ressource_type,
    montant_mensuel,
    debut_date,
    fin_date,
    est_en_cours
from {{ ref('stg_prevcorp__ressources') }}
