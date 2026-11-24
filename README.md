# SolarScope AI

Plateforme interactive de **prévision probabiliste du rayonnement solaire** en Afrique (Monastir, Tamanrasset, Dakar).
Elle présente les résultats réels du projet *Probabilistic Solar Energy Forecasting in Africa* (Sujet C) :
quantiles Q10, Q50, Q90, évaluation de la couverture, convergence des algorithmes et contraintes physiques.

## Installation

Depuis le dossier du projet, dans PowerShell :

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements_app.txt
```

## Lancement

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

L'application s'ouvre sur `http://localhost:8501`. Le tableau de bord est accessible directement, sans connexion.

## Structure

```
SolarScope AI/
├── app.py                   # point d'entrée, navigation, sélecteur de site
├── pages/
│   ├── home.py              # accueil
│   ├── 1_Vue_generale.py    # KPI, carte, comparaison des sites
│   ├── 2_Prevision.py       # Q10 / Q50 / Q90 vs observé, zoom, filtre de période, export CSV
│   ├── 3_Sites_climat.py    # carte, climat, performance par site
│   ├── 4_Evaluation.py      # brut, gaussien, CQR : couverture, largeur, graines
│   ├── 5_Optimisation.py    # convergence des axes 1 à 3
│   ├── 6_Contraintes.py     # violations avant / après contraintes
│   └── 7_A_propos.py        # projet, méthodologie, inventaire des fichiers
├── components/              # thème (theme.py) et graphiques Plotly (charts.py)
├── services/
│   ├── data_loader.py       # lecture et validation des fichiers (aucune valeur saisie à la main)
│   ├── analysis.py          # indicateurs calculés à partir des données
│   └── metrics.py           # couverture, largeur, pinball, RMSE, croisements, bornes
├── donnees/                 # observations NASA POWER (un CSV par site)
├── exports/                 # prédictions et historiques écrits par les scripts d'axe
├── axe1_ridge.py … axe4_cqr.py   # expériences (écrivent les *_resume.csv et exports/)
├── *_resume.csv             # résultats par site des axes 1 à 4
├── resultats_groupe.csv     # format commun du groupe
└── DATA_INVENTORY.md        # inventaire des données du projet
```

## Régénérer les sorties

Les pages lisent les fichiers de `exports/`. Pour les recréer (sans modifier les paramètres ni les modèles) :

```powershell
.\.venv\Scripts\python.exe axe1_ridge.py
.\.venv\Scripts\python.exe axe2_quantile.py
.\.venv\Scripts\python.exe axe3_contraintes.py
.\.venv\Scripts\python.exe axe4_cqr.py
```

Chaque script refait ses calculs (environ une à deux minutes au total).

## Principes de données

- Aucune observation, prédiction ni métrique n'est saisie à la main : tout est lu depuis `donnees/`, `exports/` ou les `*_resume.csv`.
- Un fichier absent affiche un message *« Résultats expérimentaux non disponibles »* au lieu d'une valeur inventée.
- Les indicateurs calculés dans l'application (couverture, largeur, pinball, croisements) sont recalculés à partir des prédictions et sont signalés comme tels.
- Les sites sont identifiés par leur nom, avec leurs coordonnées réelles (`resultats_groupe.csv`).

## Limites connues

- **« Se souvenir de moi »** : non implémenté. Streamlit n'offre pas de stockage persistant côté navigateur sans composant tiers.
- **Historiques d'optimisation** : exportés pour Monastir seulement (axes 1 et 3, et le sous-gradient de l'axe 2 pour τ = 0,5).
- **Calibration CQR et ACI** : exportées pour Monastir seulement. La couverture par graine est disponible pour les trois sites.
- **Analyse de régularisation** (λ ∈ {0 ; 10⁻³ ; 10⁻² ; 10⁻¹}) et historiques des quantiles Q10 et Q90 : non exportés, signalés comme tels dans l'application.
- **Garantie CQR** : non vérifiée à Tamanrasset (couverture 76,7 %, calibration 2023 non représentative du test).

## Crédits

Projet Sujet C — Optimisation pour le Machine Learning, 5e année Data Sciences et IA, École Supérieure Privée d'Ingénieurs de Monastir (ESPRIM).
Données : NASA POWER (API journalière, licence CC BY 4.0).
