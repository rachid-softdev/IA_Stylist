# Product

## Register

product

## Users

**Primary (B2B):** Fashion brands and Shopify stores (50–500 SKUs). Marketing directors, e-commerce managers, and content teams who need to reduce return rates (30–40%) and photoshoot costs (€2–10k/day). Their context: fast-paced product cycles, tight content budgets, pressure to convert online.

**Secondary (B2C):** Online fashion shoppers aged 25–45, and fashion influencers / UGC creators. Their job: visualize a garment on themselves before buying, or create authentic fashion content.

**Shared job:** See a garment on a real person (themselves or their model) in seconds — not on a hanger, not on a runway stranger.

## Product Purpose

Transform any garment into a professional photoshoot and runway video in 60 seconds.

VFS exists to solve the two core problems of fashion e-commerce:
- **Returns:** 30–40% of online fashion is returned because the customer couldn't visualize the fit. VFS cuts this by 20–30%.
- **Content cost:** Traditional photoshoots cost €2–10k/day and take 4–8 weeks. VFS divides this by 10.

Success = brands reduce returns measurably, shoppers buy with confidence, and visual content becomes a real-time asset, not a quarterly production.

## Brand Personality

**Three words:** Precise. Confident. Exclusive.

**Voice:** Direct, never condescending. Short copy, no filler. Microcopy is useful ("15 crédits restants"), not cheerful ("Vous avez presque épuisé votre solde"). Professional with an edge of exclusivity — this is a tool for serious fashion work, not a toy.

**Emotional goals:** Prestige (user feels they're using professional-grade tech), confidence (the result looks real), delight (the "wow" moment when the generation reveals).

## Anti-references

- Generic purple/violet AI gradients
- White cards with soft shadows everywhere (SaaS-cream monoculture)
- Plastic 3D illustrations (Notion/Lottie style avatars)
- Clean SaaS typography (Inter, DM Sans)
- Glassmorphism used decoratively
- Gradient text (`background-clip: text`)
- The hero-metric template (big number, small label, repeating stat cards)
- Tiny uppercase tracked eyebrow above every section
- Numbered section markers (01/02/03) as default scaffolding
- Identical card grids (icon + heading + text, endlessly repeated)
- Side-stripe borders on cards, callouts, or list items

## Design Principles

1.  **Wow first, account second.** The user's first generation must be breathtaking. The account gate comes *after* the wow moment, not before. Retention is earned in the first 60 seconds.

2.  **Zero-friction upload.** Drag & drop everywhere, immediate preview. The barrier between "I have a photo" and "I see the result" should feel like one step, not a form.

3.  **Real-time feedback, always.** The user always knows where their generation is: queued, processing, done, or failed. Progress is visible, not guesswork. Status is communicated in text, not just color.

4.  **Progressive disclosure.** Advanced features (batch lookbook, video generation, API keys) are hidden until the user needs them. The default interface is simple; complexity is revealed by context.

5.  **Errors are useful.** Never "Une erreur est survenue." Always: what failed, why, and what the user should do next. Credit refunds are explicit, not silent.

6.  **Dark luxury editorial is the differentiator.** The visual identity (deep blacks, warm gold, editorial serif typography) is not decoration — it's a product signal that VFS is for serious fashion professionals, not casual filter apps.

## Accessibility & Inclusion

- **WCAG AA minimum:** 4.5:1 contrast for body text, 3:1 for large text and UI elements
- **Full keyboard navigation:** Tab, Enter, Escape, Arrow keys across all interactive surfaces
- **Visible focus indicators:** 2px outline in accent-primary with 2px offset
- **ARIA:** Labels on all non-text interactive elements; `role="status"` on job progress; `aria-live="polite"` on toasts
- **Reduced motion:** All animations degrade gracefully via `prefers-reduced-motion: reduce` — crossfade or instant transition, never gating content visibility on animation
- **Touch targets:** Minimum 44×44px on mobile interactive elements
- **Color independence:** No content is conveyed by color alone — always icon + color + text
- **Dark/light themes:** Full dual-theme support with system preference detection
