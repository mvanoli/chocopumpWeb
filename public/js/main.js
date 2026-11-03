(function () {
  var C = window.CHOCOPUMP || {};
  var M = C.models || {};
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var money = function (n) { return "$" + Number(n).toLocaleString("en-US"); };
  var L = (document.documentElement.lang || "en").slice(0, 2);
  var S = {
    en: { lot: function (n) { return "Limited lot: " + n + " units available in the USA"; }, sold: "This limited lot is sold out. Reserve one from the next.", soldBtn: "Reserve from the next lot",
          add: "Add your ", cont: " to continue.", sending: "Sending…", okRes: "Grazie! Reserved. Check your email for the payment link.", okQ: "Grazie! We'll reply by email.",
          err: function (e) { return "That didn't go through. Email us at " + e + " and we'll take it from there."; }, m: "month", ms: "months", d: "days" },
    it: { lot: function (n) { return "Lotto limitato: " + n + " pezzi disponibili negli USA"; }, sold: "Questo lotto limitato è esaurito. Prenota dal prossimo.", soldBtn: "Prenota dal prossimo lotto",
          add: "Inserisci ", cont: " per continuare.", sending: "Invio…", okRes: "Grazie! Prenotato. Controlla la tua email per il link di pagamento.", okQ: "Grazie! Ti risponderemo via email.",
          err: function (e) { return "Invio non riuscito. Scrivici a " + e + " e ci pensiamo noi."; }, m: "mese", ms: "mesi", d: "giorni" },
    es: { lot: function (n) { return "Lote limitado: " + n + " unidades disponibles en EE. UU."; }, sold: "Este lote limitado está agotado. Reserva uno del próximo.", soldBtn: "Reservar del próximo lote",
          add: "Completa ", cont: " para continuar.", sending: "Enviando…", okRes: "¡Grazie! Reservado. Revisa tu correo para el enlace de pago.", okQ: "¡Grazie! Te responderemos por correo.",
          err: function (e) { return "No se pudo enviar. Escríbenos a " + e + " y lo resolvemos."; }, m: "mes", ms: "meses", d: "días" }
  };
  S = S[L] || S.en;



  // Prices and limited-lot quantities
  $$("[data-price]").forEach(function (el) { var m = M[el.dataset.price]; if (m) el.textContent = money(m.price); });
  $$("[data-units]").forEach(function (el) { var m = M[el.dataset.units]; if (m) el.textContent = m.lotUnits; });
  $$("[data-stock]").forEach(function (el) {
    var m = M[el.dataset.stock]; if (!m) return;
    el.textContent = m.soldOut ? S.sold : S.lot(m.lotUnits);
  });
  $$("[data-email]").forEach(function (a) { if (C.contactEmail) { a.href = "mailto:" + C.contactEmail; if (a.textContent.indexOf("@") > -1) a.textContent = C.contactEmail; } });
  var yr = $("#yr"); if (yr) yr.textContent = new Date().getFullYear();

  // Buy buttons: Stripe link if set, otherwise the reserve dialog
  var dlg = $("#reserve");
  function openReserve(key) {
    var m = M[key]; if (!dlg || !m) return;
    $("[data-res-model]", dlg).textContent = m.name;
    $("[data-res-price]", dlg).textContent = money(m.price);
    $('input[name="model"]', dlg).value = m.name;
    if (dlg.showModal) dlg.showModal(); else dlg.setAttribute("open", "");
  }
  $$("[data-buy]").forEach(function (b) {
    var key = b.dataset.buy, m = M[key]; if (!m) return;
    if (m.soldOut) b.textContent = S.soldBtn;
    else if (m.checkout) { var lg = (document.documentElement.lang || "en").slice(0, 2); b.href = m.checkout + (lg !== "en" ? "?locale=" + lg : ""); b.rel = "noopener"; return; }
    b.addEventListener("click", function (e) { e.preventDefault(); openReserve(key); });
  });
  if (dlg) {
    $("[data-close]", dlg).addEventListener("click", function () { dlg.close(); });
    dlg.addEventListener("click", function (e) { if (e.target === dlg) dlg.close(); });
  }

  // Forms -> /api/lead
  $$("form[data-kind]").forEach(function (f) {
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var status = $(".status", f); status.className = "status";
      var bad = $$("[required]", f).find(function (i) { return !i.value.trim() || (i.type === "email" && !/^\S+@\S+\.\S+$/.test(i.value)); });
      if (bad) { status.textContent = S.add + bad.closest("label").firstChild.textContent.trim().toLowerCase() + S.cont; status.classList.add("err"); bad.focus(); return; }
      var data = Object.fromEntries(new FormData(f).entries()); data.kind = f.dataset.kind; data.lang = L;
      var btn = $('button[type="submit"]', f), label = btn.textContent; btn.disabled = true; btn.textContent = S.sending;
      fetch("/api/lead", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) })
        .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
        .then(function () { status.textContent = data.kind === "reserve" ? S.okRes : S.okQ; status.classList.add("ok"); f.reset(); })
        .catch(function () { status.textContent = S.err(C.contactEmail); status.classList.add("err"); })
        .finally(function () { btn.disabled = false; btn.textContent = label; });
    });
  });

  // Video facades: YouTube loads only on click
  $$(".vid[data-yt]").forEach(function (v) {
    v.addEventListener("click", function () {
      if ($("iframe", v)) return;
      var f = document.createElement("iframe");
      f.src = "https://www.youtube-nocookie.com/embed/" + v.dataset.yt + "?autoplay=1&rel=0";
      f.allow = "autoplay; encrypted-media; picture-in-picture"; f.allowFullscreen = true; f.title = v.getAttribute("aria-label");
      v.appendChild(f);
    });
  });

  // Product gallery
  $$(".thumbs").forEach(function (t) {
    var main = $(t.dataset.target);
    $$("button", t).forEach(function (b) {
      b.addEventListener("click", function () {
        $$("button", t).forEach(function (x) { x.setAttribute("aria-current", "false"); });
        b.setAttribute("aria-current", "true");
        var img = $("img", main); img.src = b.dataset.src; img.alt = b.dataset.alt || "";
        main.classList.toggle("cover", b.dataset.fit === "cover");
      });
    });
  });

  // Calculator: payback is the headline
  var calc = $("#calc");
  if (calc) {
    var model = "pro";
    $$(".seg button", calc).forEach(function (b) {
      b.addEventListener("click", function () {
        model = b.dataset.model;
        $$(".seg button", calc).forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
        run();
      });
    });
    function run() {
      var tub = +$("#tub").value, srv = +$("#srv").value, over = +$("#over").value / 100, days = +$("#days").value;
      $("#tubv").textContent = "$" + tub; $("#srvv").textContent = srv; $("#overv").textContent = Math.round(over * 100) + "%"; $("#daysv").textContent = days;
      var loss = srv * days * over * (tub / 105.8);
      var price = M[model].price;
      $("#lossv").textContent = money(Math.round(loss));
      $("#pricev").textContent = money(price);
      $("#modelv").textContent = model === "pro" ? "PRO" : "DELUXE";
      var n = $("#payv"), u = $("#payu");
      if (loss < 1) { n.textContent = "–"; u.textContent = ""; return; }
      var months = price / loss;
      if (months < 1) { n.textContent = Math.max(1, Math.round(months * 30)); u.textContent = S.d; }
      else { var r = Math.round(months * 10) / 10; n.textContent = r % 1 === 0 ? r.toFixed(0) : r.toFixed(1); u.textContent = r === 1 ? S.m : S.ms; }
    }
    ["tub", "srv", "over", "days"].forEach(function (id) { $("#" + id).addEventListener("input", run); });
    run();
  }
})();
