---
target: apps/web/app - all pages
total_score: 24
p0_count: 1
p1_count: 2
timestamp: 2026-06-12T16-09-10Z
slug: apps-web-app-all-pages
---
## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 3/4 | Catalogue et Membres utilisent "Chargement..." texte brut au lieu de squelettes |
| 2 | Match System / Real World | 2/4 | Angicismes persistants : "Brand Dashboard", "API Keys", "Face", "Top"/"Bottom" |
| 3 | User Control and Freedom | 2/4 | Aucun bouton "Retour" dans les flows onboarding. Pas d'undo sur suppression |
| 4 | Consistency and Standards | 3/4 | AddGarmentForm utilise `<label>`/`<select>` bruts hors système composants |
| 5 | Error Prevention | 2/4 | Zéro confirmation sur actions destructrices (suppression look, membre, compte) |
| 6 | Recognition Rather Than Recall | 3/4 | Recherche Dressing filtre par UUID — pas par nom de vêtement |
| 7 | Flexibility and Efficiency | 2/4 | Aucune action groupée, pas de tri, pas de raccourcis clavier listes |
| 8 | Aesthetic and Minimalist Design | 3/4 | Barres Analytics sans échelle Y ni date dans tooltip |
| 9 | Error Recovery | 2/4 | Login/signup sans suggestions de récupération ("Mot de passe oublié ?") |
| 10 | Help and Documentation | 2/4 | Aucun système d'aide, crédits jamais expliqués, pas de FAQ |
| **Total** | | **24/40** | **Acceptable — améliorations significatives nécessaires** |

## Anti-Patterns Verdict

**LLM assessment**: Le design ne crie pas "AI made this". Les choix sont cohérents : un thème dark luxury editorial assumé, une typographie serif + mono bien différenciée, des animations homogènes. Le plus gros signal de template est l'eyebrow uppercase omniprésent sur les KPIs et titres de section, mais il est appliqué comme un token système plutôt qu'un ornement vide. Pas de gradient text, pas de side-stripe borders, pas de numbered section markers.

**Deterministic scan**: Aucun anti-pattern détecté sur l'ensemble des 17 pages. Le code est structurellement propre.

**Visual overlays**: Non disponibles (aucun serveur de développement en cours d'exécution).

## Overall Impression

L'ADN visuel est excellent : le thème dark luxury avec or chaud, la typographie éditoriale, et le système d'animation cohérent placent cette app bien au-dessus de la moyenne des projets AI-générés. Le problème est ailleurs : des lacunes fonctionnelles (pas de confirmation avant suppression, pas de récupération de mot de passe, pas de retour dans les flows) et des placeholders qui exposent l'incomplétude du produit (billing, settings). La base design est solide ; ce sont les détails d'interaction qui trahissent un produit encore en construction.

## What's Working

1. **Système typographique** : Le trio `font-display` (serif editorial) / `font-heading` (mono) / body avec `text-wrap: balance` et tracking précis — raffinement rare, parfait pour une marque mode luxe.

2. **États vides pensés** : Chaque page de contenu (Dressing, History, Catalog, Analytics, Dashboard, Stylist) a un état vide distinct avec icône, explication, et CTA directionnel. Le dressing vide redirige vers le Studio — UX qui guide, pas qui bloque.

3. **Système d'animation cohérent** : Le easing `[0.16, 1, 0.3, 1]` et le motif `staggerChildren` créent une fluidité homogène sur toutes les pages. L'animation `result-reveal` (flou → net avec scale) est parfaitement adaptée au contexte photo mode.

## Priority Issues

### P0 — Aucune confirmation avant les actions destructrices
- **Où** : `dressing/page.tsx:147` (handleDelete), `members/page.tsx:117` (bouton Trash2), `settings/page.tsx:86` ("Supprimer mon compte")
- **Pourquoi** : Un clic suffit à perdre un look, retirer un collègue, ou (tentativement) supprimer un compte. Aucun dialog "Êtes-vous sûr ?", pas d'undo.
- **Fix** : Ajouter `<Dialog>` de confirmation avant toute action destructive. Désactiver le bouton après le premier clic pour éviter les doublons.
- **Commande** : `/impeccable harden dressing members settings`

### P1 — Navigation arrière absente des flows multi-étapes
- **Où** : `onboarding/page.tsx`, `create-brand/page.tsx`
- **Pourquoi** : Une fois step 2 engagé, impossible de revenir en arrière sans rafraîchir la page. Perte de données utilisateur.
- **Fix** : Ajouter un bouton "Retour" dans chaque étape, avec préservation du state des steps précédents.
- **Commande** : `/impeccable harden onboarding create-brand`

### P1 — Placeholders fonctionnels non signalés (dead ends)
- **Où** : `billing/page.tsx:43` ("Changer de plan" → toast vide), `settings/page.tsx:86` ("Supprimer mon compte" → toast vide), `login/page.tsx:64` / `signup/page.tsx:65` (simulation de connexion)
- **Pourquoi** : L'utilisateur pense faire une action réelle et se heurte à un mur. Déception + sentiment de produit inachevé.
- **Fix** : Soit rendre fonctionnel, soit masquer avec un badge "Bientôt disponible" ou désactiver avec explication.
- **Commande** : `/impeccable harden billing settings`

### P2 — Pas de "Mot de passe oublié" sur la page de connexion
- **Où** : `login/page.tsx`
- **Pourquoi** : Un des motifs d'abandon les plus fréquents dans tout funnel auth. L'utilisateur qui ne se souvient plus de son mot de passe est définitivement bloqué.
- **Fix** : Ajouter un lien "Mot de passe oublié ?" sous le champ password. Même si la page reset n'existe pas encore, le lien est moins frustrant que l'absence totale.
- **Commande** : `/impeccable clarify login`

### P2 — Terminologie anglaise dans une app française
- **Où** : "Brand Dashboard" → Tableau de bord, "API Keys" → Clés API, "Face" → Visage, "Top"/"Bottom" → Haut/Bas, "Starter" → Démarrage
- **Pourquoi** : L'utilisateur français lit une app en français et tombe sur des termes anglais non traduits. Incohérence perçue.
- **Fix** : Traduire tous les titres et labels visibles.
- **Commande** : `/impeccable clarify all`

### P3 — Chargement sans squelette adapté
- **Où** : `catalog/page.tsx:83`, `members/page.tsx:94`
- **Pourquoi** : Toutes les autres pages utilisent `<Skeleton>` ; ces deux pages affichent un texte "Chargement..." basique. Incohérence.
- **Fix** : Remplacer par des `<Skeleton>` adaptés au layout (grid pour catalogue, rows pour membres).
- **Commande** : `/impeccable harden catalog members`

### P3 — Graphique Analytics sans étiquettes de date
- **Où** : `analytics/page.tsx:175`
- **Pourquoi** : Le tooltip hover montre le count mais pas la date. Impossible d'identifier quel jour correspond à quelle barre.
- **Fix** : Ajouter la date dans le tooltip et des labels d'axe X.
- **Commande** : `/impeccable clarify analytics`

## Persona Red Flags

### Alex (Power User) — Usage quotidien
1. **Pas de sélection multiple** dans Dressing. 50 looks = 50 téléchargements individuels.
2. **Pas de tri** dans Dressing/History (par date, catégorie, statut).
3. **Pas de raccourcis clavier** sur les pages liste (↑↓ navigation, Delete suppression).
4. **Double-clic dangereux** : Bouton "Supprimer" jamais désactivé après le premier clic.

### Sam (Accessibility) — Clavier, lecteur d'écran
1. **Icônes KPI** : `<Package>`, `<TrendingUp>` avec `aria-hidden` mais pas d'alternative textuelle.
2. **`<select>` sans label associé** dans AddGarmentForm (`catalog/page.tsx:167`) et Members invite (`members/page.tsx:151`).
3. **Images Dressing** : `alt="Try-on"` générique pour toutes les images — devrait être dynamique.
4. **`prefers-reduced-motion`** géré sur la landing via `MotionConfig` mais pas sur les pages internes.
5. **Graphique barres Analytics** : Simple `div` avec hauteur en % — pas de données accessibles, pas de rôle ARIA.

### Riley (Stress Tester) — Limites, erreurs
1. **Double-clic suppression** dans Dressing → deux appels DELETE avec le même ID.
2. **Double-clic "Générer"** dans Studio → deux appels POST avant que `isGenerating` soit vrai.
3. **Brand dashboard** : `retry: 1` — une indispo réseau = erreur définitive.
4. **Aucun `onError` handler** sur `<img>` dans Dressing (`page.tsx:117`). URL expirée = carré gris silencieux.
5. **Recherche Dressing** : Filtre côté client sans pagination. >1000 jobs = blocage navigateur.

## Minor Observations

1. **Onboarding step 1** : Les zones photo ont `cursor-pointer` mais aucun `onClick` — utilisateur clique dans le vide.
2. **Dressing search** : Filtre par `job.id.toLowerCase()` — les UUID n'ont pas de sens pour l'utilisateur.
3. **Settings email** : Read-only sans indication de comment le modifier.
4. **Members** : `brandId` dérivé de `members[0].brand_id` — si pas de marque, plantage silencieux.
5. **Widget** : Clé API codée en dur `vfs_live_...` — remplacer par appel au store.
6. **CSS** : `font-family: 'Söhne', ...` — police payante Klim, vérifier le bundle.
7. **`transition-all`** sur cartes/boutons — `transition-colors` ou `transition-shadow` serait plus performant.
8. **Billing** : "Plan Starter" en dur — devrait venir de l'API.
9. **Landing** : Le point après "en 60 secondes." dans le hero casse le rythme editorial.
10. **Analytics vs Dashboard** : Les 4 mêmes KPI avec les mêmes icônes sur les deux pages — confusion sur la différenciation.

## Questions to Consider

1. **Brand Dashboard et Analytics affichent les 4 mêmes KPI.** Quelle est la différence de valeur entre ces deux pages ? Dashboard ne devrait-il pas être un résumé narratif ("Cette semaine vs. dernière semaine") plutôt qu'une répétition des chiffres ?

2. **Settings est la page la plus frustrante de l'app.** Email read-only, suppression non fonctionnelle, changement de plan vers un toast vide. Si ces features ne sont pas prêtes, les masquer derrière un badge "Bientôt disponible" ne serait-il pas plus honnête ?

3. **Pourquoi 3 pages d'auth (login, signup, onboarding) mais pas de "Mot de passe oublié" ?** Le funnel d'acquisition s'arrête net au premier échec de connexion.
