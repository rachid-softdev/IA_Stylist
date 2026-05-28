# architecture.md — AI Fashion Visualization Platform

---

## Vue globale

### Concept architectural

Architecture **monorepo hybride** : frontend Next.js déployé sur Vercel, backend Python FastAPI sur Railway/Render, services GPU externalisés via fal.ai / Replicate, stockage Cloudflare R2, base de données PostgreSQL managée (Supabase ou Neon).

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  Web App     │  │  Mobile App  │  │  Brand Dashboard (B2B)   │  │
│  │  Next.js 14  │  │  Expo RN     │  │  Next.js / same codebase │  │
│  └──────┬───────┘  └──────┬───────┘  └────────────┬─────────────┘  │
└─────────┼─────────────────┼───────────────────────┼────────────────┘
          │                 │                       │
          └─────────────────┴───────────────────────┘
                            │ HTTPS / WS
┌───────────────────────────▼─────────────────────────────────────────┐
│                        API GATEWAY                                  │
│            FastAPI — Python 3.12 — Railway                          │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────────────┐ │
│  │ Auth       │ │ Users      │ │ Try-On     │ │ Brands / Shopify │ │
│  │ /auth/*    │ │ /users/*   │ │ /generate/*│ │ /brands/*        │ │
│  └────────────┘ └────────────┘ └─────┬──────┘ └──────────────────┘ │
└──────────────────────────────────────┼──────────────────────────────┘
                                       │
         ┌─────────────────────────────┼──────────────────────────┐
         │                   SERVICES LAYER                        │
         │  ┌───────────────┐   ┌──────▼──────┐  ┌────────────┐  │
         │  │  Job Queue    │   │  GPU Router │  │  Webhook   │  │
         │  │  Redis/BullMQ │◄──│  (fal/repl) │  │  Handler   │  │
         │  └───────┬───────┘   └─────────────┘  └────────────┘  │
         └──────────┼──────────────────────────────────────────────┘
                    │
    ┌───────────────┼──────────────────────────────────┐
    │         EXTERNAL AI SERVICES                     │
    │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
    │  │ fal.ai   │ │Replicate │ │ Kling / Seedance  │ │
    │  │ FLUX     │ │ IDM-VTON │ │ (vidéo)           │ │
    │  │ CatVTON  │ │ InstantID│ │                   │ │
    │  └──────────┘ └──────────┘ └──────────────────┘  │
    └──────────────────────────────────────────────────┘
         │
┌────────┼────────────────────────────────────────────────────────────┐
│                     DATA LAYER                                      │
│  ┌─────▼──────┐  ┌────────────┐  ┌──────────┐  ┌────────────────┐  │
│  │ PostgreSQL │  │ Redis      │  │ R2/S3    │  │ Supabase Auth  │  │
│  │ (Neon)     │  │ (Upstash)  │  │ (fichiers│  │                │  │
│  │            │  │            │  │  media)  │  │                │  │
│  └────────────┘  └────────────┘  └──────────┘  └────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
```

### Flux de données — Génération Try-On

```
User Upload Photo + Vêtement
        │
        ▼
Frontend valide (taille, format, résolution min)
        │
        ▼
POST /generate/try-on  ──► Auth Check ──► Credit Check
        │
        ▼
Upload fichiers ──► R2/S3 (URLs signées)
        │
        ▼
Job créé en DB (status: pending) ──► Redis Queue
        │
        ▼
Worker Python récupère job
        │
        ├──► Image: fal.ai (IDM-VTON / CatVTON / FLUX)
        └──► Video: Kling API / Seedance
        │
        ▼
Résultat stocké R2 ──► DB updated (status: done, url)
        │
        ▼
WebSocket push ──► Frontend affiche résultat
        │
        ▼
Déduction crédit utilisateur
```

---

## Stack technique

### Frontend

| Technologie | Rôle | Justification |
|---|---|---|
| Next.js 14 (App Router) | Framework principal | SSR/SSG, RSC, routing, API routes intégrées |
| TypeScript | Typage | Maintenabilité, DX, erreurs au build |
| Tailwind CSS v3 | Styling | Utility-first, performance, pas de runtime CSS |
| Framer Motion | Animations | Qualité animation, API déclarative |
| Zustand | State management | Léger, simple, pas de boilerplate Redux |
| React Query (TanStack) | Data fetching | Cache, retry, loading states automatiques |
| Expo (React Native) | Mobile | Code sharing logique métier avec web |
| shadcn/ui | Composants base | Accessible, customisable, pas de dépendance lock-in |

### Backend

| Technologie | Rôle | Justification |
|---|---|---|
| Python 3.12 | Runtime | Écosystème IA natif, performance suffisante |
| FastAPI | Framework | Async natif, auto-doc OpenAPI, typage Pydantic |
| Pydantic v2 | Validation | Rapide, typage strict, sérialisation |
| SQLAlchemy 2.0 | ORM | Async, migrations Alembic, requêtes complexes |
| Celery + Redis | Job Queue | Workers async GPU, retry, priorité |
| httpx | HTTP client | Async, appels API externes |

### Base de données

| Service | Usage | Free tier |
|---|---|---|
| Neon (PostgreSQL) | DB principale | 0.5 GB, autoscale à 0 |
| Upstash Redis | Cache + Queue | 10k req/jour free |
| Supabase Auth | Authentification | Gratuit jusqu'à 50k users |

**Neon** préféré à Supabase DB pour le contrôle SQL pur et l'autoscaling.

### Stockage fichiers

**Cloudflare R2** :
- 10 GB stockage gratuit
- 0 frais d'egress (critique pour images/vidéos)
- Compatible S3 API
- CDN intégré via Cloudflare

Structure buckets :
```
r2-bucket/
├── uploads/raw/{user_id}/{uuid}.{ext}     # Photos utilisateur (temp 24h)
├── outputs/images/{job_id}/{uuid}.webp    # Try-on générés
├── outputs/videos/{job_id}/{uuid}.mp4    # Vidéos générées
├── assets/garments/{brand_id}/{sku}.png  # Vêtements marques
└── avatars/{user_id}/profile.webp        # Photos profil
```

### Authentification

**Supabase Auth** avec JWT :
- Email/password + OAuth (Google, Apple)
- JWT stocké en httpOnly cookie (pas localStorage)
- Refresh tokens automatiques
- Row Level Security PostgreSQL natif

### Cache

```
L1 : In-memory Next.js (RSC cache, fetch cache)
L2 : Upstash Redis (sessions, résultats jobs, rate limiting)
L3 : Cloudflare CDN (assets statiques, images outputs)
```

TTL strategy :
```
Sessions         → 7 jours
Job results      → 30 jours
User profile     → 5 minutes
Brand catalog    → 1 heure
Rate limit keys  → fenêtre glissante 1h
```

### Queue / Jobs

**Celery + Redis (Upstash)** :
```
Queues prioritaires :
├── high    : génération premium, temps réel
├── default : génération standard
└── low     : batch processing, exports, analytics
```

Workers déployés sur Railway avec autoscaling selon longueur de queue.

### Monitoring & Analytics

| Outil | Usage | Coût |
|---|---|---|
| Sentry | Error tracking frontend/backend | Free 5k events/mois |
| Axiom | Logs centralisés | Free 500MB/jour |
| Posthog | Analytics produit | Free 1M events/mois |
| Uptime Robot | Monitoring uptime | Free 50 monitors |
| Railway Metrics | Infra CPU/RAM | Inclus |

### WebSocket / Realtime

**Supabase Realtime** pour les updates de jobs :
- Push du statut job (pending → processing → done)
- Pas de polling nécessaire
- Fallback polling 3s si WS indisponible

---

## Hébergement

### Comparatif

| Option | Avantages | Inconvénients | Coût |
|---|---|---|---|
| Vercel | DX excellent, CDN global, preview deployments | Serverless cold starts, pricing élevé à scale | ~$20/mois |
| Railway | Simple, full stack, logs intégrés | Moins mature que AWS | ~$10-30/mois |
| Render | Bon free tier, Docker natif | Cold starts free tier | Gratuit → $7/service |
| AWS/GCP | Scale infini, tous services | Complexité, coût opérationnel | Variable |
| Fly.io | Edge global, Docker, latence faible | DX moins smooth | ~$5-20/mois |

### Recommandation finale

```
┌─────────────────────────────────────────────┐
│  FRONTEND   → Vercel (Next.js natif, CDN)   │
│  BACKEND    → Railway (FastAPI + Workers)   │
│  DB         → Neon (PostgreSQL serverless)  │
│  CACHE      → Upstash (Redis serverless)    │
│  STORAGE    → Cloudflare R2                 │
│  AUTH       → Supabase Auth                 │
│  AI COMPUTE → fal.ai + Replicate            │
└─────────────────────────────────────────────┘
```

Coût infra estimé au lancement : **~$50-80/mois** pour 1000 utilisateurs actifs.

---

## Performance

### Stratégie cache

```python
# Backend — décorateur cache Redis
@cache(ttl=3600, key="brand:{brand_id}:catalog")
async def get_brand_catalog(brand_id: str): ...

# Frontend — React Query
const { data } = useQuery({
  queryKey: ['catalog', brandId],
  staleTime: 1000 * 60 * 60, // 1h
  gcTime: 1000 * 60 * 60 * 24,
})
```

### CDN & Images

- Toutes les images output servies via Cloudflare R2 + CDN
- Next.js Image component avec `sizes`, `srcSet` automatique
- Format WebP systématique pour outputs
- Lazy loading natif + Intersection Observer pour galeries
- Skeleton loading pour tous les états de chargement

### Compression

```nginx
# Headers R2/Cloudflare
Content-Encoding: br (Brotli)
Cache-Control: public, max-age=31536000, immutable  # assets
Cache-Control: public, max-age=3600  # outputs générés
```

### Pagination

```
Curseur-based (cursor pagination) pour :
├── Historique générations
├── Catalogue vêtements
└── Dashboard brand analytics

Offset pour :
└── Admin panel (simpler)
```

---

## Sécurité

### Auth & Permissions

```
Rôles :
├── user        : génération, dressing personnel
├── brand_admin : dashboard marque, catalogue, analytics
├── brand_member: lecture dashboard
└── super_admin : accès complet platform
```

### Validation & Protection

```python
# Rate limiting par tier
RATE_LIMITS = {
    "free":    "10/hour",
    "pro":     "100/hour",
    "brand":   "1000/hour",
    "api_key": "10000/day",
}

# Validation fichiers upload
ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]
MAX_SIZE_MB = 10
MIN_RESOLUTION = (512, 512)
```

### Sécurité API

- Toutes routes protégées JWT (sauf /auth/*)
- API keys hashées en DB (bcrypt), préfixe `vfs_live_` / `vfs_test_`
- CORS strict : liste blanche domaines autorisés
- Rate limiting Redis sliding window
- Validation Pydantic sur tous les inputs
- SQL injection impossible via SQLAlchemy ORM
- XSS : Content-Security-Policy strict en headers Next.js
- CSRF : tokens doubles-submit pour mutations sensibles
- Secrets via Railway Env Vars / Vercel Env (jamais en code)

### Backup Strategy

```
PostgreSQL (Neon) : snapshots automatiques 7 jours
R2 Cloudflare    : versioning activé sur bucket outputs
Redis (Upstash)  : persistance AOF
Code             : GitHub, branches protégées
```

---

## DevOps

### CI/CD

```
GitHub Actions :
├── PR → lint + typecheck + tests unitaires
├── merge main → preview deploy Vercel
│              → staging Railway
└── tag release → production deploy automatique
```

### Docker

```dockerfile
# Backend
FROM python:3.12-slim
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Worker Celery
CMD ["celery", "-A", "app.worker", "worker", "--loglevel=info"]
```

### Environnements

```
local       → .env.local, DB locale Docker Compose
staging     → Railway env vars, Neon staging branch
production  → Railway/Vercel env vars, Neon production
```

### Logs & Monitoring

```python
# Structured logging JSON
import structlog
logger = structlog.get_logger()
logger.info("job.started", job_id=job_id, user_id=user_id, model="catvton")
```

- Axiom pour centralisation logs
- Sentry pour erreurs avec contexte user
- Alertes Slack via webhooks (erreurs critiques, queue saturée)

---

## Architecture scalable

### Scaling horizontal

```
Frontend : Vercel auto-scale (serverless, edge functions)
Backend  : Railway réplicas multiples (load balancer intégré)
Workers  : Railway autoscale selon queue length (0→N workers)
DB       : Neon connection pooling (PgBouncer intégré)
Cache    : Upstash Redis cluster
```

### Gestion forte charge

```
1. Queue GPU saturée → file d'attente visible utilisateur
2. Rate limiting par tier → protection abus
3. Circuit breaker fal.ai → fallback Replicate automatique
4. DB connection pool max 20 → PgBouncer absorbe le reste
5. CDN absorbe 95% des requêtes assets/outputs
```

### Séparation services

```
API Server  : routes HTTP, validation, auth → Railway
Workers     : jobs GPU, webhooks            → Railway (séparé)
Scheduler   : cron jobs (cleanup, reports)  → Railway cron
Frontend    : SSR/CSR, edge functions       → Vercel
```

---

## Structure projet

```
virtual-fashion-studio/
├── apps/
│   ├── web/                          # Next.js 14
│   │   ├── app/
│   │   │   ├── (auth)/
│   │   │   │   ├── login/page.tsx
│   │   │   │   └── signup/page.tsx
│   │   │   ├── (app)/
│   │   │   │   ├── studio/page.tsx
│   │   │   │   ├── history/page.tsx
│   │   │   │   ├── dressing/page.tsx
│   │   │   │   └── settings/page.tsx
│   │   │   ├── (brand)/
│   │   │   │   ├── dashboard/page.tsx
│   │   │   │   ├── catalog/page.tsx
│   │   │   │   └── analytics/page.tsx
│   │   │   ├── api/
│   │   │   │   └── webhooks/stripe/route.ts
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx              # Landing
│   │   ├── components/
│   │   │   ├── ui/                   # shadcn/ui base
│   │   │   ├── studio/               # Composants métier
│   │   │   ├── brand/
│   │   │   └── shared/
│   │   ├── lib/
│   │   │   ├── api.ts                # Client API typé
│   │   │   ├── auth.ts
│   │   │   └── utils.ts
│   │   ├── stores/                   # Zustand stores
│   │   ├── hooks/                    # Custom hooks
│   │   └── types/
│   │
│   └── mobile/                       # Expo React Native
│       ├── app/                      # Expo Router
│       ├── components/
│       └── lib/                      # Shared avec web
│
├── packages/
│   ├── shared-types/                 # Types TypeScript partagés
│   ├── ui/                           # Composants partagés web/mobile
│   └── utils/                        # Fonctions utilitaires
│
├── backend/
│   ├── app/
│   │   ├── main.py                   # FastAPI app
│   │   ├── config.py                 # Settings (pydantic-settings)
│   │   ├── dependencies.py           # DI FastAPI
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── generate.py           # Try-on, vidéo
│   │   │   ├── brands.py
│   │   │   ├── catalog.py
│   │   │   └── webhooks.py
│   │   ├── models/                   # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── job.py
│   │   │   ├── brand.py
│   │   │   └── credit.py
│   │   ├── schemas/                  # Pydantic schemas
│   │   ├── services/
│   │   │   ├── ai/
│   │   │   │   ├── fal_client.py
│   │   │   │   ├── replicate_client.py
│   │   │   │   ├── kling_client.py
│   │   │   │   └── router.py         # Circuit breaker
│   │   │   ├── storage.py            # R2 client
│   │   │   ├── credits.py
│   │   │   └── stripe.py
│   │   ├── worker/
│   │   │   ├── celery_app.py
│   │   │   ├── tasks/
│   │   │   │   ├── generate_image.py
│   │   │   │   ├── generate_video.py
│   │   │   │   └── cleanup.py
│   │   ├── db/
│   │   │   ├── session.py
│   │   │   └── migrations/           # Alembic
│   │   └── middleware/
│   │       ├── auth.py
│   │       ├── rate_limit.py
│   │       └── logging.py
│   ├── tests/
│   ├── Dockerfile
│   ├── Dockerfile.worker
│   └── requirements.txt
│
├── infra/
│   ├── docker-compose.yml            # Dev local
│   └── .github/workflows/
│       ├── ci.yml
│       └── deploy.yml
│
├── docs/
│   ├── architecture.md
│   ├── Plan.md
│   └── Design.md
│
├── turbo.json                        # Turborepo
├── package.json
└── pnpm-workspace.yaml
```

### Conventions de nommage

```
Fichiers TS/TSX    : kebab-case (try-on-card.tsx)
Composants React   : PascalCase (TryOnCard)
Hooks              : camelCase préfixe use (useGenerationJob)
Stores Zustand     : camelCase suffixe Store (studioStore)
API routes Next    : route.ts dans dossier
Backend Python     : snake_case partout
DB tables          : snake_case pluriel (generation_jobs)
DB colonnes        : snake_case (created_at)
Env vars           : SCREAMING_SNAKE_CASE
```
