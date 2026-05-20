{{ config(materialized='table') }}

SELECT range::DATE AS date_day
FROM range(DATE '2020-01-01', DATE '2030-12-31', INTERVAL '1 day')