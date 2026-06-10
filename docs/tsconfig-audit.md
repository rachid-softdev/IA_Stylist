# Audit de configuration TypeScript — IA Stylist

> **Date** : 2026-06-10
> **TypeScript** : ^5.5.0
> **Monorepo** : 5 tsconfig.json (apps/web, apps/mobile, packages/ui, packages/utils, shared-types)
> **Aucun extends/base** : chaque fichier est indépendant, pas de tsconfig racine commun

---

## Résumé

| Critère | Statut |
|---|---|
| `strict: true` **partout** | ✅ |
| Fichiers tsconfig **dupliqués** | ❌ (5 copies indépendantes) |
| Options post-strict absentes | ❌ |
| `skipLibCheck: true` partout | ⚠️ compromis sécurité |
| `forceConsistentCasingInFileNames` manquant dans apps | ❌ |
| **Note globale** | **5 / 10** |

---

## Analyse détaillée de chaque option

### 🔹 `strict` (true partout)

**État** : ✅ Activé explicitement dans les 5 tsconfig.

`strict: true` active **7 sous-options** d'un coup (voir ci-dessous). C'est le socle minimal pour un projet moderne.

---

### 🔹 `noImplicitAny` — Activé via `strict`

**Ce que ça change** : Interdit les déclarations où TypeScript déduit `any` implicitement (paramètres sans type, etc.).

**Risque si désactivé** : Une fonction `function add(a, b)` serait typée `(a: any, b: any) => any` — zéro sécurité.

**Recommandé** : ✅ Oui, absolument.

**Bug évité** :
```ts
// Sans noImplicitAny, ça compile :
function multiply(a, b) { return a * b; }
multiply("hello", {}); // NaN silencieux
```

---

### 🔹 `strictNullChecks` — Activé via `strict`

**Ce que ça change** : `null` et `undefined` ne sont plus assignables à tous les types. Oblige à gérer les valeurs nullables.

**Risque si désactivé** : `string | null` devient `string`, accès à `.length` sur null → crash runtime.

**Recommandé** : ✅ Oui.

**Bug évité** :
```ts
const user = getUser(); // user: User | null
console.log(user.name); // TypeError: Cannot read property 'name' of null
// StrictNullChecks oblige : if (user) { user.name }
```

---

### 🔹 `strictFunctionTypes` — Activé via `strict`

**Ce que ça change** : Active la **contravariance** des paramètres de fonction. Un `(arg: Animal) => void` n'est plus assignable à `(arg: Dog) => void`.

**Risque si désactivé** : TypeScript devient structurellement moins strict sur les fonctions callback, ce qui peut cacher des bugs de typage.

**Recommandé** : ✅ Oui.

**Bug évité** :
```ts
type FeedDog = (dog: Dog) => void;
const feedAnimal: FeedDog = (animal: Animal) => { /* suppose que c'est un Animal */ };
// Sans strictFunctionTypes, on pourrait passer un Chat ici
```

---

### 🔹 `strictBindCallApply` — Activé via `strict`

**Ce que ça change** : Les méthodes `.bind()`, `.call()`, `.apply()` sont typées précisément avec le nombre et type d'arguments.

**Risque si désactivé** : `fn.apply(null, args)` accepte n'importe quels args.

**Recommandé** : ✅ Oui.

**Bug évité** :
```ts
function greet(greeting: string, name: string) {}
greet.call(null, 42); // TypeError silencieux sans l'option
```

---

### 🔹 `strictPropertyInitialization` — Activé via `strict`

**Ce que ça change** : Une propriété de classe déclarée sans initialiseur et sans `?` doit être initialisée dans le constructeur.

**Risque si désactivé** : Propriétés non initialisées → `undefined` inattendu.

**Recommandé** : ✅ Oui.

**Bug évité** :
```ts
class UserService {
  private db: Database; // Erreur : non initialisée
  // Obligé : constructor() { this.db = new Database(); }
}
```

---

### 🔹 `noImplicitThis` — Activé via `strict`

**Ce que ça change** : Interdit l'usage de `this` là où son type ne peut pas être inféré (fonctions non-fléchées hors classe).

**Risque si désactivé** : `this` devient `any` → accès à des propriétés inexistantes sans erreur.

**Recommandé** : ✅ Oui.

**Bug évité** :
```ts
function handleClick() {
  console.log(this.value); // Erreur : this est any
}
```

---

### 🔹 `alwaysStrict` — Activé via `strict`

**Ce que ça change** : Émet `"use strict"` dans tous les fichiers JS compilés.

**Risque si désactivé** : Assignation accidentelle à une variable globale sans `let`/`const`.

**Recommandé** : ✅ Oui.

---

### 🔹 `useUnknownInCatchVariables` ❌ NON activé

**État** : ❌ Désactivé (pas dans `strict`).

**Ce que ça change** : Passe le type de `catch(e)` de `any` → `unknown`, obligeant à vérifier le type avant d'utiliser `e`.

**Risque** : Accès à `e.message` sans vérification → crash si ce n'est pas une `Error`.

**Recommandé** : ✅ Oui pour toute app production.

**Bug évité** :
```ts
try {
  JSON.parse(input);
} catch (e) {
  console.log(e.message); // TypeError si e === "oups" (string jeté manuellement)
  // Avec useUnknownInCatchVariables : obligé de faire instanceof Error
}
```

---

### 🔹 `exactOptionalPropertyTypes` ❌ NON activé

**État** : ❌ Désactivé.

**Ce que ça change** : `prop?: string` signifie `prop: string | undefined`, mais sans cette option, on peut aussi assigner `undefined` explicitement alors qu'avec, `prop` ne peut être que `string` (ou absent).

**Risque** : Comportement incohérent entre `{ prop: undefined }` et `{ }`.

**Recommandé** : ⚠️ Peut casser beaucoup de code existant. Recommandé mais demande migration progressive.

**Bug évité** :
```ts
interface Config {
  theme?: string;
}
const c1: Config = { theme: undefined }; // OK sans exactOptionalPropertyTypes
// Avec : erreur, doit être string ou absent
```

---

### 🔹 `noUncheckedIndexedAccess` ❌ NON activé

**État** : ❌ Désactivé.

**Ce que ça change** : L'accès à un index `arr[i]` ou `obj[key]` retourne `T | undefined` au lieu de `T`.

**Risque** : Accès hors limites ou clé inexistante → `undefined` propagé sans vérification.

**Recommandé** : ✅ Oui, surtout si utilisation de tableaux/maps/records.

**Bug évité** :
```ts
const items: string[] = ["a", "b"];
const first = items[0]; // string avec unchecked, string | undefined avec l'option
console.log(first.toUpperCase()); // OK sans, risque si tableau vide
// Avec : obligé de vérifier : if (first) ...
```

---

### 🔹 `noImplicitOverride` ❌ NON activé

**État** : ❌ Désactivé.

**Ce que ça change** : Oblige le mot-clé `override` sur les méthodes qui surchargent une méthode de classe parente.

**Risque** : Renommer une méthode parente sans mettre à jour la classe fille → la méthode fille devient indépendante au lieu de surcharger.

**Recommandé** : ✅ Oui, essentiel pour la maintenabilité.

**Bug évité** :
```ts
class Base {
  fetchData() {}
}
class Derived extends Base {
  // Sans override, si fetchData est renommé en loadData dans Base,
  // fetchData dans Derived devient une méthode distincte jamais appelée
  override fetchData() {} // Avec override : erreur si plus de match
}
```

---

### 🔹 `noPropertyAccessFromIndexSignature` ❌ NON activé

**État** : ❌ Désactivé.

**Ce que ça change** : Oblige à utiliser la notation `obj["key"]` pour les signatures d'index, interdit `obj.key`.

**Risque** : Accès typographiquement incorrect via `.` sur un record typé avec `[key: string]: T`.

**Recommandé** : ⚠️ Utile mais peut être verbeux.

**Bug évité** :
```ts
interface Dict { [key: string]: string; }
const d: Dict = { name: "test" };
d.name; // OK sans l'option, mais "name" n'est pas garanti d'exister
// Avec : obligé d'écrire d["name"]
```

---

### 🔹 `allowUnusedLabels` (défaut = false) ✅

**État** : ✅ Désactivé (sûr par défaut).

**Ce que ça change** : Interdit les labels inutilisés (`loop: for(...)` sans `break loop`).

**Sûr** : ✅ Oui.

---

### 🔹 `allowUnreachableCode` (défaut = false) ✅

**État** : ✅ Désactivé (sûr par défaut).

**Ce que ça change** : Interdit le code après un `return`, `throw`, etc.

**Sûr** : ✅ Oui.

---

### 🔹 `noFallthroughCasesInSwitch` (défaut = false) ❌ NON activé

**État** : ❌ Désactivé (doit être activé explicitement, option séparée).

**Ce que ça change** : Interdit le fallthrough non intentionnel dans les `switch` (un `case` qui enchaîne sur le suivant sans `break`/`return`).

**Risque** : Oubli de `break` → exécution du case suivant.

**Recommandé** : ✅ Oui, absolument.

**Bug évité** :
```ts
switch (status) {
  case "draft":
    doDraftStuff(); // Oubli de break → exécute aussi publish
  case "published":
    doPublishStuff();
}
```

---

### 🔹 `noImplicitReturns` ❌ NON activé

**État** : ❌ Désactivé.

**Ce que ça change** : Vérifie que tous les chemins d'une fonction retournent une valeur si le type de retour n'est pas `void`.

**Risque** : Fonction déclarée avec un type de retour non-`void` mais qui omet un return dans certaines branches → `undefined` silencieux.

**Recommandé** : ✅ Oui.

**Bug évité** :
```ts
function isPositive(n: number): boolean {
  if (n > 0) return true;
  // Pas de return ici → undefined, mais type dit boolean
}
```

---

### 🔹 `noUnusedLocals` ❌ NON activé

**État** : ❌ Désactivé.

**Ce que ça change** : Interdit les variables locales déclarées mais jamais utilisées.

**Risque** : Code mort, fausses déclarations, variables oubliées.

**Recommandé** : ✅ Oui, devrait être activé.

---

### 🔹 `noUnusedParameters` ❌ NON activé

**État** : ❌ Désactivé.

**Ce que ça change** : Interdit les paramètres de fonction déclarés mais jamais utilisés (sauf avec `_` préfixé).

**Risque** : Paramètres oubliés après refactor.

**Recommandé** : ✅ Oui (avec exceptions via `_prefix`).

---

### 🔹 `isolatedModules` ⚠️ Partiellement activé

**État** : ✅ Activé dans **apps/web** uniquement. ❌ Désactivé dans apps/mobile, packages/ui, packages/utils, shared-types.

**Ce que ça change** : Garantit que chaque fichier peut être transpilé indépendamment (nécessaire pour SWC/esbuild/Babel).

**Risque** : Sans cette option dans les packages, on peut utiliser des constructions TS qui ne passent pas avec SWC (renommage const enum, export namespace).

**Recommandé** : ✅ Oui, pour toute app compilée par SWC (Next.js) ou bundler.

**Bug évité** :
```ts
// Sans isolatedModules, ceci compile :
const enum Color { Red, Green }
// Mais avec SWC : pas de support → runtime error
```

---

### 🔹 `verbatimModuleSyntax` ❌ NON activé

**État** : ❌ Désactivé partout.

**Ce que ça change** : Empêche l'élimination silencieuse d'imports de types. Oblige à utiliser `import type` pour les imports purement types.

**Risque** : Un import peut être éliminé par le compilateur sans avertissement si utilisé uniquement comme type — peut casser avec les bundlers modernes.

**Recommandé** : ⚠️ Recommandé pour les packages, peut être contraignant dans les apps.

---

### 🔹 `moduleDetection` (défaut = "auto") ✅

**État** : Non spécifié → valeur par défaut `"auto"` partout.

**Ce que ça change** : Détecte automatiquement si un fichier est un module (présence d'import/export). Sûr.

**Sûr** : ✅ Oui.

---

### 🔹 `skipLibCheck` ⚠️ Activé partout

**État** : ✅ Activé dans les 5 tsconfig.

**Ce que ça change** : Ignore la vérification des types dans tous les fichiers `.d.ts` (y compris `node_modules`).

**Risque** :
- Bugs dans les types des dépendances passent inaperçus.
- Un package peut fournir des types incompatibles avec votre version TS.
- Les `@types/*` peuvent avoir des erreurs.

**Compromis** : Énorme gain de vitesse de compilation. Risque réel mais acceptable pour la plupart des projets.

**Recommandé** : ⚠️ Acceptable pour la DX, mais à désactiver ponctuellement en CI si possible.

---

## Analyse transversale

### Options incompatibles / dangereuses

| Problème | Fichiers | Impact |
|---|---|---|
| `skipLibCheck: true` partout | Tous | Masque les erreurs des dépendances |
| `target: ES2017` dans apps/web | apps/web | N'exploite pas `ES2022` (disponible partout en 2026) |
| `allowJs: true` dans apps/web | apps/web | Permet du JS non typé dans le projet |
| `isolatedModules` manquant dans 4/5 | mobile, packages | Risque `const enum` avec SWC/bundler |
| `forceConsistentCasingInFileNames` manquant | apps/web, apps/mobile | Bugs cross-platform (macOS CI case-sensitive vs dev) |

### Compromis DX vs Sécurité

| Option | DX Impact | Sécurité | Verdict |
|---|---|---|---|
| `skipLibCheck` | ⚡ Rapide | ⚠️ Risque masqué | Acceptable |
| `noUnusedLocals` | 🐌 Bloque commit | ✅ Code propre | À activer |
| `noUncheckedIndexedAccess` | 🐌 Plus verbeux | ✅ Array-safe | À activer |
| `verbatimModuleSyntax` | 🐌 `import type` obligatoire | ✅ Clair | À activer dans packages |

### Options trop permissives

1. **`allowJs: true`** (apps/web) : Utile pour migration, mais permet du JS non typé dans une base TS. Risque de régression silencieuse.
2. **Absence de `noUnusedLocals`** : Code mort s'accumule.
3. **Absence de `noImplicitReturns`** : `undefined` retourné silencieusement.
4. **Absence de `noFallthroughCasesInSwitch`** : Bugs de switch.

### Options manquantes pour un projet robuste

- `useUnknownInCatchVariables`
- `noUncheckedIndexedAccess` (prioritaire pour les tableaux React)
- `noImplicitOverride`
- `noImplicitReturns`
- `noUnusedLocals`
- `noUnusedParameters`
- `noFallthroughCasesInSwitch`
- `forceConsistentCasingInFileNames` (manquant dans apps)
- `isolatedModules` (manquant dans mobile et packages)
- `verbatimModuleSyntax` (recommandé pour les packages)

### Impacts par framework

**Next.js / React** :
- `isolatedModules: true` nécessaire pour SWC (Next.js 15)
- `noUncheckedIndexedAccess` critique pour les tableaux React (rendu de listes)
- `jsx: "preserve"` dans apps/web est correct (Next.js gère la transpilation)
- `target` minimal pour Next.js via SWC (peu importe, SWC décide)
- `paths` utilisé correctement pour les aliases

**Node.js (backend)** :
- `moduleResolution: "bundler"` est compatible avec les bundlers modernes
- Pour un backend Node pur, `moduleResolution: "node16"` serait plus approprié (mais ce projet est frontend)

**Expo (mobile)** :
- `jsx: "react-jsx"` dans apps/mobile — compatible avec Expo/React Native
- `isolatedModules` manquant — Expo utilise Metro/Babel qui en a besoin

---

## Note globale : **5/10**

Le projet a le minimum (`strict: true`) mais manque toutes les options post-strict qui font la différence entre "ça compile" et "c'est fiable".

---

## Version améliorée complète du tsconfig.json

### Proposition : tsconfig de base partagé

> Créer un fichier `tsconfig.base.json` à la racine, chaque projet l'étend via `extends`.

#### `/tsconfig.base.json`

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
    "verbatimModuleSyntax": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "resolveJsonModule": true
  }
}
```

#### `/apps/web/tsconfig.json`

```json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": false,
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

#### `/apps/mobile/tsconfig.json`

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

#### `/packages/ui/tsconfig.json`

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

#### `/packages/utils/tsconfig.json` et `/packages/shared-types/tsconfig.json`

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

---

## Plan d'action prioritaire

### 🔴 Critique

| # | Action | Fichiers | Justification |
|---|---|---|---|
| 1 | Ajouter `useUnknownInCatchVariables` | Tous | `catch(e: any)` est un trou de sécurité béant |
| 2 | Ajouter `noUncheckedIndexedAccess` | Tous | Les tableaux React sans protection = crash potentiel |
| 3 | Ajouter `noFallthroughCasesInSwitch` | Tous | Bugs silencieux faciles à introduire |
| 4 | Ajouter `forceConsistentCasingInFileNames` | apps/web, apps/mobile | Bugs cross-platform en CI |
| 5 | Ajouter `isolatedModules` | mobile, packages/ui, packages/utils, shared-types | Nécessaire pour SWC/Babel/Metro |
| 6 | Supprimer `allowJs: true` ou le conditionner | apps/web | JS non typé dans codebase TS |

### 🟡 Important

| # | Action | Fichiers | Justification |
|---|---|---|---|
| 7 | Ajouter `noImplicitOverride` | Tous | Protection refactor héritage |
| 8 | Ajouter `noImplicitReturns` | Tous | `undefined` retourné silencieusement |
| 9 | Ajouter `noUnusedLocals` | Tous | Code mort |
| 10 | Ajouter `noUnusedParameters` | Tous | Paramètres oubliés |
| 11 | Créer `tsconfig.base.json` | Racine | Élimine la duplication entre les 5 fichiers |

### 🟢 Amélioration

| # | Action | Fichiers | Justification |
|---|---|---|---|
| 12 | Monter `target` de ES2017 → ES2022 | apps/web | ES2022 supporté partout en 2026 |
| 13 | Ajouter `verbatimModuleSyntax` | Packages | Bonne pratique pour les librairies |
| 14 | Ajouter `exactOptionalPropertyTypes` | Tous | Cohérence des props optionnelles (migration) |
| 15 | Ajouter `noPropertyAccessFromIndexSignature` | Tous | Protection accès index |
| 16 | Envisager une CI avec `skipLibCheck: false` périodique | CI | Vérifier les types des dépendances |

---

**Rappel** : L'activation de `noUncheckedIndexedAccess`, `noUnusedLocals` et `noImplicitReturns` va probablement générer des centaines d'erreurs dans une base existante. Procéder par étapes :
1. D'abord ajouter les flags "sûrs" (ceux qui ne cassent presque rien) : `noFallthroughCasesInSwitch`, `noImplicitOverride`, `useUnknownInCatchVariables`
2. Puis `isolatedModules` + `verbatimModuleSyntax` dans les packages
3. Puis `noImplicitReturns` + `noUnusedLocals` + `noUnusedParameters` en corrigeant au fur et à mesure
4. Enfin `noUncheckedIndexedAccess` (le plus perturbant)
