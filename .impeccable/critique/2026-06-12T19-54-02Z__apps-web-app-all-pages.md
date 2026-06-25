---
target: apps/web/app - all pages v2
total_score: 36
p0_count: 0
p1_count: 1
timestamp: 2026-06-12T19-54-02Z
slug: apps-web-app-all-pages
---
## Design Health Score

| # | Heuristique | Score | Problème clé |
|---|-------------|-------|-------------|
| 1 | Visibilité de l'état du système | 4/4 | Skeletons, toasts, JobProgress, empty states, badges — partout |
| 2 | Correspondance système/monde réel | 4/4 | 100% français, terminologie mode cohérente |
| 3 | Contrôle et liberté utilisateur | 4/4 | Retour dans wizards, confirm dialogs, Escape |
| 4 | Cohérence et standards | 4/4 | Mêmes composants, variants, animations — MotionConfig partout |
| 5 | Prévention d'erreurs | 4/4 | Validation, anti-double-click, confirm avant delete |
| 6 | Reconnaissance plutôt que mémorisation | 4/4 | Sidebar icon+label, headings, empty states, badges |
| 7 | Flexibilité et efficacité | 3/4 | Raccourcis ⌘⏎/Escape, recherche, filtre. Pas d'actions groupées |
| 8 | Design esthétique et minimaliste | 4/4 | Propre, équilibré, typographie soignée, thème dark/light |
| 9 | Récupération d'erreurs | 4/4 | Erreurs inline, toasts, messages clairs |
| 10 | Aide et documentation | 1/4 | Aucun système d'aide, FAQ, support |
| **Total** | | **36/40** | **Excellent — +12 vs 24 précédent** |

## Anti-Patterns Verdict

**LLM assessment**: Aucun slop détecté. Copywriting spécifique, alt text descriptifs, placeholders avec exemples réels, pas d'anglais dans l'UI. Un cran au-dessus de la moyenne des apps IA.

**Déterministic scan**: Aucun anti-pattern détecté sur les 17 pages.

## Overall Impression

L'app a fait un bond significatif. La note de 24/40 était justifiée ; les correctifs (confirm dialogs, back navigation, traductions, skeletons, reduced-motion) portent leurs fruits. La cohérence visuelle est absolue, la gestion des états irréprochable, la qualité des animations subtile et respectueuse de `prefers-reduced-motion`. Le seul vrai point faible — l'absence de système d'aide — est un choix délibéré plus qu'un oubli.

## Vérification des correctifs précédents

| Problème | Statut |
|----------|--------|
| [P0] Confirm dialogs avant suppression | ✅ Dressing, Members, Settings |
| [P0] Anti-double-click | ✅ Boutons `loading` + `disabled` |
| [P1] Back navigation onboarding/create-brand | ✅ Boutons "Retour" présents |
| [P1] Placeholders billing/settings améliorés | ✅ Messages clairs |
| [P2] "Mot de passe oublié" sur login | ✅ Lien présent |
| [P2] Traductions (Dashboard, API Keys, AI Stylist, ...) | ✅ Toutes traduites |
| [P3] Skeleton loaders catalogue | ✅ Grid de squelettes |
| [P3] Analytics : date + ARIA | ✅ Tooltip avec date, aria-label |
| [P3] reduced-motion via MotionConfig | ✅ Layouts app + brand |
| [P3] Alt text, ARIA, recherche par nom | ✅ Dynamique + garment_name |

## Problèmes résiduels

### P1 — Bug de redirection auth
**Où** : `(brand)/layout.tsx:15`
**Problème** : `router.push('/auth/login')` → la route est `/login`, pas `/auth/login`. 404 sur pages brand non authentifiées.
**Fix** : `router.push('/login')`

### P3 — Loading state du dialog de confirmation invisible
**Où** : `dressing/page.tsx:45,188`
**Problème** : `loading={deletingId === confirmDeleteId}` — `confirmDeleteId` est remis à `null` avant l'appel API (ligne 45). Le dialog se ferme sans feedback visuel.
**Fix** : Déplacer `setConfirmDeleteId(null)` après la réussite de l'appel API, pas avant.

### P3 — "Analytiques" anglicisé
**Où** : `brand-sidebar.tsx:24`
**Fix** : `'Analyses'` ou `'Statistiques'`

### P3 — Zones d'upload onboarding non fonctionnelles
**Où** : `onboarding/page.tsx:59-68`
**Problème** : 3 zones décoratives avec `cursor-pointer` mais aucun `onClick`. L'utilisateur clique sans effet.
**Fix** : Ajouter `UploadZone` importé mais inutilisé, ou retirer `cursor-pointer`.

### P3 — Pas de confirmation du mot de passe à l'inscription
**Où** : `signup/page.tsx`
**Problème** : Un seul champ password. Risque d'erreur de saisie non détectée.
**Fix** : Ajouter un champ "Confirmer le mot de passe".

### P3 — `window.location.href` au lieu du router Next.js
**Où** : `login/page.tsx:64`, `signup/page.tsx:65`
**Problème** : Perte d'état et rechargement complet de la page.
**Fix** : Remplacer par `router.push('/studio')`.

### P3 — Aucun système d'aide (documentation)
**Où** : Toutes les pages
**Problème** : Aucun moyen de trouver de l'aide, FAQ, ou support.
**Fix** : Ajouter un lien "Aide" global (sidebar ou menu utilisateur).

## Persona Red Flags

**Alex (Power User)** : Score flexibilité 3/4 — le seul vrai manque. Pas d'actions groupées dans Dressing (sélection multiple, batch delete/download). Pas de palette de commandes.

**Sam (Accessibility)** : Tout est propre — ARIA labels, alt text, roles, MotionConfig reduced-motion. Le graphique Analytics a maintenant `role="img"` et `aria-label`.

**Riley (Stress Tester)** : Les confirm dialogs sont là, l'anti-double-click aussi. Le bug de redirection auth (P1) est le plus gros risque — si l'utilisateur perd sa session sur une page brand, il tombe sur 404.

## Questions

1. **Le bug de redirection auth (P1)** — je le corrige tout de suite ? C'est le seul vrai blocage.
2. **Aide/documentation** — tu veux qu'on ajoute un lien "Aide" ou "Centre d'aide" dans la sidebar/menu ? C'est le plus gros impact pour le score (1/4 → 2/4).
3. **Pour les P3** (loading state dialog, zones upload onboarding, confirmation password, router) — on les prend tous ou on focus le P1 d'abord ?
