# Build Prompt: Distinct Minerals World

You are a senior full-stack engineer and product designer who specializes in e-commerce and auction platforms — architecture, data modeling, security, and UX. Write clean, well-organized, non-hardcoded code that is easy to extend. Think through edge cases explicitly before implementing (auction timing races, duplicate bids, image upload failures, admin misuse, etc.) and handle them rather than assuming the happy path.

## 1. Project Summary

**Product:** Distinct Minerals World — a single-seller auction website for gemstones, minerals, and rock specimens.

**Business model:** One auction house (the site owner) lists all lots. There is no multi-vendor marketplace and no in-site checkout — winning bidders complete the purchase off-platform via WhatsApp or email, which the admin coordinates manually.

**Primary reference:** [famauctions.com](https://famauctions.com) — study its page structure, auction states, bidding mechanics, and admin capabilities as the functional blueprint. Match its proven UX patterns rather than inventing new ones.

**Design reference:** Same site's visual language (see Section 6) — reproduce it faithfully rather than defaulting to generic AI-generated styling.

## 2. Tech Stack

- **Frontend:** Next.js (React) + Tailwind CSS
- **Backend:** Next.js API routes / server actions (Node)
- **Database & Auth:** Supabase (Postgres, Row Level Security, Storage for images/videos)
- **Hosting assumption:** Vercel-compatible deployment. 

Justify any deviation from this stack before substituting something else.

## 3. Site Structure & Pages

- **Home** — hero banner (admin-editable image/headline), Live Auctions, Upcoming Auctions, Closed Auctions, trust/testimonial sections, newsletter signup
- **Auctions** (listing + filters by status: live / upcoming / closed)
- **Product/Lot detail page** — images, optional video, description, current bid, bid history, countdown timer, bid form
- **Minerals** and **Gemstones** — category landing pages
- **Category / Subcategory** listing pages
- **About Us**, **Contact Us**, **Help & Support**
- **Login / Register** (lightweight — see Section 5)
- **Admin panel** at a non-guessable path (Section 7)

## 4. Auction Mechanics

- **Auction states:** `upcoming` → `live` → `closed`, with closed lots further tagged `sold`, `not sold`, or `awaiting payment`.
- **Timing model:** Fixed start and end timestamps set per lot by the admin (not a rolling/open-ended window). Display a live countdown on live lots and a "starts in" countdown on upcoming lots.
- **Bidding:** Each bid must exceed the current bid by at least a defined minimum increment. Prevent race conditions on simultaneous bids (use a DB transaction / optimistic locking so two users can't win the same increment).
- **Bid history:** Visible per lot, but bidder identity is masked (show first and last character of the name, asterisk the middle — e.g., `J****r`).
- **No on-site payment.** After a lot closes, the admin manually marks it `awaiting payment`, `sold`, or `not sold`. The winning bidder is notified (email, and optionally WhatsApp) with instructions to complete payment off-platform.
- Cover all edge casses

## 5. Bidding & User Accounts

- To place a bid, collect: **full name, email, phone number** (required) and **WhatsApp number** (optional).
- Verification is lightweight — email/phone confirmation, not full KYC/ID verification.
- Store this as a user profile (Supabase Auth or a linked `bidders` table) so repeat bidders don't re-enter info every time.
- Rate-limit bid submissions per user/IP to prevent spam or automated sniping abuse.

## 6. Design System (from FAM Auctions reference)

Reproduce this exactly — do not substitute generic defaults.

**Typography**
- Headings: `Inter`
- Body: `Cabin`
- Base body size 14–15px, headings scale from 17px (H4) up to ~36px (display)

**Color palette**
| Role | Hex | Usage |
|---|---|---|
| Background | `#ffffff` | Primary canvas |
| Background secondary | `#e2e2e2` | Cards, alternating sections, borders |
| Primary accent | `#f5c518` | CTAs, brand highlights, active nav state |
| Secondary accent | `#ea212e` | Hover states, secondary CTAs, price/urgency text |
| Text primary | `#777777` | Headings and body — never pure black |
| Text secondary | `#666666` | Muted captions, placeholders |

**Shape & elevation**
- Rounded corners, 12px+ on interactive elements and cards (some card variants up to 50px)
- Tinted/chromatic shadows, not flat black shadows — gives a warm, soft elevation
- 5px base spacing unit; keep all gaps as multiples of it


## 7. Admin Panel

- **Path:** a non-obvious, non-guessable route (not `/admin`) — treat the exact slug as a secret credential, not something to hardcode in client-visible code or public repos.
- **Auth:** admin-only role via Supabase Auth + RLS; no public sign-up path to this role.
- **Capabilities:**
  - Create/edit/delete lots: name, description, images (multi-upload), optional video URL, starting bid, auction start/end time, category/subcategory
  - Create categories and subcategories (nested, reusable across lots)
  - Change lot/auction status: live, closed, sold, not sold, awaiting payment
  - Edit the homepage hero section (image + headline)
  - All changes must persist to Supabase and reflect on the public site immediately (no manual rebuild/deploy step required for content changes)
- cover all edge casses
## 8. Security & Reliability Requirements

- Enforce Supabase Row Level Security so only authenticated admins can write to lots/categories/status fields; public users get read-only access to published data.
- Validate and sanitize all admin inputs server-side (not just client-side) — image uploads, URLs, numeric fields (bid amounts, timestamps).
- Guard against: bid amount tampering from the client, auction end-time manipulation, duplicate/replayed bid submissions, and image upload abuse (file type/size limits).
- Mask bidder PII everywhere it's publicly displayed (bid history); keep full contact details visible only to the admin.
- Handle edge cases explicitly: a lot with zero bids at close, two bids landing within the same millisecond, an admin editing a lot while it's live, an expired/upcoming lot with a past start time, image upload failure mid-save.

## 9. Deployment Readiness (Vercel)

Build the project so it deploys to Vercel with no rework:

- **Standard Next.js app** — App Router, no custom Express/Node server wrapping it.
- **All secrets in environment variables** — Supabase URL, Supabase anon key, Supabase service-role key (server-only, never sent to the client), the admin panel's secret route slug, and any WhatsApp/email API keys. Prefix only client-safe values with `NEXT_PUBLIC_`.
- **Supabase Storage domain added to `next.config.js`** (`images.remotePatterns`) so product images/videos served from Supabase Storage work through Next.js image optimization.
- **Serverless-friendly functions** — keep bid submission, image upload, and admin-save handlers fast and stateless; drive the live countdown off a stored end timestamp client-side rather than long-polling; offload any heavy processing (e.g. video handling) instead of doing it inline in a request.
- **Deploy path:** push to GitHub → import the repo into Vercel → add all environment variables under Project Settings for Production/Preview/Development → deploy.
- **Plan note:** this is a commercial site (real auctions, real sales), so it belongs on Vercel's Pro plan, not the free Hobby tier, which is non-commercial only.

## 10. Non-Goals (explicitly out of scope)

- No in-site payment processing or checkout flow
- No multi-vendor/marketplace seller accounts
- No full KYC/identity verification