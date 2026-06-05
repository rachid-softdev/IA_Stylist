# Plan.md — AI Fashion Visualization Platform

---

## Vision produit

### Problème résolu

Les marques mode perdent des ventes à cause de :
- Retours massifs (30-40%) liés à l'incertitude taille/style
- Shootings photo coûteux (€2-10k/jour studio)
- Délai content production = 4-8 semaines
- Expérience e-commerce statique qui ne convertit pas

Les consommateurs abandonnent leur panier parce qu'ils ne peuvent pas visualiser le vêtement sur eux.

### Cible utilisateur

**B2B (primaire) :**
- Marques fashion Shopify (50-500 SKUs)
- Marques luxe avec besoin contenu premium
- Agences fashion content

**B2C (secondaire) :**
- Acheteurs mode en ligne (25-45 ans)
- Influenceurs fashion / créateurs UGC

### Proposition de valeur

> *Transformez n'importe quel vêtement en shooting professionnel et en vidéo défilé en 60 secondes.*

Pour les marques : **réduire les retours de 20-30%** et **diviser par 10 le coût du contenu visuel**.

### Différenciation

| Concurrent | Faiblesse | Notre avantage |
|---|---|---|
| Zeekit / Vue.ai | Résultats génériques, corps déformés | Cohérence visage + réalisme tissu |
| Botika | Limité mannequins IA | Vrai try-on photo utilisateur |
| Snap / IG filters | Fun, pas professionnel | Qualité production premium |
| Shootings classiques | Coût, délai | 60 secondes, fraction du coût |

---

## Fonctionnalités

### F01 — Upload & Profil utilisateur

**Description** : L'utilisateur upload 1 à 3 photos de lui-même pour créer son profil visuel IA.

**Comportement attendu** :
- Drag & drop ou sélection fichier (JPEG, PNG, WebP, max 10MB)
- Validation côté client (résolution min 512x512, format, taille)
- Upload direct vers R2 via URL présignée (pas de transit backend)
- Détection automatique silhouette (appel modèle détection)
- Stockage profil chiffré, visible uniquement par l'utilisateur

**Logique métier** :
- Si photos floues ou mal cadrées → rejection avec message explicite
- 1 photo minimum, 3 recommandées pour meilleure cohérence
- Régénération profil possible (écrase l'ancien)

**Interactions** :
- Frontend : composant upload avec preview, progress bar, validation visuelle
- Backend : POST /users/profile/photos → validation → stockage R2 → job analyse

**Edge cases** :
- Photo de groupe → rejeter, demander photo individuelle
- Photo avec vêtements très couvrants → warning qualité
- Visage masqué/flouté → erreur, photo requise face visible

**Sécurité** :
- Photos profil accessibles uniquement via token signé temporaire
- Suppression automatique raw uploads après 24h

---

### F02 — Try-On Image (cœur du produit)

**Description** : L'IA habille l'utilisateur avec un vêtement choisi et génère une photo réaliste.

**Comportement attendu** :
1. Sélection vêtement (catalogue marque ou upload PNG propre)
2. Lancement génération (déduction 1 crédit)
3. Progress temps réel via WebSocket (0% → processing → 100%)
4. Résultat affiché avec options : télécharger, partager, varier

**Logique métier** :
- Modèle principal : IDM-VTON ou CatVTON via fal.ai
- Fallback : Kolors Virtual Try-On via Replicate si fal indisponible
- Temps de génération cible : 15-30 secondes
- Si échec : retry automatique x2, puis message d'erreur + remboursement crédit

**Paramètres génération** :
```
model_photo: URL R2 photo utilisateur
garment_image: URL R2 vêtement
category: top | bottom | dress | outerwear | shoes | accessories
num_inference_steps: 30 (qualité/vitesse balance)
seed: random (reproductible si saved)
```

**Variations automatiques** :
- Couleurs alternatives du même vêtement
- Styles différents (casual, habillé, sport)
- Angles (face, 3/4, dos si disponible)

**Edge cases** :
- Vêtement trop complexe (imprimés très détaillés) → warning qualité
- Photo utilisateur incompatible avec catégorie vêtement (ex: robe + photo coupée aux épaules)
- Job timeout 120s → cancel, remboursement, notification

**Sécurité** :
- Vérification crédit AVANT lancement job (transaction DB atomique)
- Rate limit : 10 générations/heure free, 100/heure pro

---

### F03 — Génération Vidéo

**Description** : Génère une courte vidéo (3-8s) de l'utilisateur portant le vêtement en mouvement.

**Types de vidéo** :
```
runway_walk    : défilé, marche naturelle
mirror_selfie  : selfie miroir, rotation légère
360_rotation   : rotation complète outfit
transition     : avant/après outfit swap
```

**Logique métier** :
- Input : image try-on générée en F02 (pas photo brute)
- Modèle : Kling API (principal) → Seedance → Runway (fallback)
- Coût : 3 crédits (vs 1 pour image)
- Durée génération : 60-120 secondes
- Format output : MP4 H264, 1080x1080 ou 9:16

**Interactions** :
- Frontend : player vidéo intégré, contrôles lecture
- Backend : job vidéo séparé du job image, queue dédiée `high`
- WebSocket : push progression + preview GIF à 50% si possible

**Edge cases** :
- Timeout 300s → partial result ou annulation + remboursement
- Qualité insuffisante → flag review, option régénération offerte

---

### F04 — AI Stylist

**Description** : L'IA analyse le profil et conseille tailles, fits, couleurs, looks complets.

**Comportement attendu** :
- Analyse automatique post-upload photo : morphologie détectée, teint, style actuel
- Recommandations contextuelles sur chaque vêtement essayé
- Suggestions outfits complets (matching)
- Alertes proactives : "Cette coupe oversized te va mieux que le slim"

**Logique métier** :
```python
# Prompt AI Stylist
system = """Tu es un styliste expert. Analyse la morphologie 
et donne des conseils précis, directs, personnalisés.
Format JSON strict."""

input = {
    "morphologie": "...",
    "teint": "...",
    "garment_category": "...",
    "garment_fit": "...",
}
```

- Modèle : claude-sonnet via API ou GPT-4o (vision)
- Cache recommandations 24h par (user_profile, garment_id)
- Feedback utilisateur (👍/👎) pour amélioration

**Edge cases** :
- Morphologie non détectable → questions guidées utilisateur
- Vêtement hors catalogue → analyse image uniquement

---

### F05 — Dressing Virtuel

**Description** : Galerie personnelle de tous les try-ons, organisée en collections.

**Comportement attendu** :
- Vue grille images/vidéos générées
- Filtres : catégorie, date, marque, favori
- Collections manuelles (ex: "Summer looks", "Work outfits")
- Partage collection via lien public optionnel
- Export ZIP de sélection

**Logique métier** :
- Rétention : 30 jours free, illimité pro
- Tri défaut : date desc
- Search : par marque, couleur (tag auto), catégorie

**Edge cases** :
- Dressing vide → onboarding guidé "Essayez votre premier look"
- Quota stockage atteint → notification + upgrade prompt

---

### F06 — Dashboard Marque (B2B)

**Description** : Interface dédiée aux marques pour gérer catalogue, analytics, intégrations.

**Modules** :

#### Catalogue vêtements
- Upload produits (PNG fond blanc, ou fond transparent)
- Métadonnées : SKU, nom, catégorie, tailles, couleurs
- Import CSV/Shopify bulk
- Statut validation (product image quality check)

#### Analytics
```
KPIs affichés :
├── Try-ons par SKU (heatmap)
├── Taux conversion essayage → achat (via tracking Shopify)
├── Temps moyen sur try-on
├── SKUs les plus essayés
├── Retours évités estimés (calculé)
└── Économies contenu (vs shooting classique)
```

#### API Keys & Intégration
- Génération clés API (vfs_live_xxx)
- Widget embed Shopify (script tag)
- Webhook configuration (génération terminée)
- Documentation interactive (Swagger)

#### Facturation
- Dashboard consommation crédits
- Historique factures
- Upgrade/downgrade plan
- Ajout membres équipe

**Sécurité** :
- Isolation stricte données entre marques (tenant_id partout)
- Logs audit toutes actions brand_admin
- MFA obligatoire pour brand_admin

---

### F07 — Plugin Shopify

**Description** : Widget embeddable dans les pages produit Shopify pour try-on inline.

**Comportement attendu** :
```
Page produit Shopify :
├── Bouton "Essayer virtuellement"
├── Modal : upload photo ou sélection profil
├── Génération inline (spinner)
└── Résultat affiché → "Ajouter au panier" contextualisé
```

**Intégration technique** :
```javascript
// Script tag Shopify
<script src="https://cdn.vfs.ai/widget.js" 
        data-api-key="vfs_live_xxx"
        data-product-id="{{ product.id }}"
        data-sku="{{ variant.sku }}">
</script>
```

**Logique métier** :
- Widget chargé async (0 impact perf page hôte)
- Session utilisateur persistée localStorage (email hash)
- Tracking événements → analytics dashboard marque

---

### F08 — Générateur Lookbook / Shooting IA

**Description** : Génère automatiquement un lookbook complet ou un shooting studio virtuel pour une collection.

**Comportement attendu** :
1. Sélection collection vêtements (ou toute la saison)
2. Choix style : studio blanc, outdoor, lifestyle, luxe
3. Choix mannequins IA (diversité, âge, morphologie)
4. Génération batch de toutes les combinaisons
5. Export : PDF lookbook, ZIP images haute résolution, vidéos

**Logique métier** :
- Mannequins IA : galerie de 20+ avatars cohérents pré-générés
- Custom mannequin : upload référence photo modèle de la marque
- Batch processing : queue `low`, traitement overnight si >50 items
- Prix : pack crédits dédié ou ligne dans abonnement brand

**Output formats** :
```
Lookbook PDF      : mise en page automatique, logo marque
Images HD         : 2048x2048 WebP/PNG
Vidéos produit    : 9:16 Instagram, 16:9 web, 1:1 carré
UGC clips         : 15s style TikTok/Reels
```

---

## Architecture fonctionnelle

### Modules principaux

```
┌─────────────────────────────────────────────────────────┐
│                     PLATFORM                            │
│                                                         │
│  ┌───────────┐  ┌───────────┐  ┌────────────────────┐  │
│  │  AUTH     │  │  CREDITS  │  │  NOTIFICATIONS     │  │
│  │  Module   │  │  Engine   │  │  (email + WS push) │  │
│  └─────┬─────┘  └─────┬─────┘  └──────────┬─────────┘  │
│        │              │                   │             │
│  ┌─────▼──────────────▼───────────────────▼──────────┐  │
│  │                 CORE ENGINE                        │  │
│  │  ┌──────────┐  ┌──────────┐  ┌─────────────────┐  │  │
│  │  │ GENERATE │  │ CATALOG  │  │ DRESSING        │  │  │
│  │  │ (image+  │  │ Manager  │  │ (collections)   │  │  │
│  │  │  video)  │  │          │  │                 │  │  │
│  │  └──────────┘  └──────────┘  └─────────────────┘  │  │
│  └────────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │              BRAND LAYER (B2B)                   │   │
│  │  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │   │
│  │  │DASHBOARD │  │ SHOPIFY  │  │ LOOKBOOK GEN   │  │   │
│  │  │Analytics │  │ Plugin   │  │ Batch          │  │   │
│  │  └──────────┘  └──────────┘  └────────────────┘  │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Flux utilisateur principal (B2C)

```
Landing → Signup → Upload profil → Studio
                                      │
                          ┌───────────┼───────────┐
                          ▼           ▼            ▼
                    Choisir      AI Stylist    Dressing
                    vêtement      conseil       galerie
                          │
                          ▼
                    Try-On Image (1 crédit)
                          │
                          ├──► Satisfait → Télécharger / Partager
                          │
                          └──► Générer vidéo (3 crédits)
                                    │
                                    └──► Lookbook / Export
```

### Flux système — Job GPU

```
POST /generate/try-on
        │
        ▼
validate_request() → check_credits() → deduct_credits_pending()
        │
        ▼
upload_to_r2(photo, garment) → create_job(DB, status=queued)
        │
        ▼
enqueue(celery, job_id, priority=tier)
        │
        ▼
[WORKER] pick_job() → call_ai_service()
        │
        ├── success → upload_result(R2) → update_job(done) 
        │             → confirm_credit_deduction()
        │             → ws_push(user_id, job_result)
        │
        └── failure → retry(x2) → update_job(failed)
                      → refund_credit() → ws_push(error)
```

---

## Plan technique

### Ordre d'implémentation logique

```
Phase A — Fondations
├── 1. DB schema + migrations Alembic
├── 2. Auth Supabase + middleware FastAPI
├── 3. Upload R2 (URLs présignées)
├── 4. Credits engine (transactions atomiques)
└── 5. Job queue Celery basique

Phase B — Core
├── 6. Intégration fal.ai (IDM-VTON)
├── 7. WebSocket updates jobs
├── 8. Frontend Studio page (upload + génération)
└── 9. Dressing (galerie)

Phase C — B2B
├── 10. Brand onboarding + dashboard
├── 11. Catalogue upload + validation
├── 12. Analytics dashboard
└── 13. Shopify widget

Phase D — Premium
├── 14. Génération vidéo (Kling)
├── 15. AI Stylist
├── 16. Lookbook generator
└── 17. Mobile Expo
```

### Stratégie API

**REST** pour toutes les ressources CRUD.
**WebSocket** pour real-time job updates uniquement.
**Webhooks sortants** pour intégration Shopify / partenaires.

```
Base URL : https://api.vfs.ai/v1

Authentification : Bearer JWT (Supabase) OU API Key (brands)
Headers obligatoires : Authorization, Content-Type, X-Request-ID

Réponse standard :
{
  "data": {...},
  "meta": {"request_id": "...", "timestamp": "..."},
  "error": null
}

Erreur :
{
  "data": null,
  "error": {
    "code": "INSUFFICIENT_CREDITS",
    "message": "Not enough credits",
    "details": {...}
  }
}
```

### Gestion état frontend

```typescript
// Zustand stores
studioStore     : photo profil active, vêtement sélectionné, job courant
dressingStore   : collections, items, filtres actifs
brandStore      : marque active, catalogue, analytics
authStore       : user, session, plan actuel
creditsStore    : balance, historique transactions

// React Query
useGenerationJob(jobId)      : polling/WS job status
useCatalog(brandId, filters) : catalogue avec pagination
useDressing(filters)         : galerie personnelle
useAnalytics(brandId, range) : métriques dashboard
```

---

## Gestion des données

### Schéma DB

```sql
-- Users
CREATE TABLE users (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email       VARCHAR(255) UNIQUE NOT NULL,
  plan        VARCHAR(20) DEFAULT 'free',  -- free|pro|brand
  credits     INTEGER DEFAULT 10,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- User profiles (photos IA)
CREATE TABLE user_profiles (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID REFERENCES users(id) ON DELETE CASCADE,
  photos      JSONB,          -- [{url, r2_key, order}]
  metadata    JSONB,          -- {morphologie, teint, ...}
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Brands
CREATE TABLE brands (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        VARCHAR(255) NOT NULL,
  plan        VARCHAR(20) DEFAULT 'starter',
  credits     INTEGER DEFAULT 100,
  shopify_url VARCHAR(255),
  api_key_hash VARCHAR(255),
  tenant_id   UUID UNIQUE DEFAULT gen_random_uuid(),
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Brand members
CREATE TABLE brand_members (
  brand_id    UUID REFERENCES brands(id),
  user_id     UUID REFERENCES users(id),
  role        VARCHAR(20) DEFAULT 'member',  -- admin|member
  PRIMARY KEY (brand_id, user_id)
);

-- Garments (catalogue)
CREATE TABLE garments (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id    UUID REFERENCES brands(id),
  sku         VARCHAR(255),
  name        VARCHAR(255) NOT NULL,
  category    VARCHAR(50),    -- top|bottom|dress|outerwear|shoes|accessories
  image_url   VARCHAR(500),
  metadata    JSONB,          -- {colors, sizes, fit, ...}
  status      VARCHAR(20) DEFAULT 'active',
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(brand_id, sku)
);

-- Generation jobs
CREATE TABLE generation_jobs (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID REFERENCES users(id),
  brand_id        UUID REFERENCES brands(id),
  job_type        VARCHAR(20) NOT NULL,  -- image|video|lookbook
  status          VARCHAR(20) DEFAULT 'queued',
  garment_id      UUID REFERENCES garments(id),
  input_params    JSONB,
  result_url      VARCHAR(500),
  result_metadata JSONB,
  credits_used    INTEGER DEFAULT 1,
  error_message   TEXT,
  ai_provider     VARCHAR(50),
  duration_ms     INTEGER,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  completed_at    TIMESTAMPTZ
);

-- Credit transactions
CREATE TABLE credit_transactions (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID REFERENCES users(id),
  brand_id    UUID REFERENCES brands(id),
  amount      INTEGER NOT NULL,     -- positif=ajout, négatif=déduction
  type        VARCHAR(30),          -- generation|purchase|refund|bonus
  job_id      UUID REFERENCES generation_jobs(id),
  description TEXT,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Dressing collections
CREATE TABLE collections (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID REFERENCES users(id),
  name        VARCHAR(255) NOT NULL,
  is_public   BOOLEAN DEFAULT FALSE,
  share_token VARCHAR(50) UNIQUE,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE collection_items (
  collection_id UUID REFERENCES collections(id) ON DELETE CASCADE,
  job_id        UUID REFERENCES generation_jobs(id),
  added_at      TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (collection_id, job_id)
);

-- Indexes critiques
CREATE INDEX idx_jobs_user_status ON generation_jobs(user_id, status);
CREATE INDEX idx_jobs_created ON generation_jobs(created_at DESC);
CREATE INDEX idx_garments_brand ON garments(brand_id, status);
CREATE INDEX idx_transactions_user ON credit_transactions(user_id, created_at DESC);
CREATE INDEX idx_jobs_brand ON generation_jobs(brand_id, created_at DESC);
```

---

## Authentification & permissions

### Rôles et permissions

```
┌──────────────┬───────────────────────────────────────────┐
│ Rôle         │ Permissions                                │
├──────────────┼───────────────────────────────────────────┤
│ user (free)  │ generate image (quota), dressing, profile  │
│ user (pro)   │ + vidéo, collections illimitées, export    │
│ brand_member │ voir dashboard, analytics read-only        │
│ brand_admin  │ + catalogue CRUD, API keys, facturation    │
│ super_admin  │ tout                                       │
└──────────────┴───────────────────────────────────────────┘
```

### Sessions

```
Access Token  : JWT, 1 heure, httpOnly cookie
Refresh Token : JWT, 30 jours, httpOnly cookie, rotation
API Key       : HMAC-SHA256, préfixe vfs_live_, stocké hashé en DB
```

### MFA

Obligatoire pour `brand_admin` (TOTP via Supabase Auth).
Optionnel pour `user pro`.

### Récupération compte

Magic link email (Supabase Auth natif) + expiration 15 minutes.

---

## Gestion des risques techniques

### Risques critiques

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| fal.ai / Kling downtime | Moyen | Critique | Circuit breaker + fallback Replicate automatique |
| Qualité résultats IA faible | Haut | Fort | Seuil qualité automatique, option régénération offerte |
| Dépassement coûts GPU | Moyen | Fort | Rate limiting strict, quota par plan, alertes budget |
| Fuite données photos users | Faible | Critique | Chiffrement R2, tokens signés temporaires, RGPD |
| Queue GPU saturée | Moyen | Moyen | Temps d'attente visible, priorité par plan |
| Cohérence visage perdue | Haut | Moyen | InstantID / PuLID pour verrouillage identité |

### Limites techniques connues

- Tissu en mouvement complexe → artefacts vidéo possibles
- Vêtements avec pattern complexe → dégradation qualité
- Mains/superposition vêtements → point faible IDM-VTON
- Latence génération : 15-30s image, 60-120s vidéo → irréductible hardware

---

## KPIs

### Techniques

```
Uptime API              > 99.5%
Temps génération image  < 30s (p95)
Temps génération vidéo  < 120s (p95)
Taux erreur jobs        < 5%
Latence API (hors GPU)  < 200ms (p95)
Queue depth max         < 50 jobs
```

### Produit

```
Taux conversion essayage → achat   (baseline puis amélioration)
Taux retour produits B2B           -20% vs avant intégration
Jobs par utilisateur actif         > 5/semaine
Rétention J30                      > 40%
NPS brand                          > 50
```

---

## Monétisation

### Plans B2C

```
┌──────────┬──────────────┬──────────────┬───────────────┐
│          │ Free          │ Pro           │ Creator       │
├──────────┼──────────────┼──────────────┼───────────────┤
│ Prix     │ 0€           │ 19€/mois      │ 49€/mois      │
│ Crédits  │ 10/mois      │ 100/mois      │ 500/mois      │
│ Vidéo    │ Non          │ Oui           │ Oui           │
│ Export   │ Watermark    │ HD sans mark  │ HD + batch    │
│ Rétention│ 7 jours      │ 1 an          │ Illimitée     │
└──────────┴──────────────┴──────────────┴───────────────┘
```

### Plans B2B

```
┌──────────┬──────────────┬──────────────┬──────────────┐
│          │ Starter       │ Growth        │ Enterprise   │
├──────────┼──────────────┼──────────────┼──────────────┤
│ Prix     │ 199€/mois    │ 499€/mois    │ Sur devis    │
│ Crédits  │ 500/mois     │ 2000/mois    │ Illimité     │
│ SKUs     │ 50           │ 500          │ Illimité     │
│ Plugin   │ Shopify       │ + API        │ + white label│
│ Support  │ Email         │ Chat         │ CSM dédié    │
└──────────┴──────────────┴──────────────┴──────────────┘
```

### Gestion Stripe

```python
# Webhook events à gérer
customer.subscription.created   → activer plan, créditer
customer.subscription.deleted   → downgrade free
invoice.payment_succeeded        → renouvellement crédits
invoice.payment_failed           → grace period 3 jours, then downgrade
charge.dispute.created           → flag compte, alerter admin
```

---

## Checklist production

### Sécurité
- [ ] Variables d'environnement dans vault (pas en code)
- [ ] HTTPS partout, HSTS activé
- [ ] Rate limiting configuré par endpoint et par plan
- [ ] CORS strict en production
- [ ] JWT httpOnly cookies, SameSite=Strict
- [ ] Validation input backend (Pydantic) sur toutes routes
- [ ] SQL injection impossible (ORM uniquement, pas de raw SQL user-input)
- [ ] XSS : CSP headers stricts Next.js
- [ ] Audit logs brand_admin activés
- [ ] MFA obligatoire brand_admin
- [ ] URLs R2 signées temporaires (15 min) pour outputs sensibles
- [ ] RGPD : suppression données sur demande implémentée
- [ ] Backup DB testée et restauration documentée

### Performance
- [ ] CDN configuré pour tous les assets statiques
- [ ] Images Next.js optimisées (WebP, srcSet, lazy)
- [ ] React Query cache correctement configuré
- [ ] DB indexes tous créés et testés (EXPLAIN ANALYZE)
- [ ] Connection pooling PostgreSQL (PgBouncer)
- [ ] Compression Brotli activée sur Cloudflare
- [ ] Bundle Next.js analysé (next-bundle-analyzer)
- [ ] Core Web Vitals LCP < 2.5s, CLS < 0.1, FID < 100ms

### QA
- [ ] Tests unitaires services critiques (credits, auth)
- [ ] Tests intégration routes API principales
- [ ] Tests E2E flux génération complet (Playwright)
- [ ] Test fallback AI provider (simuler fal.ai down)
- [ ] Test quota et rate limiting
- [ ] Test remboursement crédit sur échec job
- [ ] Load test (100 users simultanés)

### Déploiement
- [ ] CI/CD pipeline testé end-to-end
- [ ] Migrations Alembic testées sur staging
- [ ] Rollback plan documenté (procédure < 5 min)
- [ ] Variables env production toutes configurées
- [ ] Secrets rotation documentée
- [ ] Health checks endpoints `/health` configurés

### Monitoring
- [ ] Sentry configuré frontend + backend
- [ ] Axiom logs pipeline actif
- [ ] Uptime Robot monitors configurés (API, WS, frontend)
- [ ] Alertes Slack critiques configurées
- [ ] Dashboard Posthog produit opérationnel
- [ ] Alertes budget GPU (fal.ai / Replicate) configurées

---

## Phase C — B2B : Plan d'implémentation détaillé

### C10 — Brand Onboarding + Dashboard

| Sous-tâche | Fichiers/Dossiers | Priorité |
|---|---|---|
| **C10.1 — Formulaire onboarding multi-step** | `apps/web/app/(brand)/onboarding/page.tsx` → wizard 3 étapes (infos, membre, plan) | Haute |
| **C10.2 — POST /v1/brands/onboarding complet** | `backend/app/routers/brands.py` — créer brand + admin + tenant_id | Haute |
| **C10.3 — GET /v1/brands/me enrichi** | Ajouter `member_count`, `last_generation_at`, `credits_usage%` au payload | Haute |
| **C10.4 — Sidebar navigation marque** | `apps/web/components/shared/sidebar.tsx` — liens dashboard/catalogue/analytics/API/billing | Haute |
| **C10.5 — Brand switcher** | Composant dropdown pour switch entre brands (si membre de plusieurs) | Moyenne |
| **C10.6 — Brand settings page** | Nom, URL Shopify, logo upload, branding (couleurs, fonts) | Moyenne |
| **C10.7 — Brand members UI** | `apps/web/app/(brand)/members/page.tsx` — liste membres, ajout/retrait, rôles | Haute |
| **C10.8 — Invitation email brand** | Backend envoi email + token d'invitation → `brand_members` | Moyenne |
| **C10.9 — Brand deletion flow** | Soft-delete + période de rétention 30j + notification membres | Basse |
| **C10.10 — Tests backend brands** | `backend/tests/test_brands.py` — compléter couverture (create, update, members, api keys) | Haute |
| **C10.11 — Tests frontend dashboard** | `apps/web/__tests__/` — rendu dashboard, navigation, brand switcher | Moyenne |
| **C10.12 — Tests E2E onboarding** | `e2e/specs/brand-onboarding.spec.ts` — parcours complet création marque | Moyenne |

### C11 — Catalogue Upload + Validation

| Sous-tâche | Fichiers/Dossiers | Priorité |
|---|---|---|
| **C11.1 — Catalogue list view complète** | `apps/web/app/(brand)/catalog/page.tsx` — table avec pagination, tri, search | Haute |
| **C11.2 — Catalogue add/upload garment** | `POST /v1/catalog/{brand_id}/garments` — upload image + metadata form | Haute |
| **C11.3 — Image validation AI** | Vérification fond blanc/transparent, résolution min 1024x1024, détection vêtement | Haute |
| **C11.4 — Import CSV bulk** | `POST /v1/catalog/{brand_id}/import` — parser CSV → Celery task → validation batch | Haute |
| **C11.5 — Import Shopify bulk** | Sync via Shopify API Admin (SKU, images, variants) → Webhook ou cron | Haute |
| **C11.6 — Garment detail/edit page** | `apps/web/app/(brand)/catalog/[id]/page.tsx` — éditer metadata, remplacer image | Moyenne |
| **C11.7 — Garment quality check** | Score qualité (résolution, détourage, arrière-plan) → status `validated`/`failed` | Haute |
| **C11.8 — Batch delete/archive** | `DELETE /v1/catalog/{brand_id}/garments/batch` — body avec array d'IDs | Moyenne |
| **C11.9 — Image variants** | Génération auto : thumbnail (256x256), web (1024x1024), full (2048x2048) via sharp | Moyenne |
| **C11.10 — Tests catalogue** | `backend/tests/test_catalog.py` — CRUD complet, validation, CSV import, quality check | Haute |
| **C11.11 — Tests E2E catalogue** | `e2e/specs/brand-catalog.spec.ts` — ajout, édition, import CSV | Moyenne |

### C12 — Analytics Dashboard

| Sous-tâche | Fichiers/Dossiers | Priorité |
|---|---|---|
| **C12.1 — GET /v1/analytics/{brand_id}/overview complet** | Retourner tryons_total, conversions (via Shopify), top_skus, savings_estimate, time_series | Haute |
| **C12.2 — Graphique try-ons par jour/semaine** | Composant chart.js/recharts — `apps/web/components/charts/TryonChart.tsx` | Haute |
| **C12.3 — Heatmap SKUs** | `apps/web/components/charts/SkuHeatmap.tsx` — matrice SKU × date | Haute |
| **C12.4 — Taux conversion essayage → achat** | Intégration Shopify Order API → ratio tryon → purchase | Haute |
| **C12.5 — Temps moyen sur try-on** | Logs interaction frontend → backend → analytics | Moyenne |
| **C12.6 — Retours évités estimés** | Calcul basé sur avg_return_rate × tryons_completed | Moyenne |
| **C12.7 — Économies contenu** | `savings = tryon_count × avg_photoshoot_cost_per_image` | Moyenne |
| **C12.8 — Date range picker** | Composant pour filtrer analytics (7j, 30j, 90j, custom) | Haute |
| **C12.9 — Export CSV analytics** | `GET /v1/analytics/{brand_id}/export?range=` → CSV download | Basse |
| **C12.10 — Recharts/visx lib** | Ajouter dépendance chart → `apps/web/package.json` | Haute |
| **C12.11 — Tests analytics** | `backend/tests/test_analytics.py` — calculs, time_series, export | Haute |
| **C12.12 — Tests frontend analytics** | Render charts, date range, données vides → `apps/web/__tests__/analytics/` | Moyenne |

### C13 — Shopify Widget (F07 complet)

| Sous-tâche | Fichiers/Dossiers | Priorité |
|---|---|---|
| **C13.1 — Widget SDK** | `packages/widget-sdk/` — bundle JS vanilla build avec esbuild/rollup | Haute |
| **C13.2 — Script tag embed** | `<script src="https://cdn.vfs.ai/widget.js" data-api-key data-product-id>` | Haute |
| **C13.3 — Bouton "Essayer virtuellement"** | Injection DOM sur page produit Shopify — bouton stylé VFS | Haute |
| **C13.4 — Modal upload/select profile** | Modal overlay avec drag-and-drop ou profile selector | Haute |
| **C13.5 — Inline generation spinner** | Barre de progression dans la modal avec status polling | Haute |
| **C13.6 — Résultat affiché + Ajouter panier** | Image générée + bouton "Ajouter au panier" avec variante | Haute |
| **C13.7 — Async loading (0 perf impact)** | `async` + `defer`, aucun DOMContentLoaded block | Haute |
| **C13.8 — Session persistence** | localStorage (email hash) pour éviter re-upload | Moyenne |
| **C13.9 — Event tracking → analytics marque** | Widget → POST analytics events → dashboard | Moyenne |
| **C13.10 — Theme matching Shopify** | Détecter thème store (couleurs, fonts) pour styler la modal | Moyenne |
| **C13.11 — Mobile responsive widget** | Breakpoints ≤ 768px — bottom sheet vs modal | Haute |
| **C13.12 — API endpoint widget auth** | `POST /v1/widget/auth` → token JWT court (15 min) pour widget | Haute |
| **C13.13 — Widget configuration dashboard** | Page marque pour configurer le widget (couleurs, texte bouton, position) | Basse |
| **C13.14 — Tests widget SDK** | `packages/widget-sdk/__tests__/` — unit + DOM integration | Haute |
| **C13.15 — Shopify App submission** | Créer app Shopify public, documentation install, review | Basse |

---

## Phase D — Premium : Plan d'implémentation détaillé

### D14 — Génération Vidéo (Kling + fallbacks)

| Sous-tâche | Fichiers/Dossiers | Priorité |
|---|---|---|
| **D14.1 — KlingClient robuste** | `backend/app/services/ai/kling_client.py` — retry, timeout, error handling | Haute |
| **D14.2 — Kling fallback Seedance** | `backend/app/services/ai/seedance_client.py` — second provider vidéo | Haute |
| **D14.3 — Kling fallback Runway** | `backend/app/services/ai/runway_client.py` — third fallback | Moyenne |
| **D14.4 — Circuit breaker vidéo** | Étendre `AIRouter` pour vidéo providers (image ≠ video routing) | Haute |
| **D14.5 — Vidéo player component** | `apps/web/components/studio/video-player.tsx` — player custom (contrôles, mute, loop) | Haute |
| **D14.6 — Generation progress vidéo** | WebSocket polling (3s) + barre progression avec temps estimé | Haute |
| **D14.7 — Preview GIF à 50%** | Si provider supporte, récupérer frame intermédiaire → GIF | Basse |
| **D14.8 — Video download** | MP4 download button + format selector (1080×1080, 9:16, 16:9) | Haute |
| **D14.9 — Video format/output** | 4 types : `runway_walk`, `mirror_selfie`, `360_rotation`, `transition` | Haute |
| **D14.10 — 3 crédits deduction** | Vérifié dans `POST /v1/generate/video` | Haute |
| **D14.11 — Queue dédiée high** | `task_queue="high"` sur Celery video tasks | Haute |
| **D14.12 — Timeout 300s job** | Cancel + refund si > 300s | Haute |
| **D14.13 — Video Gallery in Dressing** | Affichage vidéo dans la grille dressing (thumbnail + indicateur play) | Haute |
| **D14.14 — Tests Kling/Sedance/Runway** | Mocks HTTP → tests unitaires chaque provider | Haute |
| **D14.15 — Tests intégration vidéo** | `POST /generate/video` → poll → result (mock provider) | Haute |

### D15 — AI Stylist (LLM réel)

| Sous-tâche | Fichiers/Dossiers | Priorité |
|---|---|---|
| **D15.1 — LLM client (Claude/GPT-4o)** | `backend/app/services/llm_client.py` — provider agnostique (OpenAI-compatible) | Haute |
| **D15.2 — Prompt engineering stylist** | Système prompt structuré → JSON strict (morphologie, teint, fit, outfit) | Haute |
| **D15.3 — Analyse morphologie réelle** | Vision LLM sur photo profil → morphologie, teint, style actuel | Haute |
| **D15.4 — Recommandations par vêtement** | `POST /v1/stylist/recommendations` → LLM avec garment image + user profile | Haute |
| **D15.5 — Outfit suggestions complètes** | Matching vêtements catalogue → suggestions looks complets | Haute |
| **D15.6 — Cache 24h (user, garment)** | Cache Redis `stylist:{user_id}:{garment_id}` → TTL 86400 | Haute |
| **D15.7 — Proactive alerts** | "Cette coupe oversized te va mieux" → notification in-app | Moyenne |
| **D15.8 — User feedback loop** | 👍/👎 → store + fine-tune prompt via few-shot examples | Moyenne |
| **D15.9 — Stylist UI enrichie** | `apps/web/(app)/stylist/page.tsx` — cards recommandations, morphologie visuelle | Haute |
| **D15.10 — Questions guidées si morphologie non détectable** | Quiz 3-5 questions → formulaire → enrichir profile metadata | Moyenne |
| **D15.11 — Tests LLM client** | `backend/tests/test_llm_client.py` — mocks HTTP, parse response, error handling | Haute |
| **D15.12 — Tests intégration stylist** | `backend/tests/test_stylist.py` — enrichir avec vrais cas (mocks LLM) | Haute |
| **D15.13 — Tests frontend stylist** | render recommandations, feedback, loading/empty states | Moyenne |

### D16 — Lookbook Generator (Batch)

| Sous-tâche | Fichiers/Dossiers | Priorité |
|---|---|---|
| **D16.1 — Celery task batch lookbook** | `backend/app/worker/tasks/lookbook.py` — orchestrateur batch | Haute |
| **D16.2 — Sélection collection** | UI checkboxes garments + filtre catégorie → `apps/web/app/(brand)/lookbook/new` | Haute |
| **D16.3 — Choix style visuel** | Studio blanc, outdoor, lifestyle, luxe, streetwear → prompt template | Haute |
| **D16.4 — Choix mannequins IA** | Galerie 20+ avatars pré-générés → selection + custom upload | Haute |
| **D16.5 — Batch generation** | Parcourir toutes combinaisons (mannequin × vêtement) → queue `low` → jobs parallèles | Haute |
| **D16.6 — PDF lookbook export** | `backend/app/services/pdf_generator.py` — mise en page auto + logo marque + légendes | Haute |
| **D16.7 — ZIP images HD export** | `backend/app/services/zip_generator.py` — 2048×2048 WebP + PNG | Haute |
| **D16.8 — Video reel export** | Montage automatique vidéos → 15s TikTok/Reels format | Moyenne |
| **D16.9 — Lookbook progress tracking** | WebSocket batch progress (x/50 done, estimated time) | Haute |
| **D16.10 — Lookbook gallery** | `apps/web/app/(brand)/lookbook/page.tsx` — liste lookbooks générés | Haute |
| **D16.11 — Plan pricing: pack crédits dédié** | Validation `brand.credits ≥ item_count × cost_per_item` | Haute |
| **D16.12 — Tests lookbook** | `backend/tests/test_lookbook.py` — batch orchestrator, PDF/ZIP gen, progress | Haute |

### D17 — Mobile Expo

| Sous-tâche | Fichiers/Dossiers | Priorité |
|---|---|---|
| **D17.1 — Navigation + routing** | `apps/mobile/app/` — tabs (home, studio, dressing, profile) | Haute |
| **D17.2 — Auth screens** | Login, signup, magic link — integration Supabase Auth | Haute |
| **D17.3 — Camera/gallery upload** | `expo-image-picker` → upload photo profil | Haute |
| **D17.4 — Studio screen** | Garment selection + generation + result display | Haute |
| **D17.5 — Dressing gallery** | Grid collection items + fullscreen view | Haute |
| **D17.6 — API client mobile** | Shared types + fetch wrapper (identique pattern web) | Haute |
| **D17.7 — Push notifications** | `expo-notifications` — job completed, stylist alert | Moyenne |
| **D17.8 — Offline mode** | Cache dressing items, pending generation queue | Basse |
| **D17.9 — Tests mobile** | `apps/mobile/__tests__/` — component render, navigation | Haute |

---

## Travaux transverses restants

### T01 — Plugin Shopify (F07)

Détaillé ci-dessus dans **C13** (phase B2B). Priorité **Haute** pour activation revenus.

### T02 — Export PDF/ZIP

| Sous-tâche | Fichiers/Dossiers | Priorité |
|---|---|---|
| **T02.1 — PDF generator service** | `backend/app/services/pdf_generator.py` — ReportLab/PyPDF + template | Haute |
| **T02.2 — ZIP generator service** | `backend/app/services/zip_generator.py` — io.BytesIO + streaming | Haute |
| **T02.3 — Export endpoint générique** | `GET /v1/export/{job_id}?format=pdf|zip` — streaming response | Haute |
| **T02.4 — Frontend download button** | `apps/web/components/shared/export-button.tsx` — format selector | Haute |
| **T02.5 — Celery task export lourd** | Background pour exports > 50 images → notification download link | Moyenne |
| **T02.6 — Tests PDF/ZIP** | Validation contenu, structure, streaming | Haute |

### T03 — WebSocket temps réel

| Sous-tâche | Fichiers/Dossiers | Priorité |
|---|---|---|
| **T03.1 — WebSocket endpoint FastAPI** | `backend/app/routers/ws.py` — `WS /v1/ws` — authentifié via token query param | Haute |
| **T03.2 — Connection manager** | `backend/app/services/ws_manager.py` — gérer connexions, rooms par user_id/brand_id | Haute |
| **T03.3 — Push job progress** | Worker → Redis pub/sub → API → WS push (remplace polling) | Haute |
| **T03.4 — Frontend WebSocket hook** | `apps/web/hooks/use-websocket.ts` — reconnect, heartbeat, fallback polling | Haute |
| **T03.5 — Fallback HTTP polling** | Garder polling 3s si WS déconnecté | Haute |
| **T03.6 — Tests WebSocket** | `backend/tests/test_ws.py` — connect, auth, receive updates, disconnect | Haute |

### T04 — Intégration LLM réelle (Stylist)

Détaillé ci-dessus dans **D15**.

### T05 — Génération Lookbook batch

Détaillé ci-dessus dans **D16**.

### T06 — Chiffrement des photos

| Sous-tâche | Fichiers/Dossiers | Priorité |
|---|---|---|
| **T06.1 — Server-side encryption R2** | SSE-S3 ou client-side AES-256-GCM avant upload R2 | Haute |
| **T06.2 — Key management** | Vault/AWS KMS pour clés de chiffrement — `backend/app/services/encryption.py` | Haute |
| **T06.3 — Signed URLs temporelles** | URLs présignées 15 min pour accès photo profil + résultats | Haute |
| **T06.4 — Cleanup raw uploads 24h** | Cron/Celery beat → delete raw uploads non confirmés | Haute |
| **T06.5 — Tests chiffrement** | Encrypt → decrypt → verify integrity + corruption handling | Haute |

### T07 — Validation AI des uploads

| Sous-tâche | Fichiers/Dossiers | Priorité |
|---|---|---|
| **T07.1 — Détection visage** | Vérifier présence visage visible (non masqué, non flouté) | Haute |
| **T07.2 — Détection photo groupe** | Rejeter si >1 personne détectée | Haute |
| **T07.3 — Détection silhouette** | Vérifier corps entier ou cadre adapté selon catégorie vêtement | Haute |
| **T07.4 — Qualité image** | Score flou (Laplacian variance), résolution ≥ 512×512, format valide | Haute |
| **T07.5 — Vêtement complexe warning** | Pattern analysis → warning si imprimé très détaillé | Moyenne |
| **T07.6 — Tests validation** | Images test: flou/groupe/masqué/bonne → vérifier rejet/acceptation | Haute |

### T08 — MFA (Multi-Factor Authentication)

| Sous-tâche | Fichiers/Dossiers | Priorité |
|---|---|---|
| **T08.1 — TOTP setup flow** | Supabase Auth MFA enrollment → QR code scan → verify | Haute |
| **T08.2 — MFA enforce brand_admin** | Middleware vérifie `user.role = brand_admin` → MFA required | Haute |
| **T08.3 — MFA optional for pro users** | `apps/web/app/(app)/settings/mfa/page.tsx` — toggle ON/OFF | Moyenne |
| **T08.4 — Recovery codes** | Génération + stockage hashé codes de secours (10 codes) | Haute |
| **T08.5 — Tests MFA** | enrollment, verification, enforce middleware, recovery | Haute |

### T09 — Déploiement production

| Sous-tâche | Fichiers/Dossiers | Priorité |
|---|---|---|
| **T09.1 — Infrastructure staging** | `infra/terraform/` ou Pulumi — VPC, RDS, Redis, ECS/Fargate | Haute |
| **T09.2 — Domain + DNS** | vfs.ai → Cloudflare → Railway/Vercel | Haute |
| **T09.3 — SSL/TLS** | Cloudflare edge cert + origin cert | Haute |
| **T09.4 — CI/CD pipeline complet** | `.github/workflows/` — lint → test → build → deploy staging → deploy prod | Haute |
| **T09.5 — Migration DB automatisée** | Alembic migration run dans CI/CD deploy step | Haute |
| **T09.6 — Rollback procedure** | Script rollback DB + déploy version précédente (< 5 min) | Haute |
| **T09.7 — Health checks** | `GET /health` — DB, Redis, Celery, AI providers | Haute |
| **T09.8 — Env vars production** | `.env.production` template + vault (env réelles hors repo) | Haute |
| **T09.9 — Docker images registry** | GHCR ou Docker Hub → tags versionnés | Moyenne |
| **T09.10 — Staging environment** | Railway PR preview ou sous-domaine staging.vfs.ai | Haute |

### T10 — Monitoring (Sentry, Posthog, Logs)

| Sous-tâche | Fichiers/Dossiers | Priorité |
|---|---|---|
| **T10.1 — Sentry backend** | `sentry_sdk.init(...)` avec DSN production, traces_sample_rate=0.2 | Haute |
| **T10.2 — Sentry frontend** | `@sentry/nextjs` — source maps, user context, breadcrumbs | Haute |
| **T10.3 — Axiom logs pipeline** | `backend/app/middleware/logging.py` → exporter structured JSON vers Axiom | Haute |
| **T10.4 — Posthog product analytics** | `posthog-js` frontend + `posthog-python` backend → events: generation, upload, conversion | Haute |
| **T10.5 — Uptime monitoring** | Uptime Robot / Better Stack → API, WS, frontend — alertes Slack | Haute |
| **T10.6 — Budget alerts GPU** | Seuil $/mois → alertes email + Slack si > 80% | Haute |
| **T10.7 — Dashboard monitoring** | Grafana ou Better Stack dashboard — overview systèmes | Moyenne |
| **T10.8 — Alertes Slack configurées** | Webhook Slack pour: job failure rate > 5%, API latency > 500ms, provider down | Haute |
| **T10.9 — Tests monitoring** | Vérifier Sentry capture exception, Posthog event, log format | Moyenne |

---

## Priorités d'exécution

### Par phase

| Ordre | Phase | Justification |
|---|---|---|
| 1 | **T03 — WebSocket temps réel** | Prérequis pour toute UX génération fluide (phase B) |
| 2 | **C10 — Brand onboarding** | Activation revenus B2B |
| 3 | **C11 — Catalogue upload** | Nécessaire pour try-on marque |
| 4 | **C12 — Analytics** | Valeur ajoutée B2B immédiate |
| 5 | **C13/T01 — Shopify widget** | Canal d'acquisition B2B principal |
| 6 | **D15/T04 — AI Stylist LLM** | Différenciation produit majeure |
| 7 | **T06 — Chiffrement photos** | Sécurité données sensibles |
| 8 | **T07 — Validation AI uploads** | Qualité génération |
| 9 | **D14 — Génération vidéo** | Upsell pro |
| 10 | **D16/T05 — Lookbook batch** | Upsell brand |
| 11 | **T08 — MFA** | Conformité production |
| 12 | **T02 — Export PDF/ZIP** | Feature complémentaire |
| 13 | **D17 — Mobile Expo** | Canal secondaire |
| 14 | **T09 — Déploiement production** | Bloquant pour go-live |
| 15 | **T10 — Monitoring** | Bloquant pour go-live |

### Dépendances critiques

```
T03 (WebSocket) ──► D14 (Vidéo) ──► D16 (Lookbook)
                      │
C10 (Brand) ──► C11 (Catalogue) ──► C13 (Shopify)
                │
                └──► C12 (Analytics)
                      │
T07 (Validation) ──► T04 (Stylist LLM)
                      │
T06 (Chiffrement) ──► T09 (Déploiement) ──► T10 (Monitoring)
                      │
T08 (MFA) ────────────┘
```

### Estimation charges

| Bloc | Estimation |
|---|---|
| Phase C (10-13) | ~8-12 jours |
| Phase D (14-16) | ~10-15 jours |
| Phase D (17 Mobile) | ~5-8 jours |
| Transverses (T01-T10) | ~12-18 jours |
| **Total restant** | **~35-53 jours/homme** |

