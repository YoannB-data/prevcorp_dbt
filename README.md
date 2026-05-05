# prevcorp-dbt

Projet dbt de modélisation des données de **PrevCorp**, compagnie d'assurance prévoyance collective fictive.

Ce projet constitue la couche data du [prevcorp_agent](https://github.com/YoannB-data/prevcorp_agent), un assistant conversationnel permettant d'interroger en langage naturel les données d'un assureur prévoyance.

> Toutes les données sont 100% synthétiques. Aucune donnée réelle n'est utilisée.

---

## Contexte

PrevCorp est un dataset synthétique conçu pour ressembler fortement au SI d'un assureur prévoyance collective français : structure des contrats, règles métier, types de sinistres, logique de cotisation. Il est généré avec Faker et une logique métier custom qui encode les vraies règles du secteur.

L'objectif est de permettre le développement et l'évaluation d'un agent LLM text-to-SQL sur un domaine métier complexe, sans aucun risque juridique ou RGPD.

---

## Stack technique

- [dbt Core](https://docs.getdbt.com/) + [DuckDB](https://duckdb.org/) — transformation et stockage local
- [Faker](https://faker.readthedocs.io/) — génération du dataset synthétique
- Python 3.12+ / [uv](https://github.com/astral-sh/uv) — gestion de l'environnement

---

## Conventions

### Langue des colonnes
Les noms de colonnes dans les modèles dbt sont en **français**, contrairement à la convention 
dbt standard (anglais). Ce choix est délibéré : les données, les valeurs métier, 
la documentation et les utilisateurs finaux sont francophones. Aligner la langue des colonnes 
sur ce contexte garantit une cohérence complète du projet, de la seed au prompt de l'agent.

---

## Structure du projet

```
prevcorp-dbt/
├── generate_dataset/
│   └── generate.py          # Génération du dataset synthétique
├── seeds/                   # CSV bruts (export simulé d'un progiciel de gestion)
├── models/
│   ├── staging/             # Nettoyage, typage, renommage — 1 modèle par seed
│   ├── intermediate/        # Enrichissements et jointures — logique métier
│   └── marts/               # Modèles consommés par l'agent (dim__* et fct__*)
├── schema.md                # Schéma complet avec règles métier
└── README.md
```

---

## Architecture data

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

### Couche staging
Renommage des colonnes (MAJUSCULES → snake_case anglais), cast des types, NULL explicites. Aucune logique métier.

### Couche intermediate
Enrichissements par jointure sans changement de granularité. Conçue pour être réutilisée par plusieurs modèles marts. Dans ce POC, certains modèles intermediate sont consommés par un seul mart — ils documentent la logique métier et préparent une montée en complexité future.

### Couche marts
Modèles exposés à l'agent LLM. Dimensions (`dim__*`) : entités descriptives stables. Faits (`fct__*`) : événements mesurables dans le temps ou tables pont (factless facts) pour les relations M:N.

| Modèle | Description |
|---|---|
| `dim__segments` | Segments de marché (Boucherie, Enseignement, etc.) |
| `dim__entreprises` | Entreprises clientes |
| `dim__contrats` | Contrats, enrichis avec segment et nombre d'entreprises |
| `dim__assures` | Assurés / affiliés |
| `dim__beneficiaires` | Bénéficiaires de rentes DC, avec âge calculé |
| `fct__dossiers` | Dossiers sinistres enrichis (assuré, entreprise, segment, durée) |
| `fct__paiements` | Règlements effectués par dossier |
| `fct__cotisations` | Cotisations trimestrielles par contrat |
| `fct__ressources` | Ressources déclarées des assurés en invalidité |
| `fct__contrats_entreprises` | Table pont contrat ↔ entreprise (M:N), état courant |

---

## Volumes du dataset

| Table | Volume |
|---|---|
| raw_segments | 10 |
| raw_contracts | 500 |
| raw_companies | 500 |
| raw_contract_companies | ~418 |
| raw_policyholders | 5 000 |
| raw_claims | ~5 250 |
| raw_payments | ~144 000 |
| raw_premiums | ~4 400 |
| raw_resources | ~2 200 |
| raw_beneficiaries | ~1 600 |

Fenêtre temporelle : 2022-01-01 → 2025-12-31

---

## Installation et lancement

### Prérequis

- Python 3.12+
- [uv](https://github.com/astral-sh/uv)

### Setup

```bash
git clone https://github.com/YoannB-data/prevcorp-dbt.git
cd prevcorp-dbt

uv venv
source .venv/bin/activate  # Mac/Linux
# ou .venv\Scripts\activate  # Windows

uv sync
```

### Générer le dataset

```bash
python generate_dataset/generate.py
```

### Configurer dbt

Créer `~/.dbt/profiles.yml` :

```yaml
prevcorp_dbt:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: dev.duckdb
      threads: 1
```

### Lancer dbt

```bash
cd prevcorp_dbt

dbt seed        # Charger les CSV
dbt run         # Construire tous les modèles
dbt test        # Lancer les tests
```

---

## Sécurité et production

Ce projet utilise des données 100% synthétiques. Pour un déploiement sur données réelles, consulter [`ARCHITECTURE_SECURITY.md`](./ARCHITECTURE_SECURITY.md) qui décrit le pattern de production recommandé (couche `marts/ai_safe`, tests anti-PII, validation RSSI/DPO).

---

## Projet lié

- [prevcorp_agent](https://github.com/YoannB-data/prevcorp_agent) — agent LLM text-to-SQL qui consomme les modèles `marts/` de ce projet
