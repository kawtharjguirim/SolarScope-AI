# SolarScope AI — inventaire des données du projet

Phase 1 : analyse du dépôt réel. Aucun fichier n'a été modifié ni réentraîné pour établir cet inventaire.

## 1. Données d'entrée (observations NASA POWER)

| Fichier | Site | Lignes | Colonnes | Période |
|---|---|---|---|---|
| `donnees/Monastir.csv` | Monastir (35,78 ; 10,83) | 4 564 | `date`, `ALLSKY_SFC_SW_DWN`, `CLRSKY_SFC_SW_DWN`, `T2M`, `T2M_MAX`, `T2M_MIN`, `RH2M`, `WS2M`, `PS`, `PRECTOTCORR`, `CLOUD_AMT` | 2014-01-01 → 2026-06-30 |
| `donnees/Tamanrasset.csv` | Tamanrasset (22,79 ; 5,52) | 4 564 | idem | idem |
| `donnees/Dakar.csv` | Dakar (14,69 ; −17,44) | 4 564 | idem | idem |

Source : NASA POWER (API journalière, sans compte). Valeurs manquantes codées `-999` : aucune dans les trois fichiers, et aucune date manquante.

## 2. Résultats d'expériences (fichiers CSV exportés par les notebooks)

| Fichier | Axe | Lignes | Colonnes | Contenu |
|---|---|---|---|---|
| `axe1_resume.csv` | 1 · Ridge | 3 (un par site) | `site`, `lat`, `lon`, `n_app`, `n_test`, `kappa`, `iter_pred`, `iter_obs`, `rmse_ridge`, `rmse_naif`, `mae_ridge`, `mae_naif` | Vitesse de descente, RMSE/MAE du ridge et du naïf |
| `axe2_resume.csv` | 2 · Quantiles | 3 | `site`, `lat`, `lon`, `n_app`, `n_test`, `pinball_q10/q50/q90`, `couv_q10`, `couv_q90`, `couv_interval`, `largeur`, `croisements_avant` | Pinball, couverture, largeur, croisements |
| `axe3_resume.csv` | 3 · Contraintes | 3 | `site`, `n_app`, `n_test`, `violation_train`, `iter_AL`, `croisements_apres`, `sorties_bornes_apres`, `pinball_moyen`, `couv_interval`, `largeur`, `jours_borne_active` | Après contraintes (lagrangien augmenté) |
| `axe4_resume.csv` | 4 · R3 CQR | 3 | `site`, `n_app`, `n_test`, `piste`, `couv_brut`, `couv_gauss`, `couv_cqr_moy`, `couv_cqr_ecart`, `largeur_brut`, `largeur_cqr_moy`, `largeur_cqr_ecart` | Couverture moyenne et écart-type sur 5 graines |
| `resultats_groupe.csv` | Format commun | 3 | 23 colonnes (voir cahier) | Synthèse par site ; `zone_carte` et `zone_nasa` identiques |

## 3. Fichiers présents mais sans sortie exportée

| Élément demandé | Statut | Où le trouver |
|---|---|---|
| Prédictions Q10 / Q50 / Q90 par jour | **Absent en fichier.** L'application les recalcule (même algorithme que l'axe 2). Les couvertures recalculées (78,7 % à Monastir) correspondent à `axe2_resume.csv`. | Calcul dans `solar_core.py` |
| Modèles sérialisés | **Absents.** Les modèles sont des vecteurs de poids recalculés à la volée. | — |
| Historiques de convergence (axes 1, 2, 3) | **Absents en fichier.** Les courbes ont été affichées dans les notebooks, sans sauvegarde. | Sorties des notebooks |
| Résultats par graine (CQR, 5 graines) | **Absents du CSV.** Seules la moyenne et l'écart-type sont exportés. | Sortie du notebook `axe4_cqr` |
| Calibration (6 mois, 1 an, 2 ans), ACI, couverture gaussienne par saison | **Absents en fichier.** Valeurs visibles seulement dans les sorties du notebook (Monastir). | `results_data.py` (saisie manuelle) |
| Sorties de l'axe 2 (F\*, smoothing ε, mini-lots) | **Absentes en fichier.** | `results_data.py` (saisie manuelle) |
| Sorties de l'axe 3 (dual, KKT, violations) | **Absentes en fichier**, sauf les résumés CSV. | `results_data.py` (saisie manuelle) |
| Figures enregistrées | **Absentes.** Les figures sont affichées dans les notebooks, sans fichier. | — |

## 4. Fichiers de code et de rapport

- Scripts : `axe1_ridge.py`, `axe2_quantile.py`, `axe3_contraintes.py`, `axe4_cqr.py`
- Notebooks : `axe1_ridge.ipynb` à `axe4_cqr.ipynb`, et copies dans `notebook/`
- Rapport : `rapport_sujet_C.tex`, `questions_communes.md`
- Application : `app.py`, `app_pages/`, `solar_core.py`, `results_data.py`, `auth.py`, `ui.py`
- Comptes utilisateurs : `users.json` (mots de passe hachés)
- Prototype visuel : `template_solarscope.html`

## 5. Ce qui manque pour respecter le cahier des charges

1. **Export des historiques de convergence et des prédictions** : exécuter une fois les scripts d'axe en ajoutant la sauvegarde (CSV). Cela ne réentraîne pas de modèle nouveau, mais répète les calculs.
2. **Export par graine** de l'axe 4 et des sorties de calibration / ACI.
3. **Plotly** n'est pas installé dans l'environnement de l'application.
4. **Google** : aucune authentification OAuth configurée, donc le bouton n'est pas affiché.
5. **Valeurs saisies à la main** dans `results_data.py` : à remplacer par des fichiers exportés, pour respecter la règle « ne jamais figer de métriques ».

## 6. Décisions à prendre avant la phase 2

- Autoriser l'export des historiques (relance des scripts d'axe, sans changer les paramètres).
- Accepter Plotly (installation dans le `.venv`) ou rester sur les graphiques Streamlit natifs.
- Renommer `app_pages/` en `pages/` avec numérotation, comme le cahier le suggère.
