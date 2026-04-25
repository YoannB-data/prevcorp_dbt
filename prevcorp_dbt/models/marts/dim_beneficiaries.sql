select
    beneficiary_id,
    claim_id,
    last_name,
    first_name,
    birth_date,
    date_diff('year', birth_date, current_date) as age
from {{ ref('stg_prevcorp__beneficiaries') }}
