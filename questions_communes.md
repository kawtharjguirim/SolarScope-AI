# Questions communes — réponses

Sites : Monastir (BSh), Tamanrasset (BWh), Dakar (BSh). Chiffres issus des notebooks des axes 1 à 4 (test 2024–2026, 912 jours).

## 1. Classement des sites du plus facile au plus difficile

Critère retenu : la prévision ponctuelle (RMSE du ridge, axe 1), puis la prévision de la médiane et les intervalles.

| Site | RMSE ridge | RMSE naïf | Gain vs naïf | Médiane (pinball q50) | Largeur brute |
|---|---|---|---|---|---|
| Tamanrasset | 0,709 | 0,803 | 12 % | 0,239 | 1,44 |
| Dakar | 0,790 | 0,951 | 17 % | 0,266 | 1,55 |
| Monastir | 0,939 | 1,204 | 22 % | 0,323 | 1,85 |

**Classement : Tamanrasset (le plus facile) < Dakar < Monastir (le plus difficile).** Le classement est le même pour le ridge, pour la médiane et pour la largeur de l'intervalle.

Deux réserves :
- Le **gain** vs naïf est le plus élevé à Monastir, qui est pourtant le site le plus difficile en valeur absolue. Le ridge y corrige donc davantage l'erreur naïve, sans pour autant la rendre faible.
- La **largeur** est exprimée en kWh/m²/j, donc elle dépend du niveau moyen du rayonnement. Une largeur relative (divisée par la moyenne) serait plus juste pour comparer les sites ; nous ne l'avons pas calculée.

Le classement **ne reste pas le même** pour la fiabilité des intervalles (axe 4) : après calibration CQR, la couverture à 80 % vaut 81,1 % à Monastir, 83,5 % à Dakar et seulement 76,7 % à Tamanrasset. Tamanrasset est donc le site le plus facile à prévoir, mais le moins bien calibré.

## 2. La difficulté d'optimisation suit-elle la difficulté de prévision ?

**Non, pas de façon simple.**

- Conditionnement κ du ridge (axe 1) : Monastir 564, Tamanrasset 462, Dakar 398. Dakar a le κ le plus faible, donc la borne théorique la plus favorable.
- Itérations observées pour diviser l'écart par 10⁶ au pas 1/L : Tamanrasset 703, Monastir 858, **Dakar 1 319**.

Dakar, pourtant le mieux conditionné, est le site où la descente est la plus lente. Le rapport observé/prédit vaut 0,22 à Monastir et Tamanrasset, mais 0,48 à Dakar : la borne en κ ne suffit pas à prédire la vitesse d'un site à l'autre. La cause probable est la répartition du spectre, qui n'est pas résumée par κ seul ; nous ne l'avons pas démontrée.

Pour le lagrangien augmenté (axe 3), le nombre d'itérations externes est de 5, 5 et 3 : il n'est pas corrélé à la difficulté de prévision.

## 3. L'hypothèse de D.1 est-elle confirmée ? Qu'est-ce qui a surpris ?

**Nous ne pouvons pas répondre à la première partie** : aucune hypothèse de D.1 n'a été rédigée et datée avant les essais. Le groupe doit inscrire son hypothèse (quel site sera le plus difficile, et pourquoi) avant de conclure. À défaut, cette réponse ne peut pas être présentée comme une confirmation.

Ce qui a surpris, par rapport à ce que suggère le climat :
- **Dakar** (BSh, humide en été) est plus lent à optimiser que son κ ne le laisse prévoir (voir question 2).
- **Tamanrasset** (BWh, désertique), le plus facile à prévoir, est le site où la calibration des intervalles est la moins fiable (couverture 76,7 %). Un climat stable rend la prévision simple, mais la calibration sensible au décalage entre calibration et test.
- Sans contrainte, le quantile 0,9 dépasse le ciel clair sur **71 %** des jours à Monastir : le modèle linéaire est physiquement incohérent (axe 3).

## 4. Quelle méthode recommander à un exploitant pour un nouveau site ?

Recommandation provisoire, fondée sur trois sites seulement :

1. **Prévision ponctuelle** : ridge (λ = 10⁻²) avec les variables de l'axe 1. Il bat le naïf sur les trois sites (de 12 % à 22 % de RMSE en moins).
2. **Quantiles** : régression quantile lissée (Moreau, ε = 10⁻³) résolue par Newton amorti. C'est la méthode la plus rapide ; le sous-gradient projeté donne une précision comparable mais demande plus d'itérations.
3. **Intervalles** :
   - **Climat stable et ensoleillé (désert, BWh)** : ACI en ligne, car la calibration statique peut dériver.
   - **Climat plus variable (steppe, BSh)** : CQR avec au moins un an de calibration récente. Elle couvre 81 % à Monastir et 83,5 % à Dakar.
4. **Contraintes physiques** : les bornes de ciel clair doivent être imposées. Le lagrangien augmenté converge en quelques itérations ; le dual projeté ne converge pas en pratique (constante de Lipschitz du dual L_d ≈ 1,2·10⁷).

Limites : trois sites, deux du même type climatique (BSh), une seule année de test. Ces conclusions doivent être confirmées sur davantage de sites avant d'être généralisées à un nouveau site.
