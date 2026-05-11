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
