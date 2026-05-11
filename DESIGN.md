# Design.md — AI Fashion Visualization Platform

---

## Direction artistique

### Identité visuelle

**Nom produit** : VFS — Virtual Fashion Studio

**Territoire** : Luxe technologique. Pas une app "filtre Instagram". Pas un dashboard SaaS générique. Un **studio de mode digitalisé** : sophistication, précision, prestance.

**Références visuelles** :
- Interfaces Maison Margiela × Nothing Phone (materialité + tech brut)
- Editorial Dazed & Confused (photographie audacieuse, typographie forte)
- Dashboard Linear (UX précis, densité contrôlée)
- Bottega Veneta digital (luxe sans logo, matière avant tout)

**Anti-références** (à éviter absolument) :
- Gradients violets IA génériques
- Cards blanches avec ombres douces partout
- Illustrations 3D plastiques type Notion/Lottie
- Typographie "clean SaaS" (Inter, DM Sans)

### Style global

**Esthétique** : *Dark luxury editorial* avec accents chauds.

```
Ambiance : Studio photo de nuit. Spots directionnels. 
           Matières texturées. Sophistication industrielle.
           Noir profond → contrastes forts → détails précis.
```

**Ton produit** :
- Confiant, direct, jamais condescendant
- Professionnel avec une touche d'exclusivité
- Copy court, percutant (pas de "Découvrez notre incroyable solution IA")
- Microcopy utile : "15 crédits restants" pas "Vous avez presque épuisé votre solde"

---

## Design system

### Palette couleurs

Deux thèmes complets. Les accents de marque (or, terracotta, sauge) restent identiques dans les deux modes — seule l'infrastructure tonale change.

#### Implémentation

```css
/* ─── DARK MODE (défaut) ──────────────────────────────────── */
:root,
[data-theme="dark"] {
  /* Backgrounds */
  --bg-base:        #0A0A0A;   /* Noir absolu — fond principal */
  --bg-surface:     #111111;   /* Surfaces cards, panels */
  --bg-elevated:    #1A1A1A;   /* Dropdowns, modales */
  --bg-overlay:     #222222;   /* Hover states, inputs */

  /* Borders */
  --border-subtle:  #1F1F1F;   /* Séparateurs discrets */
  --border-default: #2E2E2E;   /* Borders cards */
  --border-strong:  #444444;   /* Borders inputs focus */

  /* Text */
  --text-primary:   #F5F0E8;   /* Blanc chaud — titres, body */
  --text-secondary: #9A9185;   /* Labels, descriptions */
  --text-tertiary:  #5C5650;   /* Placeholders, disabled */
  --text-inverse:   #0A0A0A;   /* Sur fonds clairs */

  /* Shadows */
  --shadow-sm:  0 1px 2px rgba(0,0,0,0.4);
  --shadow-md:  0 4px 12px rgba(0,0,0,0.5);
  --shadow-lg:  0 12px 32px rgba(0,0,0,0.6);
  --shadow-xl:  0 24px 64px rgba(0,0,0,0.7);
  --glow-gold:  0 0 24px rgba(212,168,83,0.15);
}

/* ─── LIGHT MODE ─────────────────────────────────────────── */
[data-theme="light"] {
  /* Backgrounds */
  --bg-base:        #F7F4EF;   /* Blanc crème chaud — jamais blanc pur */
  --bg-surface:     #FFFFFF;   /* Surfaces cards, panels */
  --bg-elevated:    #F0EDE8;   /* Dropdowns, modales */
  --bg-overlay:     #E8E4DE;   /* Hover states, inputs */

  /* Borders */
  --border-subtle:  #E4E0DA;   /* Séparateurs discrets */
  --border-default: #D5D0C8;   /* Borders cards */
  --border-strong:  #A8A29A;   /* Borders inputs focus */

  /* Text */
  --text-primary:   #1A1714;   /* Noir chaud — titres, body */
  --text-secondary: #6B6560;   /* Labels, descriptions */
  --text-tertiary:  #A8A29A;   /* Placeholders, disabled */
  --text-inverse:   #F7F4EF;   /* Sur fonds sombres */

  /* Shadows — plus légères en light */
  --shadow-sm:  0 1px 3px rgba(26,23,20,0.08);
  --shadow-md:  0 4px 12px rgba(26,23,20,0.10);
  --shadow-lg:  0 12px 32px rgba(26,23,20,0.12);
  --shadow-xl:  0 24px 64px rgba(26,23,20,0.14);
  --glow-gold:  0 0 24px rgba(180,130,40,0.12);
}

/* ─── ACCENTS — identiques dark & light ─────────────────── */
:root,
[data-theme="dark"],
[data-theme="light"] {
  /* Brand accent */
  --accent-primary: #D4A853;   /* Or chaud — CTA, highlights */
  --accent-warm:    #C8956A;   /* Terracotta — secondaire */
  --accent-cool:    #6B8F8A;   /* Vert sauge — succès, badges */

  /* Status */
  --status-success: #4A7C59;
  --status-warning: #C4873A;
  --status-error:   #8B3A3A;
  --status-info:    #3A5F8B;

  /* Generation states */
  --gen-queued:     #9A9185;
  --gen-processing: #D4A853;
  --gen-done:       #4A7C59;
  --gen-error:      #8B3A3A;
}

/* ─── RESPECTS PRÉFÉRENCE SYSTÈME ──────────────────────── */
/* Appliqué uniquement si aucun data-theme n'est explicitement posé */
@media (prefers-color-scheme: light) {
  :root:not([data-theme]) {
    --bg-base:        #F7F4EF;
    --bg-surface:     #FFFFFF;
    --bg-elevated:    #F0EDE8;
    --bg-overlay:     #E8E4DE;
    --border-subtle:  #E4E0DA;
    --border-default: #D5D0C8;
    --border-strong:  #A8A29A;
    --text-primary:   #1A1714;
    --text-secondary: #6B6560;
    --text-tertiary:  #A8A29A;
    --text-inverse:   #F7F4EF;
    --shadow-sm:  0 1px 3px rgba(26,23,20,0.08);
    --shadow-md:  0 4px 12px rgba(26,23,20,0.10);
    --shadow-lg:  0 12px 32px rgba(26,23,20,0.12);
    --shadow-xl:  0 24px 64px rgba(26,23,20,0.14);
    --glow-gold:  0 0 24px rgba(180,130,40,0.12);
  }
}
```

#### Tableau comparatif des tokens

| Token | Dark | Light | Usage |
|---|---|---|---|
| `--bg-base` | `#0A0A0A` | `#F7F4EF` | Fond global de page |
| `--bg-surface` | `#111111` | `#FFFFFF` | Cards, panels |
| `--bg-elevated` | `#1A1A1A` | `#F0EDE8` | Dropdowns, modales |
| `--bg-overlay` | `#222222` | `#E8E4DE` | Hover, inputs |
| `--border-default` | `#2E2E2E` | `#D5D0C8` | Borders cards |
| `--text-primary` | `#F5F0E8` | `#1A1714` | Titres, body |
| `--text-secondary` | `#9A9185` | `#6B6560` | Labels, captions |
| `--accent-primary` | `#D4A853` | `#D4A853` | CTA, highlights |
| `--status-error` | `#8B3A3A` | `#8B3A3A` | Erreurs |

#### Toggle thème — implémentation Next.js

```typescript
// hooks/use-theme.ts
import { useEffect, useState } from 'react'

type Theme = 'dark' | 'light' | 'system'

export function useTheme() {
  const [theme, setTheme] = useState<Theme>('system')

  useEffect(() => {
    const stored = localStorage.getItem('vfs-theme') as Theme | null
    if (stored) setTheme(stored)
  }, [])

  useEffect(() => {
    const root = document.documentElement
    if (theme === 'system') {
      root.removeAttribute('data-theme')
    } else {
      root.setAttribute('data-theme', theme)
    }
    if (theme !== 'system') localStorage.setItem('vfs-theme', theme)
  }, [theme])

  return { theme, setTheme }
}
```

```typescript
// components/ui/theme-toggle.tsx
// Toggle 3 états : dark → light → system
// Icônes : Moon / Sun / Monitor
// Placement : bas sidebar desktop, Settings mobile
// Transition : opacity + scale 150ms sur changement icône
```

#### Règles d'adaptation light mode

```
Images générées    : pas d'adaptation nécessaire (contenu)
Skeleton loader    : bg #E8E4DE → shimmer vers #D5D0C8
Overlays images    : gradient rgba(247,244,239,0.85) au lieu de rgba(0,0,0,0.85)
Bouton primary     : même or (#D4A853), texte inverse (#F7F4EF)
Focus ring         : outline #D4A853 identique aux deux modes
Scrollbar custom   : track --bg-elevated, thumb --border-strong
```

### Typographie

```css
/* Display — Titres majeurs, hero */
--font-display: 'Canela', 'Freight Display', Georgia, serif;
/* → Caractère éditorial, luxe, contraste fort avec tech */

/* Heading — Sections, cards */
--font-heading: 'Suisse Int'l Mono', 'JetBrains Mono', monospace;
/* → Ancrage technique, précision, caractère unique */

/* Body — Texte courant */
--font-body: 'Söhne', 'Aktiv Grotesk', 'Helvetica Neue', sans-serif;
/* → Lisibilité maximale, neutre sans être générique */

/* Mono — Code, IDs, données */
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;

/* Scale typographique */
--text-xs:    0.6875rem;   /* 11px — labels très petits */
--text-sm:    0.8125rem;   /* 13px — captions, metadata */
--text-base:  0.9375rem;   /* 15px — body text */
--text-md:    1.0625rem;   /* 17px — body large */
--text-lg:    1.25rem;     /* 20px — headings petits */
--text-xl:    1.5rem;      /* 24px — headings */
--text-2xl:   2rem;        /* 32px — titres sections */
--text-3xl:   2.75rem;     /* 44px — titres pages */
--text-4xl:   3.75rem;     /* 60px — hero */
--text-5xl:   5rem;        /* 80px — display majeur */

/* Line heights */
--leading-tight:  1.1;
--leading-snug:   1.3;
--leading-normal: 1.5;
--leading-relaxed: 1.7;

/* Letter spacing */
--tracking-tight:  -0.03em;
--tracking-normal:  0;
--tracking-wide:    0.08em;
--tracking-widest:  0.2em;  /* Majuscules labels */
```

### Spacing

```css
/* Base 4px */
--space-1:  0.25rem;   /* 4px */
--space-2:  0.5rem;    /* 8px */
--space-3:  0.75rem;   /* 12px */
--space-4:  1rem;      /* 16px */
--space-5:  1.25rem;   /* 20px */
--space-6:  1.5rem;    /* 24px */
--space-8:  2rem;      /* 32px */
--space-10: 2.5rem;    /* 40px */
--space-12: 3rem;      /* 48px */
--space-16: 4rem;      /* 64px */
--space-20: 5rem;      /* 80px */
--space-24: 6rem;      /* 96px */
--space-32: 8rem;      /* 128px */
```

### Grid system

```css
/* Desktop */
--grid-columns: 12;
--grid-gutter:  var(--space-6);   /* 24px */
--grid-margin:  var(--space-8);   /* 32px */
--grid-max:     1440px;

/* Tablet */
@media (max-width: 1024px) {
  --grid-columns: 8;
  --grid-gutter:  var(--space-4);
  --grid-margin:  var(--space-6);
}

/* Mobile */
@media (max-width: 640px) {
  --grid-columns: 4;
  --grid-gutter:  var(--space-3);
  --grid-margin:  var(--space-4);
}
```

### Radius

```css
/* Invariants dark & light */
--radius-sm:   2px;
--radius-md:   6px;
--radius-lg:   12px;
--radius-xl:   20px;
--radius-full: 9999px;
```

> Les tokens `--shadow-*` et `--glow-gold` sont définis par thème dans la section Palette couleurs ci-dessus (intensité adaptée selon le fond).

---

## UX

### Principes UX

1. **Zéro friction upload** : drag & drop partout, preview immédiate
2. **Feedback temps réel** : l'utilisateur sait toujours où en est sa génération
3. **Progressive disclosure** : fonctions avancées cachées jusqu'à pertinence
4. **Wow first** : le premier résultat doit couper le souffle — c'est le moment de rétention clé
5. **Erreurs utiles** : jamais "Une erreur est survenue". Toujours : ce qui a échoué + action suggérée

### Navigation globale

```
Sidebar gauche (desktop) :
├── Logo VFS
├── Studio          [icône caméra]
├── Dressing        [icône cintre]
├── AI Stylist      [icône étoile]  — badge "Pro"
├── ─────────────
├── Crédits         [badge solde]
└── Settings / Profile

Top bar (mobile) :
├── Logo
├── [icône Studio] [icône Dressing] [icône Stylist]
└── Avatar → menu
```

### Onboarding

```
Étape 1 : "Votre studio en 3 photos"
  → Upload 3 photos (pas 1, pour qualité)
  → Guidance : "Face, 3/4, corps entier"
  → Progress dots visuels

Étape 2 : "Choisissez votre premier vêtement"
  → Catalogue des vêtements démo (pre-loaded)
  → Pas de formulaire, action directe

Étape 3 : Génération automatique
  → "Nous préparons votre look..." avec animation
  → Résultat affiché immédiatement
  → "Télécharger" → créer compte si non connecté (gate post-wow)
```

**Logique clé** : le "wow" arrive AVANT la création de compte.

### Accessibilité

- Contraste minimum 4.5:1 (WCAG AA) pour tout texte body
- Contraste minimum 3:1 pour texte large et éléments UI
- Navigation clavier complète (Tab, Enter, Escape, Arrow keys)
- Focus visible : outline 2px `var(--accent-primary)`, offset 2px
- ARIA labels sur tous les éléments interactifs non-textuels
- `role="status"` sur les zones de progress/status jobs
- `aria-live="polite"` pour les notifications toast
- Tailles cibles min : 44x44px mobile
- Pas de contenu exclusif couleur (toujours icône + couleur)

---

## Pages & écrans

### Landing Page

**Objectif** : Convertir en inscription. Démontrer la qualité visuellement.

**Composants** :
```
Hero :
  ├── Headline : "Votre shooting photo en 60 secondes."
  ├── Sous-titre : 1 ligne, factuel
  ├── Demo interactive : avant/après slider
  └── CTA : "Essayer gratuitement — 10 crédits offerts"

Social proof :
  └── Logos marques (si disponibles) ou chiffres clés

Feature grid :
  ├── Try-On Photo
  ├── Vidéo défilé
  ├── AI Stylist
  └── Dashboard marque

Pricing preview :
  └── 3 colonnes (Free / Pro / Brand)

Footer minimal
```

**États** : Pas d'état vide (landing toujours pleine).

**Responsive** :
- Mobile : hero stack vertical, demo plein écran, CTA sticky bottom

---

### Studio Page (cœur)

**Objectif** : Générer un try-on de la façon la plus fluide possible.

**Layout desktop** :
```
┌────────────────────────────────────────────────────────┐
│ Sidebar nav (240px)  │  Canvas principal (flex-grow)    │
│                      │                                  │
│                      │  ┌─────────────┬──────────────┐  │
│                      │  │ Photo zone  │ Vêtement zone│  │
│                      │  │             │              │  │
│                      │  │  [Ma photo] │  [Vêtement]  │  │
│                      │  │             │              │  │
│                      │  └─────────────┴──────────────┘  │
│                      │                                  │
│                      │  ┌──────────────────────────────┐ │
│                      │  │ Paramètres : catégorie, style│ │
│                      │  └──────────────────────────────┘ │
│                      │                                  │
│                      │  [Générer — 1 crédit]            │
│                      │                                  │
│                      │  ─────── Résultat ───────        │
│                      │  ┌──────────────────────────────┐ │
│                      │  │  [Image générée / loader]    │ │
│                      │  │  [Télécharger] [Vidéo] [+]   │ │
│                      │  └──────────────────────────────┘ │
└──────────────────────┴──────────────────────────────────┘
```

**États** :
```
Vide      : "Uploadez votre photo et choisissez un vêtement"
Loading   : Barre progression + étapes texte ("Analyse du vêtement...")
Résultat  : Image + boutons actions
Erreur    : Message + bouton réessayer + remboursement crédit affiché
```

**Responsive mobile** :
- Step-by-step vertical (photo → vêtement → génération → résultat)
- CTA sticky bottom pendant génération

---

### Dressing Page

**Objectif** : Galerie de tous les try-ons, organisation en collections.

**Layout** :
```
Header : filtres (catégorie, date, marque, favoris)
Body   : grille 3 colonnes desktop, 2 mobile, 1 small mobile
         Cards : image 1:1, hover → actions (télécharger, ajouter collection, supprimer)
Sidebar : Collections (list) — desktop uniquement
```

**États** :
- Vide : illustration + "Créez votre premier look" → redirect Studio
- Loading : skeleton cards
- Erreur : retry

---

### AI Stylist Page

**Objectif** : Afficher les conseils personnalisés, recommandations outfits.

**Layout** :
```
Profil résumé (photos, morphologie détectée)
──────────────────────────────────────
"Mes recommandations"
  Cards conseils : [vêtement] + texte conseil + fit score
──────────────────────────────────────
"Outfits suggérés"
  Grid looks complets : 3 items par outfit
──────────────────────────────────────
Feedback : [👍 Utile] [👎 Pas vraiment]
```

---

### Brand Dashboard

**Objectif** : Vision complète analytique + gestion catalogue.

**Layout** :
```
Topbar    : Brand name, plan badge, crédits restants
──────────────────────────────────────────────────
KPI row   : [Try-ons] [Conversion] [Retours évités] [Économies]
            (4 cards avec delta vs mois précédent)
──────────────────────────────────────────────────
Charts    : [Try-ons/semaine lineChart] [Top SKUs barChart]
──────────────────────────────────────────────────
Catalogue : Table SKUs avec miniatures, statut, nb try-ons
──────────────────────────────────────────────────
Actions   : [Ajouter produit] [Importer CSV] [Shopify sync]
```

---

## Composants UI

### Boutons

```
Variants :
├── primary    : bg --accent-primary, text --text-inverse
│               hover: brightness(1.1), active: scale(0.98)
├── secondary  : border --border-default, text --text-primary
│               hover: bg --bg-overlay
├── ghost      : text --text-secondary
│               hover: text --text-primary
├── destructive: text --status-error, border --status-error
└── loading    : spinner remplace icône left, disabled state

Tailles :
├── sm : h-8, px-3, text-sm
├── md : h-10, px-4, text-base  (défaut)
└── lg : h-12, px-6, text-md

Règle : toujours icône left OU right, jamais les deux.
```

### Formulaires

```
Input :
├── bg --bg-surface
├── border --border-default
├── focus: border --border-strong + shadow 0 0 0 2px rgba(212,168,83,0.2)
├── placeholder : --text-tertiary
├── error : border --status-error + message rouge dessous
└── disabled : opacity 0.4, cursor not-allowed

Label : au-dessus, --text-secondary, text-sm, tracking-widest, majuscules

Validation :
├── Temps réel sur blur (pas sur change)
└── Message : icon + texte, couleur status
```

### Cards

```
Base :
├── bg --bg-surface
├── border --border-default
├── radius --radius-lg
├── padding --space-6
└── hover : border --border-strong, shadow --shadow-md

Card génération (résultat try-on) :
├── Image pleine (aspect-ratio: 3/4)
├── Overlay bottom gradient : actions (download, video, save)
├── Badge status (coin haut-droit)
└── hover : overlay visible
```

### Progress / Loading états

```
Job progress bar :
├── Track : --bg-elevated, height 2px
├── Fill : --accent-primary, transition smooth
├── Texte dessous : étape courante (monospace, text-xs)
└── Animation : shimmer sur fill pendant processing

Skeleton :
├── bg --bg-elevated
├── animation: shimmer gradient left-right 1.5s infinite
└── Même shape que le contenu final (image skeleton → 3/4 ratio)

Spinner :
├── Cercle 16px ou 24px
├── border --border-default, border-top --accent-primary
└── rotation 0.8s linear infinite
```

### Notifications / Toast

```
Position : bottom-right desktop, top mobile (sous header)
Max visible : 3 simultanés (stack)

Variants :
├── success : border-left 3px --status-success
├── error   : border-left 3px --status-error
├── info    : border-left 3px --accent-primary
└── warning : border-left 3px --status-warning

Anatomy :
├── Icône (16px)
├── Titre (text-sm, font-medium)
├── Message optionnel (text-xs, --text-secondary)
└── Bouton close (x)

Durée : success 3s, error 6s, info 4s (auto-dismiss)
Animation : slide-in depuis droite, fade-out
```

### Upload Zone

```
États :
├── Default  : border-dashed --border-default, texte centré
├── Hover    : border --accent-primary, bg --bg-overlay
├── Drag-over: border --accent-primary, bg rgba(212,168,83,0.05)
├── Has file : preview image + bouton remplacer
└── Error    : border --status-error, message

Anatomy default :
├── Icône upload (24px, --text-tertiary)
├── "Glissez votre photo ici"
├── "ou cliquez pour sélectionner"
└── Formats acceptés (text-xs, --text-tertiary)
```

---

## Responsive design

### Breakpoints

```css
--bp-sm:  640px;   /* Mobile landscape */
--bp-md:  768px;   /* Tablet portrait */
--bp-lg:  1024px;  /* Tablet landscape / petit desktop */
--bp-xl:  1280px;  /* Desktop standard */
--bp-2xl: 1440px;  /* Desktop large */
```

### Adaptation par composant

| Composant | Mobile | Tablet | Desktop |
|---|---|---|---|
| Navigation | Bottom bar | Sidebar collapsed | Sidebar expanded |
| Studio | Steps verticaux | 2 colonnes | 2 colonnes + panneau résultat |
| Dressing | 1 col | 2 col | 3 col + sidebar collections |
| Dashboard | Stack vertical, charts plein écran | 2 col charts | 4 KPIs + 2 charts |
| Cards vêtements | 2 col | 3 col | 4 col |

---

## Animations & interactions

### Philosophie animation

```
Vitesse standard : 200ms (micro), 300ms (transitions), 500ms (entrées majeures)
Easing : cubic-bezier(0.16, 1, 0.3, 1) — ease-out spring
Pas d'animation > 600ms (frustrant)
Pas d'animation purement décorative si pas de sens UX
```

### Animations clés

```css
/* Entrée card */
@keyframes card-in {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Résultat génération (moment wow) */
@keyframes result-reveal {
  0%   { opacity: 0; transform: scale(0.96); filter: blur(8px); }
  60%  { filter: blur(0); }
  100% { opacity: 1; transform: scale(1); }
}
/* duration: 600ms, easing: ease-out */

/* Progress pulse */
@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 0 0 rgba(212,168,83,0); }
  50%       { box-shadow: 0 0 12px 2px rgba(212,168,83,0.3); }
}

/* Shimmer skeleton */
@keyframes shimmer {
  from { background-position: -200% 0; }
  to   { background-position: 200% 0; }
}
```

### Micro-interactions

```
Bouton CTA       : scale(0.97) on active, return 150ms spring
Upload zone      : border color transition 200ms + bg fade
Job status badge : couleur transition 300ms (queued→gold→green)
Crédit balance   : count-up animation sur changement
Image hover      : scale(1.02) + overlay fade, 200ms
Sidebar items    : bg slide-in left, 150ms
```

### Transition de page

```
Navigation : fade 150ms + translateX(8px) sortant
Modales    : backdrop fade 200ms + contenu scale 0.95→1 + fade 250ms
Drawer     : slide depuis droite/bas selon contexte
```

---

## Accessibilité

### Contraste

```
Texte body sur bg-base   : #F5F0E8 / #0A0A0A = 18.7:1 ✓
Texte secondary sur base : #9A9185 / #0A0A0A = 5.8:1  ✓
Accent primary sur base  : #D4A853 / #0A0A0A = 7.2:1  ✓
Accent sur bg-surface    : #D4A853 / #111111 = 6.8:1  ✓
```

### Focus management

```css
/* Focus visible global */
:focus-visible {
  outline: 2px solid var(--accent-primary);
  outline-offset: 2px;
  border-radius: var(--radius-sm);
}

/* Modales : focus trap */
/* → tabindex sur tous éléments interactifs */
/* → Escape ferme la modale */
/* → Focus retourne à l'élément déclencheur à la fermeture */
```

### ARIA patterns

```html
<!-- Job progress -->
<div role="status" aria-label="Génération en cours" aria-live="polite">
  <progress value="65" max="100" aria-valuenow="65">65%</progress>
  <span>Analyse du vêtement...</span>
</div>

<!-- Upload zone -->
<div 
  role="button" 
  tabindex="0"
  aria-label="Uploader votre photo. Formats acceptés : JPEG, PNG, WebP"
  aria-dropeffect="copy"
>

<!-- Toast -->
<div role="alert" aria-live="assertive" aria-atomic="true">
  <span>Look généré avec succès</span>
</div>
```

---

## Design engineering

### Structure Figma

```
VFS — Design System
├── 🎨 Foundations
│   ├── Colors
│   ├── Typography
│   ├── Spacing
│   ├── Shadows
│   └── Icons
├── 🧩 Components
│   ├── Buttons
│   ├── Forms
│   ├── Cards
│   ├── Navigation
│   ├── Overlays
│   ├── Upload
│   ├── Progress
│   └── Data display
├── 📐 Templates
│   ├── Studio
│   ├── Dressing
│   ├── Brand Dashboard
│   └── Landing
└── 📱 Flows
    ├── Onboarding
    ├── Generation
    └── Brand Setup
```

### Design tokens (CSS vars → Tailwind)

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        'bg-base':      'var(--bg-base)',
        'bg-surface':   'var(--bg-surface)',
        'accent':       'var(--accent-primary)',
        'text-primary': 'var(--text-primary)',
        // ...
      },
      fontFamily: {
        display: ['Canela', 'Georgia', 'serif'],
        heading:  ['Suisse Int\'l Mono', 'monospace'],
        body:     ['Söhne', 'Helvetica Neue', 'sans-serif'],
      },
      animation: {
        'card-in':       'card-in 300ms ease-out',
        'result-reveal': 'result-reveal 600ms ease-out',
        'shimmer':       'shimmer 1.5s infinite',
      }
    }
  }
}
```

### Conventions composants frontend

```typescript
// Naming
ComponentName.tsx          // PascalCase
use-component-name.ts      // kebab-case pour hooks
component-name.stories.tsx // Storybook si applicable

// Structure composant
interface Props {
  // Props typées strictement
  // Pas de prop "any" jamais
}

export function ComponentName({ prop1, prop2 }: Props) {
  // 1. Hooks
  // 2. Handlers
  // 3. Computed values
  // 4. Return JSX
}

// Variants via cva() (class-variance-authority)
const buttonVariants = cva(
  "base-classes",
  {
    variants: {
      variant: { primary: "...", secondary: "..." },
      size:    { sm: "...", md: "...", lg: "..." },
    },
    defaultVariants: { variant: "primary", size: "md" }
  }
)
```

---

## Inspirations UI

### Références directes

| Référence | Ce qu'on emprunte |
|---|---|
| **Linear** | Densité information, navigation sidebar, raccourcis clavier |
| **Vercel Dashboard** | Tables de données, status badges, dark theme épuré |
| **Arc Browser** | Micro-interactions, transitions fluides |
| **Cron** | Typographie éditoriale dans interface produit |
| **Raycast** | Commande palette, vitesse perçue, feedbacks instantanés |
| **Loewe.com** | Luxe éditorial, photographie dominante, typographie majuscules |
| **Acne Studios** | Minimalisme luxe, grille photo, blanc/noir + accent couleur |

### Ce qui rend VFS mémorable

1. **L'animation de révélation** : le résultat try-on n'apparaît pas — il se *matérialise*, comme une photo qui sort du bain révélateur.
2. **La typographie serif sur dark** : inattendu dans un produit tech, immédiatement premium.
3. **L'or comme accent** : dosé, pas criard. Présent sur les CTA et les états actifs uniquement.
4. **La densité contrôlée** : pas de whitespace excessif façon landing générique. L'interface est un studio de travail.
5. **Les uploads comme ritual** : drag & drop avec feedback sensoriel (son optionnel, animation physique).
