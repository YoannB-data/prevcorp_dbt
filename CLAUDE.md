# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PrevCorp is a synthetic dbt + DuckDB project modeling a French collective insurance ("prévoyance collective") company. It is designed as a PoC for an LLM text-to-SQL agent. All column names are intentionally in **French** to match the insurance domain, regulatory terminology, and LLM agent context.

## Setup

```bash
# Installer uv (une seule fois)
winget install astral-sh.uv

# Créer le venv et installer les dépendances
uv sync --all-groups

# Activer le venv
.venv\Scripts\activate
```

## Commands

All dbt commands must be run from the `prevcorp_dbt/` subdirectory:

```bash
cd prevcorp_dbt

# Load seed CSVs into DuckDB
dbt seed

# Run all models
dbt run

# Run a single model
dbt run --select <model_name>

# Run a layer
dbt run --select staging
dbt run --select intermediate
dbt run --select marts

# Run tests
dbt test

# Run tests for a single model
dbt test --select <model_name>

# Full refresh (recreate tables)
dbt run --full-refresh
```

To regenerate the synthetic CSV seeds:

```bash
python generate_dataset/generate.py
```

## Architecture

### Directory Layout

```
prevcorp_dbt/          ← dbt project root (run dbt commands from here)
  seeds/               ← raw_*.csv source data (Faker-generated)
  models/
    staging/           ← stg_prevcorp__* models
    intermediate/      ← int__* models
    marts/             ← dim__* and fct__* models
generate_dataset/      ← Python script that generates seeds
```

### Database

DuckDB (local file-based). The database file `prevcorp_dbt/dev.duckdb` is created automatically on `dbt seed`. No external warehouse needed. The `profiles.yml` must exist at `~/.dbt/profiles.yml` with profile name `prevcorp_dbt`, type `duckdb`, path `dev.duckdb`, target `dev`.

### Model Layers

**Staging (`stg_prevcorp__*`)**: One model per seed. Responsibilities: column renaming (UPPERCASE → French snake_case), type casting, NULL handling. No business logic.

**Intermediate (`int__*`)**: Enrichment joins across staging models. No grain changes. Designed for reuse by marts. Current models: `int__contrats_enrichis`, `int__cotisations_enrichies`, `int__dossiers_enrichis`, `int__paiements_enrichis`.

**Marts (`dim__*`, `fct__*`)**: End-user facing. Dimensions hold descriptive attributes; facts hold transactional/measurable data. These are what the LLM text-to-SQL agent queries.

### Naming Conventions

- **Seeds**: `raw_<entity>` (English entity names, UPPERCASE columns)
- **Staging**: `stg_prevcorp__<entité>` (French entity names, `entity_attribute` column pattern)
- **Intermediate**: `int__<entités_enrichies>`
- **Marts**: `dim__<entité>` / `fct__<entité>`
- **Columns**: `<entité>_<attribut>` (e.g., `contrat_type`, `assure_nom`, `dossier_numero`)

### Data Relationships

```
raw_segments       1 ──── n  raw_contracts
raw_contracts      n ──── n  raw_companies        (via raw_contract_companies)
raw_companies      1 ──── n  raw_policyholders
raw_policyholders  1 ──── n  raw_claims
raw_claims         1 ──── n  raw_payments
raw_claims         1 ──── n  raw_resources
raw_claims         1 ──── n  raw_beneficiaries
raw_contracts      1 ──── n  raw_premiums
```

Temporal coverage: 2022-01-01 to 2025-12-31.

## Key Files

- [schema.md](schema.md) — Full data dictionary with column descriptions and business rules
- [prevcorp_dbt/dbt_project.yml](prevcorp_dbt/dbt_project.yml) — dbt project config (profile, paths)
- [prevcorp_dbt/seeds/schema.yml](prevcorp_dbt/seeds/schema.yml) — Seed column type overrides (e.g., SIRET as varchar)
- [prevcorp_dbt/models/staging/_schema.yml](prevcorp_dbt/models/staging/_schema.yml) — Staging model docs and generic tests
- [generate_dataset/generate.py](generate_dataset/generate.py) — Synthetic data generator (Faker-based)


## Git / Commits

Un commit = une intention. Ne jamais regrouper des changements sans lien dans un seul commit.

Exemples de bons decoupages :
- Déplacement d'un modèle dans un autre domaine → 1 commit
- Ajout d'un nouveau modèle (staging + int + YAML) → 1 commit
- Nouveau mart (SQL + YAML) → 1 commit
- Correction sur un modèle existant → 1 commit
- Refacto Python → 1 commit

Format des messages : `type(scope): description courte`
Types courants : `feat`, `fix`, `refactor`, `docs`, `chore`

## Code Style

The project includes `black`, `pylint`, and `isort` in dependencies:
```bash
black .
isort .
pylint src/
```

## SQL / dbt Conventions

- All CTEs must be named with the prefix `cte_` (e.g., `cte_contrats`, `cte_gdp_delegation`).

### YAML schema files

One YAML file per model or seed, named `_<model_or_seed_name>.yml` (underscore prefix + exact name of the model/seed).

Examples:
- `prevcorp_dbt/models/intermediate/_int__contrats_enrichis.yml` → model `int__contrats_enrichis`
- `prevcorp_dbt/models/mart/_dim__assures.yml` → model `dim__assures`

Each file contains `version: 2` and a single entry under `models:` or `seeds:`. 
Aggregate multiple models/seeds into a shared `_schema.yml` only in `prevcorp_dbt/models/staging/`.

## Documentation dbt

### Philosophie

La doc ne décrit pas ce que le code fait — elle explique ce que la donnée représente,
pour qui, et avec quelles garanties. Si l'information peut être déduite en lisant le SQL, elle n'a pas sa place dans la description.

---

### Description de modèle
```yaml
description: |
  **Ce que c'est :** <sujet métier en une phrase>.
  **Grain :** Une ligne = <unité de granularité>.
  **À qui ça s'adresse :** <consommateurs — équipe, rapport, outil>.
  **Sources :** <origines clés et règles de gestion associées>.
  **Exceptions :** <exclusions, filtres, cas ambigus — si pertinent>.
```

---

### Description de colonne

1 à 3 phrases, sens métier uniquement. Jamais de références techniques (jointure, seed, type SQL).

**Colonne catégorielle** — expliquer le sens de chaque valeur si non évident.
Les valeurs exhaustives vont dans `accepted_values`, pas dans la description.
```yaml
- name: statut_contrat
  description: |
    Statut courant du contrat.
    ACTIF = en cours de validité. SUSPENDU = cotisations impayées. RESILIE = fin de contrat.
  tests:
    - accepted_values:
        arguments:
          values: ["ACTIF", "SUSPENDU", "RESILIE", "EN_ATTENTE"]
```

**Colonne numérique** — toujours préciser l'unité dans la description si le nom seul ne suffit pas.

**Colonne calculée** — décrire la règle en termes métier, pas la formule SQL.
```yaml
- name: taux_sinistralite_pct
  description: |
    Rapport entre sinistres réglés et cotisations perçues sur la période, en pourcentage.
    Un taux supérieur à 100 % indique un exercice déficitaire.
```

---

### Tests = documentation exécutable

Si une contrainte métier existe, il y a un test. Sans exception.

| Cas | Test |
|---|---|
| Toutes les PKs | `unique` + `not_null` |
| Toutes les FKs | `relationships` |
| Colonnes catégorielles | `accepted_values` |
<!-- | Montants et taux | `dbt_expectations` (plages cohérentes) | -->

---

### Ce qu'on ne met pas dans le YAML

- Formules SQL ou noms de colonnes techniques
- Explications de jointures
- Valeurs sentinelles techniques (ex : code `88887`)
- Listes exhaustives de valeurs dans `description` → `accepted_values`
- Bloc `meta:` — intégrer les infos utiles dans `description`

---

### Générer et consulter les docs
```bash
cd prevcorp_dbt
dbt docs generate
dbt docs serve --port 8080
```