# Méta-gouvernance — Auto-contestation et détection des erreurs non détectées

**Statut :** FONDATION ARCHITECTURALE — principe directeur et protocole de gouvernance
**Date d'établissement :** 12 septembre 2026
**Portée :** système autonome d'intelligence de contenu

---

## 1. Principe fondateur

Un système robuste ne doit pas seulement apprendre, produire des décisions et vérifier ses résultats. Il doit disposer d'une capacité permanente à rechercher **pourquoi ce qu'il croit pourrait être faux, incomplet, mal mesuré ou devenu invalide**.

> **L'intelligence utile du système ne se mesure pas uniquement à sa capacité à produire une réponse correcte, mais à sa capacité à rechercher activement les conditions dans lesquelles sa propre réponse pourrait être incorrecte.**

La méta-gouvernance protège donc les trois fondations du système :

1. **POURQUOI / VALEUR** — sommes-nous toujours en train de résoudre le bon problème et de mesurer la bonne valeur ?
2. **RÈGLES / CONNAISSANCE** — nos règles, hypothèses et connaissances sont-elles réellement justifiées, applicables et toujours valides ?
3. **SYSTÈME / ARCHITECTURE** — notre manière de produire les décisions est-elle elle-même correcte, complète et suffisamment robuste ?

La méta-gouvernance ne doit pas être une étape ponctuelle. C'est une **fonction permanente de contestation**.

---

## 2. Le problème critique : l'erreur non détectée

Une erreur connue peut être corrigée. Une erreur inconnue ou non détectée peut contaminer :

**HYPOTHÈSE → DONNÉES → EXPÉRIMENTATION → CONNAISSANCE → DÉCISION → ACTION → VALEUR**

Le risque majeur est donc :

> **croire que le système fonctionne parce que les contrôles existants ne détectent pas ce qui est réellement défaillant.**

La gouvernance doit chercher prioritairement les **erreurs non détectées**, les angles morts et les hypothèses jamais réellement mises à l'épreuve.

---

## 3. Question permanente de contestation

Toute connaissance, décision importante, évolution architecturale ou conclusion significative doit pouvoir être confrontée à :

> **« Je pense que X est vrai. Qu'est-ce qui pourrait démontrer que X est faux, incomplet, mal mesuré, mal causalement attribué ou devenu invalide ? »**

Puis :
- Qu'avons-nous supposé sans le tester ?
- Qu'est-ce que nos tests ne couvrent pas ?
- Quelles observations contrediraient notre conclusion ?
- Quelles alternatives expliquent également le résultat ?
- Qu'est-ce qui pourrait créer un faux signal de réussite ?
- Dans quelles conditions cette connaissance cesse-t-elle d'être valable ?
- Qu'est-ce qui pourrait avoir changé depuis sa validation ?
- Quel coût, risque ou opportunité avons-nous oublié ?
- Quelle décision différente deviendrait rationnelle si notre hypothèse principale était fausse ?

Une conclusion sans condition d'invalidation connue est une conclusion **incomplètement spécifiée**.

---

## 4. Boucle de méta-gouvernance

**HYPOTHÈSE / CONNAISSANCE → ATTENTE → OBSERVATION → ÉCART → CONTESTATION → INVESTIGATION → NOUVELLE HYPOTHÈSE → EXPÉRIMENTATION → RÉSULTAT → CORRECTION OU CONFIRMATION → RE-TEST → VERDICT**

Cette boucle complète la boucle d'apprentissage :

**INCONNU → OBSERVATION → INFORMATION → HYPOTHÈSE → EXPÉRIMENTATION → CONNAISSANCE → DÉCISION → ACTION → VALEUR**

Le système doit aussi demander :

> **« Qu'est-ce que nous aurions pu apprendre mais que notre dispositif actuel ne permet pas de voir ? »**

---

## 5. Six familles d'angles morts obligatoires

### A. Erreur de problème / finalité

Vérifier que le système résout toujours le problème qui crée réellement de la valeur et que les métriques restent de bons proxys de cette valeur.

### B. Erreur de représentation

Vérifier que les données, variables, catégories et signaux représentent suffisamment le monde réel, y compris les populations, périodes et conditions absentes des tests.

### C. Erreur causale

Rechercher les causes alternatives, facteurs cachés, coïncidences et biais expérimentaux avant d'attribuer un résultat à une cause.

### D. Erreur de généralisation

Une règle vraie dans un domaine limité ne devient pas automatiquement universelle. Chaque connaissance importante doit préciser son domaine de validité, ses conditions nécessaires, son niveau de confiance et ses conditions d'invalidation.

### E. Erreur d'architecture

Le système lui-même peut être la source du problème : composant manquant, dépendance critique, interaction non prévue, garde-fou contournable ou hypothèse architecturale jamais testée.

### F. Erreur économique / valeur nette

Évaluer la valeur réellement créée après data, compute, infrastructure, maintenance, supervision, temps humain, coût d'opportunité et risques. Une capacité techniquement meilleure peut être économiquement moins bonne.

---

## 6. Anomalies comme mécanisme de découverte

**ATTENTE → OBSERVATION → ÉCART → ANOMALIE → INVESTIGATION → NOUVELLE CONNAISSANCE**

Une anomalie significative doit pouvoir déclencher une investigation lorsqu'elle est répétée, importante, contradictoire avec une connaissance critique, observée dans une zone jamais testée ou révélatrice d'un changement de contexte.

Une anomalie ne doit pas être supprimée automatiquement parce qu'elle dégrade une métrique.

---

## 7. Tests adversariaux et recherche active de réfutation

Pour toute connaissance ou architecture critique :

1. formuler la thèse ;
2. identifier les hypothèses nécessaires ;
3. définir les conditions de falsification ;
4. tester sur des conditions différentes ;
5. rechercher des explications alternatives ;
6. reproduire ;
7. rechercher un contre-exemple ;
8. corriger si nécessaire ;
9. re-casser ;
10. rendre un verdict **PASS / FAIL / BLOCKED**.

**BLOCKED n'est jamais PASS.** L'absence de preuve n'est pas une preuve de validité.

---

## 8. Provenance de la confiance

Toute connaissance critique doit pouvoir répondre à : **Pourquoi le croyons-nous ?**

Chaîne minimale :

**CONNAISSANCE → SOURCE → OBSERVATION → HYPOTHÈSE → EXPÉRIENCE → RÉSULTAT → TESTS CONTRADICTOIRES → NIVEAU DE PREUVE → DOMAINE DE VALIDITÉ → CONDITIONS D'INVALIDATION**

---

## 9. Détection du drift

Une connaissance peut devenir invalide sans avoir été fausse lors de sa validation. Surveiller les changements de données, comportement du monde, coûts, contraintes, objectifs, interactions internes, performances et anomalies.

Question permanente : **« Est-elle encore vraie ici et maintenant ? »**

---

## 10. Proxy drift et optimisation perverse

Confronter périodiquement :

**OBJECTIF RÉEL ↔ PROXY MESURÉ ↔ RÉSULTAT RÉEL ↔ COÛTS ↔ RISQUES**

Si le proxy diverge de l'objectif réel, l'optimisation doit être suspendue ou requalifiée.

---

## 11. Coût d'opportunité et principe d'arrêt

Prévoir des conditions permettant d'abandonner une voie lorsque l'hypothèse est réfutée, l'amélioration est absente, le coût disproportionné, le risque excessif, les données insuffisantes, la valeur nette négative ou une meilleure alternative disponible.

Le système doit éviter le biais des coûts irrécupérables.

---

## 12. Niveaux de contestation

1. **Décision** — cette décision est-elle justifiée ?
2. **Règle** — la règle utilisée est-elle valide ?
3. **Hypothèse** — l'hypothèse sous-jacente est-elle correcte ?
4. **Architecture** — le système qui produit et vérifie la connaissance est-il fiable ?
5. **Finalité** — résolvons-nous toujours le bon problème et créons-nous réellement la valeur recherchée ?

Le niveau supérieur doit pouvoir contester le niveau inférieur.

---

## 13. Déclencheurs obligatoires

Auto-contestation au minimum :
- avant promotion d'une connaissance ou stratégie ;
- avant modification architecturale critique ;
- après anomalie significative ;
- après dégradation persistante ;
- lors d'un changement de données ou d'environnement ;
- lors d'un changement d'objectif ou de métrique ;
- avant augmentation importante d'autonomie ;
- après échec critique ;
- périodiquement même en l'absence d'anomalie.

L'absence d'anomalie ne prouve pas l'absence de problème.

---

## 14. Registre des contestations

Les contestations importantes doivent être conservées dans la mémoire expérimentale avec : objet, thèse initiale, raisons de contestation, hypothèses attaquées, tests, résultats, alternatives, corrections, re-tests, verdict, confiance, domaine de validité, conditions d'invalidation et artefacts reproductibles.

Une contestation rejetée est elle-même une connaissance utile si son rejet est démontré.

---

## 15. Séparation apprentissage / autorisation d'agir

**OBSERVATION → HYPOTHÈSE → EXPÉRIMENTATION → CONTESTATION → PREUVE → VALIDATION → AUTORISATION CONTRÔLÉE → DÉPLOIEMENT → SURVEILLANCE**

Une découverte ne doit pas automatiquement modifier le comportement opérationnel.

---

## 16. Humilité épistémique

Le système doit pouvoir déclarer : **JE SAIS**, **JE CROIS**, **JE NE SAIS PAS**, **JE NE PEUX PAS TESTER**, **JE ME SUIS TROMPÉ**, **JE NE SAIS PAS ENCORE POURQUOI**.

Reconnaître une limite est une sortie valide du système.

---

## 17. Invariant architectural

> **Aucune connaissance, règle, métrique, architecture ou décision critique ne doit être considérée comme définitivement correcte sans mécanisme explicite permettant de rechercher activement les conditions de son invalidation.**

> **Le système doit être conçu pour pouvoir découvrir qu'il a mal pensé.**

---

## 18. Critère de maturité

Un système mature sait :

**APPRENDRE → DÉCIDER → AGIR → CONTESTER → DÉTECTER SES ANGLES MORTS → RÉVISER → SUSPENDRE → ARRÊTER → REPRENDRE AVEC UNE MEILLEURE HYPOTHÈSE**.

La robustesse vient de la capacité à rendre les erreurs détectables, corrigeables et non catastrophiques.
