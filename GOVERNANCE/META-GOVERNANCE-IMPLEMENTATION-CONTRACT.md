# Contrat d'implémentation — Méta-gouvernance et auto-contestation

**Statut :** CONTRAT ARCHITECTURAL — à satisfaire avant de considérer la méta-gouvernance opérationnelle
**Date :** 12 septembre 2026
**Référence normative :** `GOVERNANCE/META-GOVERNANCE-AND-SELF-CHALLENGE.md`

## Objectif

Transformer la méta-gouvernance en mécanismes observables, testables et auditables. La présence du document de gouvernance seule ne constitue jamais une preuve d'implémentation.

## Gates d'acceptation

1. **Finalité** — détecter une dérive entre valeur réelle recherchée et proxy optimisé.
2. **Hypothèses** — identifier, versionner et contextualiser les hypothèses critiques.
3. **Réfutation** — rechercher activement des contre-exemples aux connaissances critiques.
4. **Anomalies** — transformer les écarts significatifs entre attente et observation en investigations traçables.
5. **Provenance** — remonter chaque connaissance critique à ses observations, expériences, résultats et preuves.
6. **Validité** — conserver domaine de validité, confiance et conditions d'invalidation.
7. **Drift** — détecter les changements susceptibles d'invalider une connaissance ou déclarer explicitement la couverture manquante.
8. **Promotion** — séparer apprentissage et autorisation opérationnelle par un gate vérifiable.
9. **Arrêt** — permettre de suspendre, rétrograder ou abandonner une hypothèse ou évolution.
10. **Audit adversarial** — casser chaque gate et produire uniquement PASS / FAIL / BLOCKED.

## Règle de verdict

- **PASS** : preuve exécutable et satisfaisante.
- **FAIL** : mécanisme exécuté mais violation démontrée.
- **BLOCKED** : contrôle non exécutable ou preuve insuffisante pour conclure.

**BLOCKED ne devient jamais PASS par interprétation.**

## Principe de progression

Intégrer ces gates dans l'architecture existante avec le minimum de nouvelles structures nécessaires. Toute nouvelle structure doit être justifiée par un manque démontré.

Séquence obligatoire :

**CARTOGRAPHIE → CANDIDAT MINIMAL → TEST ADVERSARIAL → CORRECTION → RE-CASSAGE → VERDICT**.

Tant que les gates ne disposent pas de preuves exécutables, l'implémentation globale reste **NON VALIDÉE**.
