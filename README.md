# chocopump.com

Pages are generated: edit copy in `i18n.py` (English, Italian, Spanish) and templates in `build.py`, then run `python3 build.py`.
Public contact: info@chocopump.com (forward to info@whimgoods.com). Form leads are emailed to LEAD_TO in wrangler.jsonc.

Static sales page + a small Cloudflare Worker (same approach as whimgoods.com).

- `public/` the site. Prices, lot sizes and checkout links live in `public/js/config.js` (the only file to edit day to day).
- `worker/index.js` serves the site, redirects www to the apex, and handles `POST /api/lead` (reserve + bulk-quote forms) by emailing info@whimgoods.com through Resend.
- `wrangler.jsonc` Worker config and chocopump.com routes.

## Go live
1. Move chocopump.com DNS to Cloudflare (Whimgoods LLC account).
2. `npx wrangler deploy` (or connect this repo to Workers Builds so each push to main deploys).
3. `npx wrangler secret put RESEND_API_KEY` (reuse the Whimgoods key; whimgoods.com is already verified, so mail is sent from website@whimgoods.com).
4. In Stripe (Whimgoods LLC account): create one product per version at $599, a Payment Link each with
   - shipping address collection on (US only), no shipping charge
   - "Limit the number of payments" = lot size (30 PRO / 40 DELUXE)
   - after payment, redirect to https://chocopump.com/thank-you.html
   Paste the two links into `public/js/config.js` and redeploy. Until then, buy buttons open the reserve form.
5. When a lot sells out, set `proSoldOut` / `deluxeSoldOut` to true; for a new lot, bump `lot.number` and the sizes.
