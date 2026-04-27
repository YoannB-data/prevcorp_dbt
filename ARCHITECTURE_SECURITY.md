# Architecture Sécurité — PrevCorp Agent

## Présentation

Ce document décrit le dispositif de sécurité recommandé pour déployer un agent LLM text-to-SQL sur les données d'un assureur prévoyance en environnement de production.

Le projet PrevCorp utilise un dataset 100% synthétique, ce qui élimine tout risque RGPD ou contractuel dans sa version actuelle. Ce document a pour objet de démontrer la maîtrise des enjeux de sécurité qui se poseraient sur des données réelles, et de formaliser le pattern d'architecture à adopter dans ce contexte.

---

## Problématique

Un agent LLM text-to-SQL génère et exécute des requêtes SQL sur une base de données, puis transmet les résultats à un modèle de langage hébergé par un tiers (ici, l'API Anthropic). Sans dispositif de filtrage, cet agent peut exposer des données personnelles à un service externe — ce qui soulève trois enjeux majeurs :

**Conformité RGPD** — La transmission de données nominatives (noms, salaires, adresses) à un prestataire tiers constitue un traitement de données personnelles soumis au RGPD.
Une base légale, un encadrement contractuel et une analyse d'impact peuvent être requis.

**Sécurité des données** — Les données de prévoyance collective sont sensibles : elles incluent des informations médicales, financières et personnelles sur les assurés.
Leur exposition doit être strictement contrôlée.

**Risque d'identification indirecte** — Même une donnée agrégée peut permettre d'identifier un individu si le groupe de référence est trop restreint (principe du k-anonymat).

---

## Architecture cible

### Vue d'ensemble

```
SI Assureur · progiciel de gestion
       │
       ▼
dbt · staging → intermediate
       │
       ├──► marts/core/       ← accès interdit à l'agent LLM
       │                        (données nominatives complètes)
       │
       └──► marts/ai_safe/    ← seule couche exposée à l'agent
                │               (données agrégées et anonymisées)
                │
                ▼
           Agent LLM ──► API Claude (Anthropic)
```

### Couche `marts/core/`

Contient les données complètes, nominatives, à la granularité individuelle.
Accessible uniquement par les outils internes (reporting, extractions métier).
**Cette couche n'est jamais exposée à l'agent LLM.**

### Couche `marts/ai_safe/`

Contient uniquement des agrégats et des données anonymisées, construits à partir de `marts/core/`. C'est la seule couche dont le schéma est injecté dans le prompt de l'agent.

Exemples de modèles `ai_safe/` :

| Modèle | Grain | Données exposées |
|---|---|---|
| `agg__dossiers_par_contrat` | 1 ligne = 1 contrat | COUNT, taux de sinistralité |
| `agg__paiements_par_risque` | 1 ligne = 1 type de risque | SUM, AVG des montants |
| `agg__cotisations_par_segment` | 1 ligne = 1 segment | Totaux trimestriels |

**Règle de k-anonymat** : aucun agrégat ne peut porter sur moins de 5 individus, afin d'éviter toute identification indirecte.

---

## Garanties techniques

La séparation `core` / `ai_safe` doit être garantie techniquement, pas seulement documentée. Deux mécanismes sont recommandés.

### Tests dbt anti-PII (Personally Identifiable Information — données personnelles identifiantes)

Des tests dbt custom sont implémentés sur chaque modèle `ai_safe/` pour bloquer le pipeline si une donnée nominative est accidentellement exposée :

```yaml
- name: agg__dossiers_par_contrat
  tests:
    - no_column_named:
        forbidden_columns: ["nom", "prenom", "adresse", "siret", "naissance_date"]
    - no_row_count_below:
        min_rows: 5
```

Ces tests s'exécutent à chaque `dbt build` et bloquent le déploiement en cas d'anomalie.

### Restriction du schema_loader

Le composant `schema_loader.py` de l'agent est configuré pour lire exclusivement les métadonnées des modèles `marts/ai_safe/` dans le `manifest.json` dbt.
Les tables `marts/core/` sont invisibles de l'agent, même si elles existent
dans la base.

---

## Processus de validation avant déploiement

Tout déploiement sur données réelles doit faire l'objet d'une validation formelle :

1. **Audit RSSI (Responsable de la Sécurité des Systèmes d'Information)** — Validation que les flux de données vers l'API externe respectent la politique de sécurité de l'organisation.

2. **Avis DPO (Data Protection Officer — Délégué à la Protection des Données)** — Confirmation de la conformité RGPD : base légale du traitement, principe de minimisation, encadrement de la sous-traitance.

3. **Data Processing Agreement** — Vérification et signature d'un accord de traitement des données avec Anthropic, précisant les conditions de rétention et d'utilisation des données transmises.

4. **PIA (Privacy Impact Assessment — Analyse d'Impact relative à la Protection des Données)** — Requis si le traitement est susceptible d'engendrer un risque élevé pour les droits et libertés des personnes.

---

## Checklist de mise en production

- [ ] Couche `marts/ai_safe/` créée avec modèles agrégés uniquement
- [ ] Tests anti-PII implémentés et passants sur l'ensemble des modèles `ai_safe/`
- [ ] `schema_loader.py` configuré pour n'exposer que `ai_safe/`
- [ ] Audit RSSI réalisé et validé
- [ ] Avis DPO obtenu
- [ ] Data Processing Agreement signé avec Anthropic
- [ ] PIA réalisé si applicable
- [ ] Tests d'intrusion sur le prompt (prompt injection visant à contourner
      la couche `ai_safe/`)
- [ ] Revue de sécurité des logs (vérification qu'aucune donnée nominative
      n'est tracée en clair)

---

## Évolution possible du projet PrevCorp

Le dataset PrevCorp étant synthétique, la couche `marts/ai_safe/` n'est pas
implémentée dans la version actuelle. Elle peut être ajoutée en quelques heures de travail pour démontrer concrètement le pattern sur un exemple fonctionnel, sans impliquer de données réelles.
