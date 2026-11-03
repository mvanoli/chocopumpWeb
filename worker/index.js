// Chocopump site worker: serves the static page and handles /api/lead (reserve + quote forms).
// Secrets (set in Cloudflare, never in code): RESEND_API_KEY
// Vars (wrangler.jsonc): LEAD_TO, LEAD_FROM
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.hostname === "www.chocopump.com") {
      url.hostname = "chocopump.com";
      return Response.redirect(url.toString(), 301);
    }
    if (url.pathname === "/api/lead") {
      if (request.method !== "POST") return new Response("Method not allowed", { status: 405 });
      let d;
      try { d = await request.json(); } catch { return json({ ok: false, error: "bad_json" }, 400); }
      if (d.website) return json({ ok: true }); // honeypot
      const email = String(d.email || "").trim();
      if (!d.name || !/^\S+@\S+\.\S+$/.test(email)) return json({ ok: false, error: "missing_fields" }, 400);
      const kind = d.kind === "quote" ? "Quote request" : "Reservation";
      const subject = `Chocopump ${kind}: ${d.model || (d.units ? d.units + " units" : "")} - ${d.company || d.name}`.slice(0, 180);
      const rows = ["kind", "model", "units", "name", "company", "email", "zip", "message"]
        .filter((k) => d[k]).map((k) => `<tr><td><b>${k}</b></td><td>${esc(d[k])}</td></tr>`).join("");
      const html = `<p>New ${kind.toLowerCase()} from chocopump.com</p><table cellpadding="6">${rows}</table>` +
        (d.kind === "reserve" ? `<p>Next step: reply with the Stripe payment link for ${esc(d.model)}.</p>` : "");
      const r = await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, "Content-Type": "application/json" },
        body: JSON.stringify({ from: env.LEAD_FROM, to: [env.LEAD_TO], reply_to: email, subject, html }),
      });
      if (!r.ok) return json({ ok: false, error: "send_failed" }, 502);
      return json({ ok: true });
    }
    return env.ASSETS.fetch(request);
  },
};
const json = (o, status = 200) => new Response(JSON.stringify(o), { status, headers: { "Content-Type": "application/json" } });
