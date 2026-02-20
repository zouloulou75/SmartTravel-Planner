# Travel ML Project

Prototype d'assistant intelligent de voyage combinant:
- Recommandation personnalisee de destinations (IntTravel)
- Generation automatique d'itineraires (TravelPlanner)

## Objectifs

### Module de recommandation (IntTravel)
- Construire un modele d'interactions utilisateur-POI a partir de donnees reelles
- Recommander une liste Top-N de destinations pour un utilisateur
- Integrer des informations contextuelles (temps, region, transport, etc.)
- Comparer une approche de base (popularite) vs personnalisee
- Evaluer la qualite via des metriques de ranking

Resultat attendu: une liste ordonnee de destinations recommandees par utilisateur.

### Module de planification (TravelPlanner)
- Analyser une requete de voyage en langage naturel
- Generer un itineraire multi-jours avec activites
- Respecter des contraintes (duree, preferences, budget, etc.)
- Produire un plan combine avec la recommandation
- Evaluer coherence et pertinence

Resultat attendu: un itineraire complet genere a partir d'une requete.

### Objectif global
Concevoir un prototype end-to-end: recommander des destinations, puis generer un itineraire adapte a l'utilisateur.

## Architecture (vue d'ensemble)

Le projet est organise en couches pour separer les preoccupations:
- API (FastAPI) expose les endpoints
- Services orchestrent la logique metier
- ML contient les modeles et pipelines
- Data gere l'ingestion, le nettoyage et les features

Flux type:
1) Requete utilisateur -> API
2) Service Reco -> modele IntTravel -> Top-N destinations
3) Service Planning -> modele TravelPlanner -> itineraire multi-jours
4) API renvoie un plan complet

## Structure du projet

```
backend/
  app/
    main.py                # Point d'entree FastAPI
    api/
      v1/
        routes/
          health.py        # Route de sante
    core/                  # Configuration et utilitaires
    models/                # Modeles domain / ORM
    schemas/               # Schemas Pydantic
    services/              # Logique metier (reco, planning)
    ml/                    # Modeles ML (IntTravel, TravelPlanner)
    pipelines/             # ETL / entrainement
  tests/
frontend/
  (React + Vite)
data/
  raw/
  processed/
  features/
```

## Endpoints initiaux

- `GET /api/v1/health`

## Lancer en local

### Backend
```
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```
cd frontend
npm install
npm run dev
```
