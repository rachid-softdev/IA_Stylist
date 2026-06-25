# Audit de configuration TypeScript — IA Stylist

> **Date** : 2026-06-24
> **TypeScript** : `^5.5.0` (root package.json)
> **Monorepo** : Turborepo avec 5 fichiers tsconfig.json + 1 package sans tsconfig
> **Analyseur** : tech-lead
> **Note globale** : **4.5 / 10**

---

## 1. Architecture des fichiers tsconfig

| Fichier | `strict` | `skipLibCheck` | `isolatedModules` | Déclarations |
|---|---|---|---|---|
| `apps/web/tsconfig.json` | ✅ true | ✅ true | ✅ true | ❌ |
| `apps/mobile/tsconfig.json` | ✅ true | ✅ true | ❌ | ❌ |
| `packages/ui/tsconfig.json` | ✅ true | ✅ true | ❌ | ✅ declaration + declarationMap |
| `packages/utils/tsconfig.json` | ✅ true | ✅ true | ❌ | ✅ declaration + declarationMap |
| `packages/shared-types/tsconfig.json` | ✅ true | ✅ true | ❌ | ✅ declaration + declarationMap |
| `packages/widget-sdk/` | ❌ Aucun tsconfig | ❌ Aucun tsconfig | ❌ Aucun tsconfig | ❌ |

**Problème architecturel majeur** : Aucun `extends` partagé. Chaque tsconfig est dupliqué manuellement. Il manque un `tsconfig.base.json` racine.

---

## 2. Analyse exhaustive de chaque option

### 2.1 Options activées via `strict: true`

#### 🔹 `noImplicitAny`

| | |
|---|---|
| **État** | ✅ Activé (via `strict` dans les 5 fichiers) |
| **Ce que ça change** | Empêche TypeScript de déduire `any` quand le type ne peut pas être inféré. Oblige à annoter les paramètres. |
| **Risque si désactivé** | `function add(a, b)` deviendrait `(a: any, b: any) => any` — zéro sécurité de type. |
| **Recommandé** | ✅ Oui, indispensable |
| **Exemple de bug évité** | `function divide(a, b) { return a / b; }` avec `noImplicitAny` → erreur, obligé de typer `(a: number, b: number)`. Sans ça, `divide("hello", {})` compile et produit `NaN` au runtime. |
| **Usage réel** | Le code utilise cette protection. Les paramètres sont bien typés. |

#### 🔹 `strictNullChecks`

| | |
|---|---|
| **État** | ✅ Activé (via `strict`) |
| **Ce que ça change** | `null` et `undefined` ne sont plus assignables à tous les types. Oblige à gérer les cas nullables. |
| **Risque si désactivé** | `user.name` sur un objet potentiellement `null` → `TypeError: Cannot read property` |
| **Recommandé** | ✅ Oui, non négociable |
| **Exemple de bug évité** | `const user: User | null = getUser(); user.name` → erreur de compilation. Obligé de faire `if (user) { user.name }` |
| **Usage réel** | Le projet utilise correctement `User | null`, `Garment | null`, `BrandMember | null`. Les stores sont bien typés avec `| null`. ✅ |

#### 🔹 `strictFunctionTypes`

| | |
|---|---|
| **État** | ✅ Activé (via `strict`) |
| **Ce que ça change** | Active la **contravariance** sur les paramètres de fonction. `(arg: Animal) => void` n'est plus assignable à `(arg: Dog) => void` |
| **Risque si désactivé** | Assignation incorrecte de callbacks sans erreur de compilation |
| **Recommandé** | ✅ Oui |
| **Exemple de bug évité** | Un callback attendant `Dog` reçoit `Animal` → méthode spécifique à `Dog` appelée sur un `Cat` = crash |

#### 🔹 `strictBindCallApply`

| | |
|---|---|
| **État** | ✅ Activé (via `strict`) |
| **Ce que ça change** | `.bind()`, `.call()`, `.apply()` sont typés avec les bons arguments |
| **Risque si désactivé** | `fn.call(null, "wrong", "args")` accepté silencieusement |
| **Recommandé** | ✅ Oui |
| **Remarque** | Option peu impactante pour ce projet (peu d'usage de call/bind/apply dans le code) |

#### 🔹 `strictPropertyInitialization`

| | |
|---|---|
| **État** | ✅ Activé (via `strict`) |
| **Ce que ça change** | Les propriétés de classe sans initialiseur `?` doivent être initialisées dans le constructeur |
| **Risque si désactivé** | Propriétés `undefined` au runtime sans avertissement |
| **Recommandé** | ✅ Oui |
| **Exemple de bug évité** | `class Service { private db: Database; }` → erreur : `db` non initialisée. Oblige un constructeur. |
| **Impact réel** | La classe `ApiClient` initialise `baseUrl` dans le constructeur. ✅. `ApiClientError` initialise `code`, `status` via le constructeur. ✅ |

#### 🔹 `noImplicitThis`

| | |
|---|---|
| **État** | ✅ Activé (via `strict`) |
| **Ce que ça改变** | `this` en dehors d'une classe ou méthode → `this: any` est interdit |
| **Risque si désactivé** | `this.value` dans une fonction normale → `any`, pas d'erreur |
| **Recommandé** | ✅ Oui |
| **Usage réel** | Le projet utilise des classes (`ApiClient`, `ApiClientError`) avec `this` correctement typé. ✅ |

#### 🔹 `alwaysStrict`

| | |
|---|---|
| **État** | ✅ Activé (via `strict`) |
| **Ce que ça change** | Émet `"use strict"` dans tous les fichiers JS compilés |
| **Risque si désactivé** | Assignation accidentelle à une variable globale sans `let`/`const` |
| **Recommandé** | ✅ Oui |

### 2.2 Options strictes NON activées (manquantes critiques)

#### 🔹 `useUnknownInCatchVariables` ❌

| | |
|---|---|
| **État** | ❌ **Non activé** (option séparée, pas dans `strict`) |
| **Ce que ça change** | `catch(e)` passe de `e: any` à `e: unknown`. Oblige à vérifier le type avant d'utiliser `e`. |
| **Risque** | `catch(e) { console.log(e.message) }` → si une `string` est jetée, `TypeError: e.message is undefined` |
| **Recommandé** | ✅ **Critique** pour toute app production |
| **Exemple** | `try { JSON.parse(input); } catch (e) { console.log(e.message); }` → crash si `throw "oups"`. Avec `useUnknownInCatchVariables` : obligé de faire `e instanceof Error` |
| **Usage réel** | Bonne nouvelle : 3 fichiers utilisent `catch (err: unknown)` **manuellement** (`studio/page.tsx`, `catalog/page.tsx`, `create-brand/page.tsx`). Mais `use-websocket.ts` et `widget-sdk` ont des `catch` non typés. |

#### 🔹 `exactOptionalPropertyTypes` ❌

| | |
|---|---|
| **État** | ❌ **Non activé** |
| **Ce que ça change** | `prop?: string` devient vraiment `string | undefined`, mais empêche d'assigner `undefined` explicitement. `{ prop: undefined }` n'est plus égal à `{}`. |
| **Risque** | Comportement incohérent entre absence et `undefined` explicite |
| **Recommandé** | ⚠️ Trop perturbant pour migration directe, mais bonne pratique |
| **Usage réel** | Les types `ProfileMetadata`, `GarmentMetadata`, `GenerationParams`, `PlanLimits` utilisent beaucoup de `?` optionnels. L'activation de cette option **casserait massivement** le code. À faire progressivement. |

#### 🔹 `noUncheckedIndexedAccess` ❌

| | |
|---|---|
| **État** | ❌ **Non activé** |
| **Ce que ça change** | `arr[i]` et `obj[key]` retournent `T | undefined` au lieu de `T` |
| **Risque** | `const first = arr[0]; first.toUpperCase()` → crash si tableau vide. Propage `undefined` silencieusement |
| **Recommandé** | ✅ **Important** pour les tableaux React (rendu de listes) |
| **Exemple** | `const items = getGarments(); items[0].name` → si le tableau est vide, `undefined.name` = crash. Avec l'option : `items[0]` est `Garment | undefined` |
| **Usage réel** | Le projet utilise `arr[0]`, `arr[i]` dans plusieurs composants (ex: `catalog/page.tsx` `garments.map(...)`). **Risque réel** en l'absence de cette option. |

#### 🔹 `noImplicitOverride` ❌

| | |
|---|---|
| **État** | ❌ **Non activé** |
| **Ce que ça change** | Oblige le mot-clé `override` sur les méthodes qui surchargent une méthode parente |
| **Risque** | Renommer une méthode dans la classe parente → la méthode "surcharge" devient une méthode indépendante silencieuse |
| **Recommandé** | ✅ **Important** pour la maintenabilité |
| **Exemple** | `class Derived extends Base { fetchData() {} }` — si `fetchData` est renommé en `loadData` dans `Base`, `Derived.fetchData` n'est plus jamais appelée. Avec `override` : erreur de compilation. |

#### 🔹 `noPropertyAccessFromIndexSignature` ❌

| | |
|---|---|
| **État** | ❌ **Non activé** |
| **Ce que ça change** | Pour les types avec `[key: string]: T`, interdit `obj.key`, oblige `obj["key"]` |
| **Risque** | Accès via `.` sur une clé qui n'est pas garantie d'exister |
| **Recommandé** | ⚠️ Utile mais verbeux. Pas prioritaire. |

### 2.3 Options de qualité de code NON activées

#### 🔹 `noFallthroughCasesInSwitch` ❌

| | |
|---|---|
| **État** | ❌ **Non activé** (doit être explicite, pas dans `strict`) |
| **Ce que ça change** | Interdit le fallthrough dans les `switch` (un `case` qui enchaîne sur le suivant sans `break`/`return`) |
| **Risque** | Oubli de `break` → exécution du case suivant = bug silencieux |
| **Recommandé** | ✅ **Critique** |
| **Exemple** | `switch(status) { case "draft": doDraft(); case "published": doPublish(); }` → oubli de `break`, `doPublish()` exécuté aussi pour "draft" |
| **Usage réel** | Le projet utilise `switch` dans `getJobStatusColor` et `getJobStatusLabel` (packages/utils) et potentiellement ailleurs. **Risque réel**. |

#### 🔹 `noImplicitReturns` ❌

| | |
|---|---|
| **État** | ❌ **Non activé** |
| **Ce que ça change** | Vérifie que tous les chemins d'une fonction retournent une valeur si le type de retour n'est pas `void` |
| **Risque** | Fonction qui dit retourner `boolean` mais omet un `return` → `undefined` |
| **Recommandé** | ✅ **Important** |
| **Exemple** | `function isPositive(n: number): boolean { if (n > 0) return true; }` → retourne `undefined` si `n <= 0` |
| **Usage réel** | La fonction `isAllowedImageType` de `utils` a un seul `return`. `formatBytes` a un seul `return` à la fin. Le risque est modéré car la plupart des fonctions ont un seul point de sortie. |

#### 🔹 `noUnusedLocals` ❌

| | |
|---|---|
| **État** | ❌ **Non activé** |
| **Ce que ça change** | Interdit les variables locales déclarées mais jamais utilisées |
| **Risque** | Code mort, fausses déclarations oubliées après refactor |
| **Recommandé** | ✅ Oui |
| **Note** | À activer avec `noUnusedParameters` ensemble. S'attendre à des erreurs initiales dans une base existante. |

#### 🔹 `noUnusedParameters` ❌

| | |
|---|---|
| **État** | ❌ **Non activé** |
| **Ce que ça change** | Interdit les paramètres de fonction déclarés mais jamais utilisés (sauf `_` préfixé) |
| **Risque** | Paramètres oubliés après refactor |
| **Recommandé** | ✅ Oui |

#### 🔹 `allowUnusedLabels` (défaut = `false`) ✅

| | |
|---|---|
| **État** | ✅ Désactivé (option non spécifiée → `false` par défaut) |
| **Ce que ça change** | Interdit les labels inutilisés comme `loop: for(...)` sans `break loop` |
| **Sûr** | ✅ Oui, valeur par défaut correcte |

#### 🔹 `allowUnreachableCode` (défaut = `false`) ✅

| | |
|---|---|
| **État** | ✅ Désactivé (option non spécifiée → `false` par défaut) |
| **Ce que ça change** | Interdit le code après un `return`, `throw`, etc. |
| **Sûr** | ✅ Oui, valeur par défaut correcte |

### 2.4 Options de module et transpilation

#### 🔹 `isolatedModules`

| | |
|---|---|
| **État** | ⚠️ **Partiellement activé** : ✅ dans `apps/web` seulement. ❌ dans `apps/mobile`, `packages/ui`, `packages/utils`, `packages/shared-types` |
| **Ce que ça change** | Chaque fichier peut être transpilé indépendamment. Interdit `const enum`, `export namespace`, `ambient const enum` |
| **Risque** | `const enum` utilisé et compilé normalement, mais avec SWC/Babel → ignoré silencieusement = valeurs `undefined` au runtime |
| **Recommandé** | ✅ **Critique** pour apps/web (SWC), apps/mobile (Metro/Babel), packages (bundler) |
| **Risque réel** | Aucun `const enum` trouvé dans le code actuel, mais l'option empêche d'en introduire accidentellement. |

#### 🔹 `verbatimModuleSyntax` ❌

| | |
|---|---|
| **État** | ❌ **Non activé** partout |
| **Ce que ça change** | Oblige `import type` pour les imports utilisés uniquement comme types. Empêche l'élimination silencieuse d'imports. |
| **Risque** | Un import peut être supprimé par le compilateur si le bundler ne comprend pas qu'il est utilisé uniquement pour le type |
| **Recommandé** | ⚠️ Important pour les **packages** (publiés). Les apps Next.js/Expo gèrent les imports de type via leur bundler. |
| **Usage réel** | Le projet utilise déjà `import type` dans plusieurs fichiers (`auth-store.ts`, `studio-store.ts`, `members/page.tsx`, etc.). ✅ Bonne pratique déjà en place partiellement. |

#### 🔹 `moduleDetection`

| | |
|---|---|
| **État** | Non spécifié → `"auto"` par défaut |
| **Ce que ça change** | Détecte automatiquement si un fichier est un module (présence d'import/export) ou un script. |
| **Sûr** | ✅ Oui |

#### 🔹 `skipLibCheck` ⚠️

| | |
|---|---|
| **État** | ✅ **Activé** dans les 5 fichiers tsconfig |
| **Ce que ça change** | Ignore la vérification des types dans tous les `.d.ts` (incluant `node_modules`) |
| **Risque** | Les erreurs de type dans les dépendances passent inaperçues. Un package peut fournir des types incorrects. |
| **Compromis** | Gain de vitesse de compilation massif. Le checker TS ne vérifie pas toutes les dépendances transitives. |
| **Recommandé** | ⚠️ **Acceptable** pour la DX quotidienne, mais prévoir un check CI périodique avec `--skipLibCheck false` |
| **Note** | C'est un compromis standard. Même les plus gros projets React/Next.js l'activent. |

---

## 3. Analyse des options incompatibles ou dangereuses

| Problème | Localisation | Gravité | Explication |
|---|---|---|---|
| `target: ES2017` | `apps/web` | 🟡 Important | Date de 2016. En 2026, tous les navigateurs et Node.js supportent ES2022+. Prive des fonctionnalités comme `Object.hasOwn()`, `at()`, `Array.fromAsync()`, ou `Error.cause`. |
| `allowJs: true` | `apps/web` | 🟡 Important | Permet du code JS non typé dans une base TS. Utile pour migration graduelle, mais dangereux si exploité. Aucun fichier `.js` trouvé dans le projet → l'option est inutilisée. |
| `moduleResolution: "bundler"` | Tous | ✅ OK | Correct pour Next.js (webpack/turbopack), Tumblr, esbuild. |
| `jsx: "preserve"` | `apps/web` | ✅ OK | Next.js gère la transpilation JSX via SWC. |
| Pas de `tsconfig` pour `widget-sdk` | `packages/widget-sdk` | 🔴 **Critique** | Le widget SDK compile avec esbuild sans aucune vérification TypeScript. Les erreurs de type dans `src/index.ts` passent inaperçues. |

---

## 4. Compromis DX vs Sécurité

| Option | DX | Sécurité | Verdict |
|---|---|---|---|
| `skipLibCheck: true` | ⚡ Très rapide | ⚠️ Risque masqué | Acceptable |
| `noUnusedLocals` | 🐌 Bloque commits | ✅ Code propre | À activer |
| `noUncheckedIndexedAccess` | 🐌 Plus verbeux | ✅ Array-safe | À activer |
| `exactOptionalPropertyTypes` | 🐌 Très contraignant | ✅ Cohérence | Migration lente |
| `verbatimModuleSyntax` | 🐌 `import type` obligatoire | ✅ Pas d'ambiguité | Packages d'abord |
| `noImplicitOverride` | 🐌 Mot-clé `override` | ✅ Refactor safe | À activer |

---

## 5. Analyse du code source : patterns réels

### `any` utilisé dans le code

| Fichier | Ligne | Usage | Problème |
|---|---|---|---|
| `apps/web/app/(app)/stylist/page.tsx` | 18 | `return res.data as any` | 🔴 Escaping complet de la sécurité de type. Le type de retour de l'API est inconnu mais `any` cache tout. |
| `apps/web/app/(brand)/members/page.tsx` | 78, 81 | `(member as any).email` | 🟡 Le type `BrandMember` n'a pas de champ `email`. Au lieu d'étendre le type, le code utilise `as any` pour accéder à une propriété non déclarée. |
| `apps/web/lib/__tests__/api.test.ts` | 52 | `delete (global as any).fetch` | ✅ Acceptable (fichier de test). Mock de `fetch` pour les tests unitaires. |
| `apps/web/lib/__tests__/api.test.ts` | 192-215 | `(err as unknown as ApiClientErrorLike)` | ✅ Double cast `unknown` puis `ApiClientErrorLike`. C'est correct pour un test. |

**Total : 4 occurrences de `as any`, dont 2 dans le code de production.**

### `as` casts (sans `any`) dans le code

Le projet utilise massivement le type assertion `as` pour le narrowing :

```typescript
// 4 occurrences dans use-generation-job.ts
data.status as JobStatus          // Risque : aucune validation de la valeur
data.result_url as string         // Risque : undefined → string
data.result_metadata as Record<string, unknown> | undefined

// api.ts
optHeaders as Record<string, string>  // Correct si les headers sont une string

// members/page.tsx
e.target.value as 'admin' | member'   // Correct : on sait que c'est la valeur du select

// garment-selector.tsx
e.target as HTMLInputElement          // Correct : l'event est un change event
```

**Ces `as` en production sont des endroits où `noUncheckedIndexedAccess` et `noImplicitReturns` feraient la différence.** Sans ces options, ces casts réussissent silencieusement même avec des données invalides.

### `catch(err: unknown)` — Usage incohérent

✅ **Bon usage** :
- `studio/page.tsx:82` : `catch (err: unknown)` + `err instanceof Error`
- `create-brand/page.tsx:29` : `catch (err: unknown)` + `err instanceof Error`
- `catalog/page.tsx:131` : `catch (err: unknown)` + `err instanceof Error`

❌ **Manquant** :
- `use-websocket.ts:89` : `catch { ... }` (pas d'argument catch)
- `widget-sdk/src/index.ts:263` : `catch (err)` — pas de type, pas de vérification
- `auth-store.ts`, `studio-store.ts` : pas de try/catch

### Qualité générale du code TypeScript

| Critère | Évaluation |
|---|---|
| Utilisation de `import type` | ✅ Plusieurs fichiers utilisent `import type` |
| Typage des stores Zustand | ✅ `create<AuthState>`, `create<StudioState>` — interfaces bien définies |
| Typage des props React | ✅ `ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<...>` |
| Génériques | ✅ `ApiResponse<T>`, `api.get<T>`, `api.post<T>` |
| `Record<string, unknown>` | ✅ Utilisé plutôt que `Record<string, any>` |
| `@ts-expect-error` / `@ts-ignore` | ✅ **Aucun** dans tout le projet |
| Fonctions utilitaires | ✅ `cn(...inputs: ClassValue[])`, `debounce<T extends (...args: unknown[]) => unknown>` |

---

## 6. Impacts par framework

### Next.js / React (apps/web)

| Option | Impact |
|---|---|
| `isolatedModules: true` | ✅ **Requis** pour SWC (compilateur par défaut de Next.js 15) |
| `jsx: "preserve"` | ✅ Correct — Next.js/SWC gère la transpilation JSX |
| `skipLibCheck: true` | ⚠️ Standard Next.js, recommandé pour la vitesse |
| `noUncheckedIndexedAccess` | 🟡 Critique pour les listes React : rendu conditionnel, map, etc. |
| `moduleResolution: "bundler"` | ✅ Compatible webpack/turbopack |
| `target: ES2017` → `ES2022` | 🟡 Next.js transpile via SWC donc `target` a peu d'impact réel, mais ES2017 est très daté |

### Expo / React Native (apps/mobile)

| Option | Impact |
|---|---|
| `isolatedModules` **manquant** | 🔴 **Critique** — Metro/Babel a besoin de `isolatedModules: true`. Les `const enum` passeraient en production sans erreur de compilation |
| `moduleResolution: "bundler"` | ✅ Compatible Metro |
| `jsx: "react-jsx"` | ✅ Correct pour Expo SDK 50+ |

### Packages (ui, utils, shared-types)

| Option | Impact |
|---|---|
| `declaration: true` | ✅ Bon pour les packages — génère les `.d.ts` |
| `declarationMap: true` | ✅ Bon pour la navigation IDE |
| `isolatedModules` **manquant** | 🟡 Les packages sont buildés par `tsc` (hypothèse) ou bundler. `const enum` serait problématique |
| Aucun `outDir` pour shared-types | 🟡 `outDir: "./dist"` présent, mais shared-types n'a pas de script `build` qui utilise tsc |

### Widget SDK (packages/widget-sdk)

**Aucun tsconfig.json** — c'est le problème le plus grave.

- Le SDK est buildé directement avec `esbuild` sans vérification TypeScript
- `widget-sdk/src/index.ts` utilise `catch (err)` sans type, accès à `document.body.style.overflow`, etc.
- Aucune validation de type en CI
- Les bugs de type dans ce fichier ne seront détectés qu'au runtime

---

## 7. Incohérences entre les fichiers tsconfig

| Incohérence | Détail |
|---|---|
| `forceConsistentCasingInFileNames` | ✅ Présent dans les 3 packages, ❌ **absent** dans `apps/web` et `apps/mobile` |
| `resolveJsonModule` | ✅ Présent dans `apps/web`, `apps/mobile` ❌ **absent** dans les 3 packages |
| `isolatedModules` | ✅ Présent seulement dans `apps/web` |
| `target` | `apps/web`: `ES2017`, `apps/mobile`: `ESNext`, packages: `ES2020` |
| `module` | `apps/web`: `esnext`, `apps/mobile`: `ESNext`, packages: `ESNext` |
| Duplication complète | Les 3 packages ont **exactement le même contenu** à 2 lignes près (jsx). Devrait être factorisé. |

---

## 8. Note globale : **4.5 / 10**

| Catégorie | Points | Max | Commentaire |
|---|---|---|---|
| Strict mode | 3 | 3 | ✅ `strict: true` partout |
| Options post-strict | 0 | 3 | ❌ Aucune n'est activée |
| Qualité de code | 0.5 | 2 | ❌ `noFallthroughCasesInSwitch`, `noImplicitReturns`, etc. absents |
| Cohérence | 0.5 | 1 | ⚠️ tsconfig dupliqués, incohérences entre fichiers |
| Sécurité production | 0.5 | 1 | ⚠️ `as any` dans le code, usage intensif de `as`, pas de `useUnknownInCatchVariables` |
| **Total** | **4.5** | **10** | |

**Rupture de note** : Le passage de 5 → 4.5 est dû à :
- La découverte de `as any` dans le code de production (2 occurrences)
- L'absence critique de `isolatedModules` dans 4/5 fichiers (mode mobile significativement exposé)
- L'absence totale de tsconfig pour le widget-sdk
- Les `as` casts non validés dans `use-generation-job.ts`

---

## 9. Classification des problèmes par gravité

### 🔴 Critiques

| # | Problème | Fichiers | Détail |
|---|---|---|---|
| C1 | **`as any` en production** | `stylist/page.tsx`, `members/page.tsx` | Contournement de la sécurité de type. Périmètre non maîtrisé. |
| C2 | **`isolatedModules` manquant** | `apps/mobile`, packages | SWC/Metro/Babel peuvent mal compiler `const enum` et autres construits TS non isolés |
| C3 | **Widget SDK sans tsconfig** | `packages/widget-sdk/` | Aucune validation TypeScript sur le SDK. Les erreurs de type arrivent en production. |
| C4 | **`noFallthroughCasesInSwitch` absent** | Tous | Risque de bug silencieux dans les `switch` existants (utils `getJobStatusColor`, `getJobStatusLabel`) |
| C5 | **`useUnknownInCatchVariables` absent** | Tous | `catch(e: any)` = crash potentiel si l'erreur n'est pas un `Error` |

### 🟡 Importants

| # | Problème | Fichiers | Détail |
|---|---|---|---|
| I1 | **Pas de tsconfig.base.json** | Racine | 5 fichiers tsconfig dupliqués manuellement. Risque de dérive. |
| I2 | **`skipLibCheck` partout** | Tous | Cache les erreurs de type des dépendances. Acceptable pour la DX mais pas de check périodique en CI |
| I3 | **`noUncheckedIndexedAccess` absent** | Tous | Accès tableau non sécurisé. Risque `undefined.name` |
| I4 | **`noImplicitOverride` absent** | Tous | Refactor d'héritage dangereux |
| I5 | **`noImplicitReturns` absent** | Tous | `undefined` retourné silencieusement |
| I6 | **`allowJs: true` inutile** | `apps/web` | Aucun fichier `.js` dans le projet. Active une fonctionnalité superflue |
| I7 | **`target: ES2017`** | `apps/web` | Trop ancien pour 2026. Ne pas exploiter les fonctionnalités modernes |

### 🟢 Améliorations

| # | Problème | Fichiers | Détail |
|---|---|---|---|
| A1 | **`noUnusedLocals` + `noUnusedParameters`** | Tous | Code mort non détecté |
| A2 | **`forceConsistentCasingInFileNames` manquant** | `apps/web`, `apps/mobile` | Bugs cross-platform (macOS ≠ Linux) |
| A3 | **`verbatimModuleSyntax`** | Packages | Import type explicite pour les packages publiés |
| A4 | **`exactOptionalPropertyTypes`** | Tous | Cohérence pour les props optionnelles (migration longue) |
| A5 | **`noPropertyAccessFromIndexSignature`** | Tous | Protection des accès indexés (verbeux, pas prioritaire) |
| A6 | **`moduleResolution: "bundler"` vs "node16"** | Packages | Pour compatibilité avec les consommateurs Node.js ESM |

---

## 10. Version améliorée complète

### 10.1 Créer un tsconfig.base.json à la racine

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "useUnknownInCatchVariables": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "forceConsistentCasingInFileNames": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "verbatimModuleSyntax": true
  }
}
```

### 10.2 apps/web/tsconfig.json

```json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "lib": ["dom", "dom.iterable", "esnext"],
    "noEmit": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": {
      "@/*": ["./*"],
      "@vfs/shared-types": ["../../packages/shared-types/src"],
      "@vfs/utils": ["../../packages/utils/src"]
    }
  },
  "include": [
    "next-env.d.ts",
    "**/*.ts",
    "**/*.tsx",
    ".next/types/**/*.ts",
    "../../packages/shared-types/src/**/*.ts",
    "../../packages/utils/src/**/*.ts"
  ],
  "exclude": ["node_modules"]
}
```

Modifications par rapport à l'actuel :
- `"extends": "../../tsconfig.base.json"` → élimine la duplication
- Suppression de `"allowJs": true` → plus de JS non typé
- `"target": "ES2022"` hérité du base
- Toutes les options de sécurité héritées

### 10.3 apps/mobile/tsconfig.json

```json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "jsx": "react-jsx",
    "noEmit": true,
    "paths": {
      "@/*": ["./*"],
      "@vfs/shared-types": ["../../packages/shared-types/src"],
      "@vfs/utils": ["../../packages/utils/src"]
    }
  },
  "include": [
    "**/*.ts",
    "**/*.tsx",
    "../../packages/shared-types/src/**/*.ts",
    "../../packages/utils/src/**/*.ts"
  ],
  "exclude": ["node_modules"]
}
```

### 10.4 packages/ui/tsconfig.json

```json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "declaration": true,
    "declarationMap": true,
    "jsx": "react-jsx",
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

### 10.5 packages/utils/tsconfig.json et packages/shared-types/tsconfig.json

```json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "declaration": true,
    "declarationMap": true,
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*.ts"],
  "exclude": ["node_modules", "dist"]
}
```

### 10.6 Ajouter un tsconfig.json pour packages/widget-sdk

```json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "declaration": true,
    "declarationMap": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "lib": ["dom", "esnext"]
  },
  "include": ["src/**/*.ts"],
  "exclude": ["node_modules", "dist"]
}
```

Et modifier le `package.json` du widget-sdk pour ajouter `"typecheck": "tsc --noEmit"` dans les scripts.

---

## 11. Plan d'action prioritaire

### 🔴 Phase 1 — Actions immédiates (sécurité)

| # | Action | Effort | Impact | Dépendances |
|---|---|---|---|---|
| 1 | Créer `tsconfig.base.json` à la racine | 15 min | Élimine la duplication | Aucune |
| 2 | Étendre tous les tsconfig du `base` | 30 min | Cohérence + options héritées | #1 |
| 3 | Ajouter `useUnknownInCatchVariables` | 15 min | Protection catch | #1 (option dans le base) |
| 4 | Ajouter `noFallthroughCasesInSwitch` | 5 min | Protection switch | #1 (option dans le base) |
| 5 | Ajouter `isolatedModules` aux 4 fichiers manquants | 10 min | Protection const enum | #1 |
| 6 | Supprimer `allowJs: true` de apps/web | 5 min | Pas de JS non typé | #1 |
| 7 | Remplacer les 2 `as any` en production | 20 min | Sécurité de type | Aucune |

### 🟡 Phase 2 — Qualité de code

| # | Action | Effort | Impact | Dépendances |
|---|---|---|---|---|
| 8 | Ajouter `noImplicitOverride` | 5 min | Protection refactor | #1 |
| 9 | Ajouter `noImplicitReturns` | 15 min | Return exhaustifs | #1 + correction des erreurs |
| 10 | Ajouter `forceConsistentCasingInFileNames` à apps | 5 min | Cross-platform | #1 |
| 11 | Ajouter `noUnusedLocals` + `noUnusedParameters` | 30 min | Code mort | #1 + nettoyage des erreurs |
| 12 | Ajouter `noUncheckedIndexedAccess` | 1-2h | Array safety | #1 + nombreuses corrections de code |
| 13 | Remplacer les `as` casts dans `use-generation-job.ts` | 30 min | Sécurité narrowing | #12 (partiellement) |

### 🟢 Phase 3 — Améliorations

| # | Action | Effort | Impact | Dépendances |
|---|---|---|---|---|
| 14 | Ajouter `verbatimModuleSyntax` aux packages | 30 min | Import type explicite | #1 + conversion des imports |
| 15 | Ajouter tsconfig + typecheck pour widget-sdk | 30 min | Validation SDK | #1 |
| 16 | Monter `target` à `ES2022` | 5 min | Features modernes | #1 |
| 17 | Ajouter `exactOptionalPropertyTypes` | 2-3h | Cohérence optional | #1 + corrections majeures |
| 18 | Ajouter un check CI `skipLibCheck: false` hebdomadaire | 30 min | Vérification dépendances | Script CI dédié |

---

## 12. Résumé des risques runtime identifiés

```mermaid
flowchart TD
    subgraph "Risques identifiés dans le code"
        A[as any dans production] --> B[(member as any).email<br/>res.data as any]
        C[as casts non validés] --> D[data.status as JobStatus<br/>sans vérification]
        E[catch non typé] --> F[use-websocket.ts<br/>widget-sdk]
        G[noUncheckedIndexedAccess ❌] --> H[arr[0] retourne T<br/>pas T | undefined]
    end
```

**Risques concrets pour l'utilisateur final :**
1. Une valeur `status` inattendue de l'API → castée silencieusement en `JobStatus` → comportement incohérent
2. Un accès à `members[0].email` (via `as any`) → crash si le membre n'a pas d'email
3. Une erreur non-`Error` dans `use-websocket.ts` → perdue silencieusement
4. Une exception `String` dans `widget-sdk` → non capturée correctement → erreur 500

---

*Document généré par tech-lead — 2026-06-24*
