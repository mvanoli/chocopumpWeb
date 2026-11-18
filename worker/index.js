// Chocopump site worker: serves the static site, redirects www to the apex,
// and handles /api/lead (reserve + quote forms) with Cloudflare Email Sending.
// Bindings (wrangler.jsonc): EMAIL -> team inbox, REPLY -> confirmation to the customer.
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const json = (o, status = 200) => new Response(JSON.stringify(o), { status, headers: { "Content-Type": "application/json" } });
const FROM = { email: "info@chocopump.com", name: "Chocopump" };

const CONF = {
  en: { reserve: ["We received your reservation", "Grazie! Your Chocopump is reserved. We'll email you a secure payment link shortly, free shipping included."],
        quote: ["We received your quote request", "Grazie! A person on our team will reply with pricing for your order."], sig: "The Chocopump team" },
  it: { reserve: ["Abbiamo ricevuto la tua prenotazione", "Grazie! Il tuo Chocopump è prenotato. A breve ti invieremo via email un link di pagamento sicuro, spedizione gratuita inclusa."],
        quote: ["Abbiamo ricevuto la tua richiesta di preventivo", "Grazie! Una persona del nostro team ti risponderà con i prezzi per il tuo ordine."], sig: "Il team Chocopump" },
  es: { reserve: ["Recibimos tu reserva", "¡Grazie! Tu Chocopump está reservado. En breve te enviaremos por correo un enlace de pago seguro, con envío gratis incluido."],
        quote: ["Recibimos tu solicitud de cotización", "¡Grazie! Una persona de nuestro equipo te responderá con precios para tu pedido."], sig: "El equipo de Chocopump" },
};

async function confirm(env, d) {
  if (!env.REPLY) return;
  const c = CONF[d.lang] || CONF.en;
  const [subject, body] = c[d.kind === "quote" ? "quote" : "reserve"];
  const lines = [`${d.name},`, body, d.model ? `${d.model}${d.units ? " × " + d.units : ""}` : "", c.sig, "info@chocopump.com · https://chocopump.com"].filter(Boolean);
  const html = `<div style="font-family:Arial,sans-serif;font-size:15px;line-height:1.6;color:#2B1A0E;max-width:560px"><p style="font-family:Georgia,serif;font-size:22px;margin:0 0 16px">Chocopump</p>${lines.map((l) => `<p style="margin:0 0 10px">${esc(l)}</p>`).join("")}</div>`;
  try {
    await env.REPLY.send({ from: FROM, to: d.email, replyTo: "info@chocopump.com", subject, html, text: lines.join("\n\n") });
  } catch (e) {
    console.log("confirm error", String(e));
  }
}

async function lead(request, env) {
  let d;
  try { d = await request.json(); } catch { return json({ ok: false, error: "bad_json" }, 400); }
  if (d.website) return json({ ok: true }); // honeypot
  d.email = String(d.email || "").trim();
  if (!d.name || !/^\S+@\S+\.\S+$/.test(d.email)) return json({ ok: false, error: "missing_fields" }, 400);
  const kind = d.kind === "quote" ? "Quote request" : "Reservation";
  const subject = `Chocopump ${kind}: ${d.model || (d.units ? d.units + " units" : "")} - ${d.company || d.name}`.slice(0, 180);
  const rows = ["kind", "model", "units", "name", "company", "email", "zip", "lang", "message"]
    .filter((k) => d[k]).map((k) => `<tr><td><b>${k}</b></td><td>${esc(d[k])}</td></tr>`).join("");
  const html = `<p>New ${kind.toLowerCase()} from chocopump.com</p><table cellpadding="6">${rows}</table>` +
    (d.kind === "reserve" ? `<p>Next step: reply with the payment link for ${esc(d.model)}.</p>` : "");
  try {
    await env.EMAIL.send({ from: { email: "info@chocopump.com", name: "Chocopump website" }, to: env.LEAD_TO, replyTo: d.email, subject, html,
      text: rows.replace(/<[^>]+>/g, " ") });
  } catch (e) {
    console.log("lead send error", String(e));
    return json({ ok: false, error: "send_failed" }, 502);
  }
  await confirm(env, d);
  return json({ ok: true });
}

// Old Shopify URLs (still in Google's index) -> new pages, permanent 301.
const LEGACY = {
  "/products/chocopump-deluxe": "/deluxe/",
  "/products/chocopump-pro": "/pro/",
  "/products/nutella-compatible-dispenser-by-chocopump-mess-free-dispenser-for-nutella-foodservice-3kg-tub": "/",
  "/pages/contact": "/#reserve",
  "/policies/privacy-policy": "/privacy/",
  "/policies/terms-of-service": "/terms/",
  "/policies/refund-policy": "/shipping-returns/",
  "/policies/shipping-policy": "/shipping-returns/",
};
const LEGACY_PREFIX = /^\/(products|collections|pages|policies|blogs|cart|account|search)(\/|$)/;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.hostname === "www.chocopump.com" || url.protocol === "http:") {
      url.hostname = "chocopump.com";
      url.protocol = "https:";
      return Response.redirect(url.toString(), 301);
    }
    const p = url.pathname.replace(/\/+$/, "") || "/";
    if (LEGACY[p] || LEGACY_PREFIX.test(url.pathname)) {
      return Response.redirect("https://chocopump.com" + (LEGACY[p] || "/"), 301);
    }
    // Old thank-you URL (may still be set as a Stripe redirect): keep the query so the purchase is still measured.
    const ty = url.pathname.match(/^\/((?:it|es)\/)?thank-you\.html$/);
    if (ty) {
      url.pathname = `/${ty[1] || ""}thank-you/`;
      return Response.redirect(url.toString(), 301);
    }
    // Clean URLs: /pro/index.html -> /pro/, /pro -> /pro/ (301 instead of the default 307)
    if (url.pathname.endsWith("/index.html")) {
      url.pathname = url.pathname.slice(0, -10);
      return Response.redirect(url.toString(), 301);
    }
    if (!url.pathname.endsWith("/") && !/\.[a-z0-9]+$/i.test(url.pathname) && !url.pathname.startsWith("/api/")) {
      url.pathname += "/";
      return Response.redirect(url.toString(), 301);
    }
    if (url.pathname === "/api/lead") {
      if (request.method !== "POST") return new Response("Method not allowed", { status: 405 });
      return lead(request, env);
    }
    const res = await env.ASSETS.fetch(request);
    // Rewrite internal links "x/index.html" -> "x/" so Google never hits a redirect.
    if ((res.headers.get("Content-Type") || "").includes("text/html")) {
      return new HTMLRewriter().on("a[href]", {
        element(el) {
          const h = el.getAttribute("href");
          if (!h || /^[a-z]+:|^\/\//i.test(h)) return;
          const clean = h.replace(/(^|\/)index\.html(?=#|$)/, "$1");
          if (clean !== h) el.setAttribute("href", clean === "" || clean.startsWith("#") ? "./" + clean : clean);
        },
      }).transform(res);
    }
    if (url.pathname.startsWith("/img/")) {
      const r = new Response(res.body, res);
      r.headers.set("Access-Control-Allow-Origin", "*");
      return r;
    }
    return res;
  },
};
