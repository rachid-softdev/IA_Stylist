# Virtual Fashion Studio (VFS)

Plateforme de visualisation mode par IA. Try-on virtuel, génération vidéo, AI Stylist, dashboard marque.

## Stack

| Couche | Technologie |
|---|---|
| Frontend Web | Next.js 14 (App Router), TypeScript, Tailwind v4, shadcn/ui |
| Frontend Mobile | Expo (React Native) |
| Backend | Python 3.12, FastAPI, Celery |
| DB | PostgreSQL (Neon), Redis (Upstash) |
| Storage | Cloudflare R2 |
| Auth | Supabase Auth |
| AI | fal.ai, Replicate, Kling |

## Structure

```
virtual-fashion-studio/
├── apps/web/          # Next.js 14 frontend
├── apps/mobile/       # Expo React Native
├── packages/          # Types & utilitaires partagés
├── backend/           # API FastAPI + Workers Celery
├── infra/             # Docker, CI/CD
└── docs/              # Architecture, Design, Plan
```

## Démarrage rapide

### Prérequis

- Node.js 20+
- pnpm 9+
- Python 3.12+
- Docker Desktop

### Installation

```bash
pnpm install
cd backend && pip install -r requirements.txt
```

### Développement local

```bash
# Démarrer les services (PostgreSQL, Redis)
pnpm docker:up

# Migrations DB
pnpm db:migrate

# Lancer le backend
cd backend && uvicorn app.main:app --reload --port 8000

# Lancer le frontend
pnpm dev --filter web

# Worker Celery (dans un autre terminal)
cd backend && celery -A app.worker.celery_app worker --loglevel=info
```

### Variables d'environnement

Copier `.env.example` en `.env.local` et remplir les valeurs.

## Documentation

- [Architecture](ARCHITECTURE.md)
- [Design System](DESIGN.md)
- [Plan Produit](PLAN.md)
