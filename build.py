#!/usr/bin/env python3
"""Builds every Chocopump page in English, Italian and Spanish. Run: python3 build.py
Copy lives in i18n.py; this file only holds the templates."""
import pathlib, json, shutil
from i18n import T, LEGAL, COMPARE, FAQ, PRODUCT

ROOT = pathlib.Path(__file__).parent / "public"
SITE = "https://chocopump.com"
LANGS = ["en", "it", "es"]
PFX = {"en": "", "it": "it/", "es": "es/"}
PAGES = {"home": "", "pro": "pro/", "deluxe": "deluxe/", "terms": "terms/", "privacy": "privacy/",
         "shipping": "shipping-returns/", "warranty": "warranty/", "thanks": "thank-you/"}
PRICE = {"pro": 569, "deluxe": 599}
EMAIL = "info@chocopump.com"


def depth(lang, page):
    return (PFX[lang] + PAGES[page]).count("/")


def link(lang_from, page_from, lang_to, page_to, anchor=""):
    up = "../" * depth(lang_from, page_from)
    return f"{up}{PFX[lang_to]}{PAGES[page_to]}index.html{anchor}"


def asset(lang, page, path):
    return "../" * depth(lang, page) + path


def url(lang, page):
    return f"{SITE}/{PFX[lang]}{PAGES[page]}"


def head(lang, page, title, desc, schema="", noindex=False):
    t = T[lang]
    a = lambda p: asset(lang, page, p)
    alts = "".join(f'<link rel="alternate" hreflang="{l}" href="{url(l, page)}">' for l in LANGS)
    alts += f'<link rel="alternate" hreflang="x-default" href="{url("en", page)}">'
    ticker_items = "".join(f'<span class="i"><span class="dot" aria-hidden="true"></span>{x}</span>' for x in t["ticker"])
    langs = "".join(f'<a href="{link(lang, page, l, page)}" hreflang="{l}" lang="{l}" aria-current="{str(l == lang).lower()}">{l.upper()}</a>' for l in LANGS)
    L = lambda p, anc="": link(lang, page, lang, p, anc)
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
{'<meta name="robots" content="noindex">' if noindex else ''}
<link rel="canonical" href="{url(lang, page)}">
{alts}
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{SITE}/img/og.jpg">
<meta property="og:locale" content="{t['locale']}">
<meta name="theme-color" content="#2B1A0E">
<link rel="icon" href="{a('img/favicon.png')}" type="image/png">
<link rel="apple-touch-icon" href="{a('img/apple-touch-icon.png')}">
<link rel="preload" href="{a('fonts/bodoni-moda-latin-500-normal.woff2')}" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{a('css/site.css')}">
<script src="{a('js/config.js')}"></script>
{schema}
</head>
<body>
<div class="ticker" role="region" aria-label="{t['ticker_label']}"><div class="track">{ticker_items}{ticker_items.replace('<span class="i">', '<span class="i" aria-hidden="true">')}</div></div>
<header class="top">
  <div class="wrap">
    <a class="brand" href="{L('home')}" aria-label="Chocopump"><img src="{a('img/logo-160.png')}" alt="Chocopump" width="160" height="176"></a>
    <nav aria-label="{t['nav_label']}">
      <a href="{L('pro')}">PRO</a>
      <a href="{L('deluxe')}">DELUXE</a>
      <a href="{L('home', '#compare')}">{t['nav_compare']}</a>
      <a href="{L('home', '#faq')}">{t['nav_faq']}</a>
      <span class="langs" aria-label="{t['lang_label']}">{langs}</span>
      <a class="btn" href="{L('home', '#versions')}">{t['nav_shop']}</a>
    </nav>
  </div>
</header>
"""


def foot(lang, page, mbar=""):
    t = T[lang]
    a = lambda p: asset(lang, page, p)
    L = lambda p, anc="": link(lang, page, lang, p, anc)
    return f"""
<dialog id="reserve" aria-labelledby="res-h">
  <button class="x" type="button" aria-label="{t['close']}" data-close>×</button>
  <div class="in">
    <p class="kicker">Prenota il tuo</p>
    <h3 id="res-h"><span data-res-model>Chocopump</span></h3>
    <p style="font:500 30px/1 var(--serif);margin:4px 0 14px" data-res-price></p>
    <p>{t['res_p']}</p>
    <form class="formgrid" data-kind="reserve" novalidate>
      <input type="hidden" name="model">
      <label>{t['f_name']}<input name="name" required autocomplete="name"></label>
      <label>{t['f_company']}<input name="company" required autocomplete="organization"></label>
      <label>{t['f_email']}<input type="email" name="email" required autocomplete="email"></label>
      <label>{t['f_units']}<select name="units"><option>1</option><option>2</option><option>3</option><option>4</option><option>5</option></select></label>
      <label class="full">{t['f_zip']}<input name="zip" inputmode="numeric" autocomplete="postal-code"></label>
      <input type="text" name="website" tabindex="-1" autocomplete="off" class="sr" aria-hidden="true">
      <div class="full"><button class="btn" type="submit">{t['res_btn']}</button><p class="form-note">{t['res_note']} <a href="{L('privacy')}">{t['l_privacy']}</a></p><p class="status" role="status"></p></div>
    </form>
  </div>
</dialog>
{mbar}
<footer>
  <div class="wrap">
    <div class="cols">
      <div>
        <img class="flogo" src="{a('img/logo-320.png')}" alt="Chocopump" width="100" height="110">
        <p>{t['foot_brand']} <a href="https://whimgoods.com">whimgoods.com</a></p>
      </div>
      <div class="links">
        <h4>{t['foot_shop']}</h4>
        <a href="{L('pro')}">Chocopump PRO</a><a href="{L('deluxe')}">Chocopump DELUXE</a>
        <a href="{L('home', '#compare')}">{t['nav_compare']}</a><a href="{L('home', '#bulk')}">{t['l_bulk']}</a>
      </div>
      <div class="links">
        <h4>{t['foot_help']}</h4>
        <a href="{L('shipping')}">{t['l_shipping']}</a><a href="{L('warranty')}">{t['l_warranty']}</a>
        <a href="{L('terms')}">{t['l_terms']}</a><a href="{L('privacy')}">{t['l_privacy']}</a>
        <a href="{L('home', '#faq')}">{t['nav_faq']}</a>
      </div>
      <div>
        <h4>{t['foot_contact']}</h4>
        <p>Whimgoods LLC<br>8620 NW 64th St, Ste 13<br>Miami, FL 33166, USA</p>
        <p><a href="mailto:{EMAIL}">{EMAIL}</a></p>
      </div>
    </div>
    <p class="legal">{t['nutella']} Chocopump® {t['reg']} © <span id="yr">2026</span> Whimgoods LLC.</p>
  </div>
</footer>
<script src="{a('js/main.js')}" defer></script>
</body>
</html>
"""


def vid(lang, page, yt, poster, cap, label):
    return (f'<button class="vid" data-yt="{yt}" aria-label="{T[lang]["play"]}: {label}">'
            f'<img src="{asset(lang, page, "img/" + poster)}" alt="" loading="lazy" decoding="async"><span class="play" aria-hidden="true"></span>'
            f'<span class="cap">{cap}</span></button>')


def schema_product(lang, key):
    p = PRODUCT[lang][key]
    img = "hero-pro.webp" if key == "pro" else "deluxe-card.webp"
    d = {"@context": "https://schema.org", "@type": "Product", "name": f"Chocopump {key.upper()}", "sku": f"CHOCOPUMP-{key.upper()}",
         "brand": {"@type": "Brand", "name": "Chocopump"}, "description": p["desc"], "image": f"{SITE}/img/{img}", "countryOfOrigin": "IT",
         "offers": {"@type": "Offer", "price": f"{PRICE[key]}.00", "priceCurrency": "USD", "availability": "https://schema.org/InStock",
                    "url": url(lang, key), "itemCondition": "https://schema.org/NewCondition",
                    "seller": {"@type": "Organization", "name": "Whimgoods LLC"},
                    "shippingDetails": {"@type": "OfferShippingDetails", "shippingRate": {"@type": "MonetaryAmount", "value": "0", "currency": "USD"},
                                        "shippingDestination": {"@type": "DefinedRegion", "addressCountry": "US"}},
                    "hasMerchantReturnPolicy": {"@type": "MerchantReturnPolicy", "applicableCountry": "US",
                                                "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow",
                                                "merchantReturnDays": 14, "returnMethod": "https://schema.org/ReturnByMail",
                                                "returnFees": "https://schema.org/ReturnShippingFees"}}}
    return '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False) + "</script>"


def schema_org():
    d = {"@context": "https://schema.org", "@type": "Organization", "name": "Chocopump", "legalName": "Whimgoods LLC", "url": SITE,
         "logo": f"{SITE}/img/logo-512.png", "email": EMAIL,
         "address": {"@type": "PostalAddress", "streetAddress": "8620 NW 64th St, Ste 13", "addressLocality": "Miami",
                     "addressRegion": "FL", "postalCode": "33166", "addressCountry": "US"}}
    return '<script type="application/ld+json">' + json.dumps(d) + "</script>"


def compare_table(lang, page):
    t = T[lang]
    rows = "".join(f'<tr><th scope="row">{a}</th><td>{b}</td><td>{c}</td></tr>' for a, b, c in COMPARE[lang])
    rows += f'<tr><th scope="row">{t["price"]}</th><td><b data-price="pro">$569</b></td><td><b data-price="deluxe">$599</b></td></tr>'
    tf = (f'<tfoot><tr><td></td><td><a class="btn" href="{link(lang, page, lang, "pro")}">{t["see_pro"]}</a></td>'
          f'<td><a class="btn" href="{link(lang, page, lang, "deluxe")}">{t["see_deluxe"]}</a></td></tr></tfoot>')
    return (f'<div style="overflow-x:auto"><table class="cmp"><caption class="sr">{t["cmp_caption"]}</caption>'
            f'<thead><tr><th scope="col"><span class="sr">{t["feature"]}</span></th><th scope="col">PRO<small>{t["pro_nick"]}</small></th>'
            f'<th scope="col">DELUXE<small>{t["deluxe_nick"]}</small></th></tr></thead><tbody>{rows}</tbody>{tf}</table></div>')


def faq_html(items):
    return "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in items)


def write(lang, page, html):
    d = ROOT / (PFX[lang] + PAGES[page])
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(html)


def home(lang):
    t = T[lang]; page = "home"
    a = lambda p: asset(lang, page, p)
    L = lambda p, anc="": link(lang, page, lang, p, anc)
    schema = schema_org() + schema_product(lang, "pro") + schema_product(lang, "deluxe")
    h = head(lang, page, t["home_title"], t["home_desc"], schema)
    uses = "".join(f"<div><strong>{a_}</strong><span>{b_}</span></div>" for a_, b_ in t["uses"])
    steps = "".join(f"<div><h3>{a_}</h3><p>{b_}</p></div>" for a_, b_ in t["steps"])
    why = "".join(f"<div><h3>{a_}</h3><p>{b_}</p></div>" for a_, b_ in t["why"])
    craft = "".join(f"<li><b>{a_}</b><span>{b_}</span></li>" for a_, b_ in t["craft_items"])
    offer = "".join(f"<li><span>{a_}</span><span>{b_}</span></li>" for a_, b_ in t["offer_items"])
    body = f"""
<main>
<section class="hero" aria-labelledby="h1">
  <div class="wrap">
    <div class="txt">
      <h1 id="h1">La porzione perfetta.<span class="en">{t['hero_sub']}</span></h1>
      <p class="lede">{t['hero_lede']}</p>
      <div class="from"><b>{t['from']} <span data-price="pro" style="font:inherit;color:inherit">$569</span></b><span>{t['hero_terms']}</span></div>
      <div class="ctas"><a class="btn" href="#versions">{t['cta_choose']}</a><a class="btn line" href="#proof">{t['cta_watch']}</a></div>
    </div>
    <div class="pic pic-wrap">
      <img src="{a('img/hero-pro.webp')}" alt="{t['hero_alt']}" width="720" height="827" fetchpriority="high">
      <span class="flag-badge"><span class="flag" aria-hidden="true"></span>{t['made']}</span>
    </div>
  </div>
</section>

<section id="proof" class="vsec proof" aria-labelledby="proof-h">
  <div class="wrap">
    <div class="vhead"><div><p class="kicker">Dicono di noi</p><h2 id="proof-h">{t['proof_h']}</h2></div><p class="lede">{t['proof_p']}</p></div>
    {vid(lang, page, "2-zluRHTiko", "v-2-zluRHTiko.webp", t['proof_cap'], t['proof_cap'])}
    <div class="quote-row">{''.join(f'<div><b>{x}</b>{y}</div>' for x, y in t['proof_facts'])}</div>
  </div>
</section>

<section id="watch" class="vsec white" aria-labelledby="watch-h">
  <div class="wrap">
    <div class="vhead"><div><p class="kicker">Guarda</p><h2 id="watch-h">{t['watch_h']}</h2></div><p class="lede">{t['watch_p']}</p></div>
    {vid(lang, page, "f3OXFhoYY8k", "v-f3OXFhoYY8k.webp", t['watch_cap'], t['watch_cap'])}
  </div>
</section>

<section class="vsec" aria-labelledby="pro-v-h">
  <div class="wrap">
    <div class="vhead"><div><p class="kicker">Il cavallo di battaglia</p><h2 id="pro-v-h">{t['prov_h']}</h2></div><p class="lede">{t['prov_p']}</p></div>
    {vid(lang, page, "uzqIbCOMiGo", "v-uzqIbCOMiGo.webp", t['prov_cap'], t['prov_cap'])}
  </div>
</section>

<section class="white" aria-label="{t['facts_label']}">
  <div class="wrap facts">
    <div><b>≈ 1 oz</b><span class="it">Una tirata, un'oncia</span><span>{t['fact1']}</span></div>
    <div><b>3 kg</b><span class="it">Il barattolo intero</span><span>{t['fact2']}</span></div>
    <div><b>Italia</b><span class="it">Fatto a mano</span><span>{t['fact3']}</span></div>
  </div>
</section>

<section aria-labelledby="how-h">
  <div class="wrap">
    <div class="head"><div><p class="kicker">Semplice</p><h2 id="how-h">{t['how_h']}</h2></div><p class="lede">{t['how_p']}</p></div>
    <div class="steps">{steps}</div>
  </div>
</section>

<section class="white" aria-labelledby="why-h">
  <div class="wrap">
    <div class="head"><div><p class="kicker">Perché</p><h2 id="why-h">{t['why_h']}</h2></div><p class="lede">{t['why_p']}</p></div>
    <div class="steps plain">{why}</div>
  </div>
</section>

<section aria-labelledby="calc-h">
  <div class="wrap">
    <div class="head"><div><p class="kicker">Il conto</p><h2 id="calc-h">{t['calc_h']}</h2></div><p class="lede">{t['calc_p']}</p></div>
    <div class="calc" id="calc">
      <form onsubmit="return false">
        <div class="seg" role="group" aria-label="{t['version']}"><button type="button" data-model="pro" aria-pressed="true">PRO, $569</button><button type="button" data-model="deluxe" aria-pressed="false">DELUXE, $599</button></div>
        <label>{t['c_tub']}<span class="row"><input type="range" id="tub" min="25" max="90" step="1" value="45"><output class="v" id="tubv">$45</output></span></label>
        <label>{t['c_srv']}<span class="row"><input type="range" id="srv" min="5" max="200" step="5" value="40"><output class="v" id="srvv">40</output></span></label>
        <label>{t['c_over']}<span class="row"><input type="range" id="over" min="0" max="50" step="5" value="20"><output class="v" id="overv">20%</output></span></label>
        <label>{t['c_days']}<span class="row"><input type="range" id="days" min="10" max="31" step="1" value="26"><output class="v" id="daysv">26</output></span></label>
      </form>
      <div class="res" aria-live="polite">
        <p class="lbl">{t['c_pays_a']} <span id="modelv">PRO</span> {t['c_pays_b']}</p>
        <div class="pay"><span id="payv">6.4</span><small id="payu">{t['months']}</small></div>
        <p class="sub">{t['c_sub']}</p>
        <small class="fine">{t['c_fine']}</small>
      </div>
    </div>
  </div>
</section>

<section id="versions" class="white" aria-labelledby="ver-h">
  <div class="wrap">
    <div class="head"><div><p class="kicker">Scegli il tuo</p><h2 id="ver-h">{t['ver_h']}</h2></div><p class="lede">{t['ver_p']}</p></div>
    <div class="versions">
      <article class="ver">
        <a class="ph contain" href="{L('pro')}"><img src="{a('img/hero-pro.webp')}" alt="Chocopump PRO" loading="lazy"></a>
        <div class="body">
          <h3>PRO</h3>
          <p class="tag">{PRODUCT[lang]['pro']['tag']}</p>
          <p style="color:var(--cacao);margin:0">{t['pro_card']}</p>
          <p style="margin:6px 0 0;font-weight:600" data-stock="pro"></p>
          <div class="row"><span class="price" data-price="pro">$569</span>
            <div class="links"><a class="more" href="{L('pro')}">{t['details']}</a><a class="btn" href="#reserve" data-buy="pro">{t['buy']} PRO</a></div></div>
          <small style="color:var(--cacao)">{t['free_ship']}</small>
        </div>
      </article>
      <article class="ver">
        <a class="ph" href="{L('deluxe')}"><img src="{a('img/deluxe-card.webp')}" alt="Chocopump DELUXE" loading="lazy"></a>
        <div class="body">
          <h3>DELUXE</h3>
          <p class="tag">{PRODUCT[lang]['deluxe']['tag']}</p>
          <p style="color:var(--cacao);margin:0">{t['deluxe_card']}</p>
          <p style="margin:6px 0 0;font-weight:600" data-stock="deluxe"></p>
          <div class="row"><span class="price" data-price="deluxe">$599</span>
            <div class="links"><a class="more" href="{L('deluxe')}">{t['details']}</a><a class="btn" href="#reserve" data-buy="deluxe">{t['buy']} DELUXE</a></div></div>
          <small style="color:var(--cacao)">{t['free_ship']}</small>
        </div>
      </article>
    </div>
  </div>
</section>

<section id="compare" aria-labelledby="cmp-h">
  <div class="wrap">
    <div class="head"><div><p class="kicker">A confronto</p><h2 id="cmp-h">{t['cmp_h']}</h2></div><p class="lede">{t['cmp_p']}</p></div>
    {compare_table(lang, page)}
  </div>
</section>

<section class="white" aria-labelledby="gal-h">
  <div class="wrap">
    <div class="head"><div><p class="kicker">Bellissimo</p><h2 id="gal-h">{t['gal_h']}</h2></div><p class="lede">{t['gal_p']}</p></div>
    <div class="gallery">
      <figure class="g1"><img src="{a('img/g-cone.webp')}" alt="{t['g1']}" loading="lazy"><figcaption>{t['g1']}</figcaption></figure>
      <div class="gr">
        <figure class="g2"><img src="{a('img/g-deluxe-pour.webp')}" alt="{t['g2']}" loading="lazy"><figcaption>{t['g2']}</figcaption></figure>
        <figure class="g3 wide"><img src="{a('img/g-croissant.webp')}" alt="{t['g3']}" loading="lazy"><figcaption>{t['g3']}</figcaption></figure>
      </div>
    </div>
  </div>
</section>

<section class="dark" aria-labelledby="craft-h">
  <div class="wrap craft">
    <div class="pic" style="background:#fff"><img src="{a('img/g-pro-side.webp')}" alt="Chocopump PRO" loading="lazy" style="object-fit:contain"></div>
    <div>
      <p class="kicker">Fatto bene</p>
      <h2 id="craft-h">{t['craft_h']}</h2>
      <p class="lede" style="margin-top:22px">{t['craft_p']}</p>
      <ul>{craft}</ul>
    </div>
  </div>
</section>

<section aria-labelledby="uses-h">
  <div class="wrap">
    <div class="head"><div><p class="kicker">Dove lavora</p><h2 id="uses-h">{t['uses_h']}</h2></div><p class="lede">{t['uses_p']}</p></div>
    <div class="uses">{uses}</div>
  </div>
</section>

<section class="white" aria-labelledby="offer-h">
  <div class="wrap">
    <div class="head"><div><p class="kicker">Tutto incluso</p><h2 id="offer-h">{t['offer_h']}</h2></div><p class="lede">{t['offer_p']}</p></div>
    <div class="offer">
      <ul>{offer}</ul>
      <div class="total">
        <p class="it" style="font-size:22px">Edizione limitata</p>
        <span class="amt">PRO <span data-price="pro">$569</span><br>DELUXE <span data-price="deluxe">$599</span></span>
        <p>{t['offer_total']}</p>
        <a class="btn" href="#versions">{t['cta_choose_short']}</a>
      </div>
    </div>
  </div>
</section>

<section id="faq" class="faq" aria-labelledby="faq-h">
  <div class="wrap" style="max-width:880px">
    <p class="kicker">Domande</p>
    <h2 id="faq-h" style="margin-bottom:28px">{t['faq_h']}</h2>
    {faq_html(FAQ[lang])}
  </div>
</section>

<section id="bulk" class="white" aria-labelledby="bulk-h">
  <div class="wrap bulk">
    <div><p class="kicker">Per i professionisti</p><h2 id="bulk-h">{t['bulk_h']}</h2><p class="lede" style="margin-top:20px">{t['bulk_p']}</p></div>
    <form class="formgrid" data-kind="quote" novalidate>
      <label>{t['f_name']}<input name="name" required autocomplete="name"></label>
      <label>{t['f_company']}<input name="company" required autocomplete="organization"></label>
      <label>{t['f_email']}<input type="email" name="email" required autocomplete="email"></label>
      <label>{t['f_howmany']}<input type="number" name="units" min="6" value="10" required></label>
      <label class="full">{t['f_msg']}<textarea name="message"></textarea></label>
      <input type="text" name="website" tabindex="-1" autocomplete="off" class="sr" aria-hidden="true">
      <div class="full"><button class="btn" type="submit">{t['quote_btn']}</button><p class="form-note">{t['res_note']} <a href="{L('privacy')}">{t['l_privacy']}</a></p><p class="status" role="status"></p></div>
    </form>
  </div>
</section>

<section class="dark" aria-labelledby="final-h">
  <div class="wrap" style="text-align:center">
    <p class="kicker">Buon lavoro</p>
    <h2 id="final-h" style="margin:0 auto">{t['final_h']}</h2>
    <p class="lede" style="margin:24px auto 34px">{t['final_p']}</p>
    <div style="display:flex;gap:14px;justify-content:center;flex-wrap:wrap"><a class="btn" href="{L('pro')}">PRO, <span data-price="pro">$569</span></a><a class="btn" href="{L('deluxe')}">DELUXE, <span data-price="deluxe">$599</span></a></div>
  </div>
</section>
</main>
"""
    mbar = f'<div class="mbar"><span class="t">{t["from"]} <span data-price="pro">$569</span><small>{t["mbar_small"]}</small></span><a class="btn" href="#versions">{t["cta_choose_short"]}</a></div>'
    write(lang, page, h + body + foot(lang, page, mbar))


def product(lang, key):
    t = T[lang]; P = PRODUCT[lang][key]; page = key
    a = lambda p: asset(lang, page, p)
    L = lambda p, anc="": link(lang, page, lang, p, anc)
    other = "deluxe" if key == "pro" else "pro"
    imgs = ([("hero-pro.webp", "Chocopump PRO", "contain"), ("g-pro-side.webp", "Chocopump PRO", "contain"),
             ("g-croissant.webp", t["g3"], "cover"), ("g-cone.webp", t["g1"], "cover")] if key == "pro" else
            [("deluxe-card.webp", "Chocopump DELUXE", "cover"), ("g-deluxe-pour.webp", t["g2"], "cover")])
    first = imgs[0]
    thumbs = "".join(f'<button type="button" data-src="{a("img/" + f)}" data-alt="{al}" data-fit="{fit}" aria-current="{"true" if i == 0 else "false"}" aria-label="{al}"><img src="{a("img/" + f)}" alt="" loading="lazy"></button>'
                     for i, (f, al, fit) in enumerate(imgs))
    specs = "".join(f'<tr><th scope="row">{x}</th><td>{y}</td></tr>' for x, y in P["specs"])
    feats = "".join(f"<li>{x}</li>" for x in P["feats"])
    video = ("uzqIbCOMiGo", "v-uzqIbCOMiGo.webp") if key == "pro" else ("f3OXFhoYY8k", "v-f3OXFhoYY8k.webp")
    h = head(lang, page, P["title"], P["desc"], schema_org() + schema_product(lang, key))
    body = f"""
<main>
<div class="wrap">
  <p class="crumbs"><a href="{L('home')}">Chocopump</a> / {key.upper()}</p>
  <div class="pp">
    <div>
      <div class="main pic-wrap{' cover' if first[2] == 'cover' else ''}" id="main-img"><img src="{a('img/' + first[0])}" alt="{first[1]}" fetchpriority="high"><span class="flag-badge"><span class="flag" aria-hidden="true"></span>{t['made']}</span></div>
      <div class="thumbs" data-target="#main-img">{thumbs}</div>
    </div>
    <div>
      <p class="kicker">{P['italian']}</p>
      <h1>Chocopump {key.upper()}</h1>
      <p class="tag">{P['tag']}</p>
      <div class="price" data-price="{key}">${PRICE[key]}</div>
      <p class="incl">{t['pp_incl']}</p>
      <p class="stock" data-stock="{key}"></p>
      <div class="buy"><a class="btn" href="#reserve" data-buy="{key}">{t['buy']} {key.upper()}</a><a class="btn line" href="{L(other)}">{t['see_' + other]}</a></div>
      <ul class="feat">{feats}</ul>
      <p class="form-note" style="margin-top:22px"><a href="{L('shipping')}">{t['l_shipping']}</a> &nbsp; <a href="{L('warranty')}">{t['l_warranty']}</a></p>
    </div>
  </div>
</div>

<section class="white" aria-labelledby="story-h">
  <div class="wrap craft" style="gap:56px">
    <div>{vid(lang, page, video[0], video[1], P['italian'], 'Chocopump ' + key.upper())}</div>
    <div><p class="kicker">Guarda</p><h2 id="story-h">{P['story_h']}</h2><p class="lede" style="margin-top:20px">{P['story']}</p></div>
  </div>
</section>

<section aria-labelledby="spec-h">
  <div class="wrap" style="max-width:960px">
    <p class="kicker">Scheda tecnica</p>
    <h2 id="spec-h" style="margin-bottom:32px">{t['specs']}</h2>
    <table class="specs">{specs}<tr><th scope="row">{t['price']}</th><td><b data-price="{key}">${PRICE[key]}</b></td></tr></table>
  </div>
</section>

<section class="white" aria-labelledby="cmp-h">
  <div class="wrap">
    <div class="head"><div><p class="kicker">A confronto</p><h2 id="cmp-h">{t['pp_cmp_h']}</h2></div><p class="lede">{t['cmp_p']}</p></div>
    {compare_table(lang, page)}
  </div>
</section>

<section class="faq" aria-labelledby="faq-h">
  <div class="wrap" style="max-width:880px">
    <p class="kicker">Domande</p>
    <h2 id="faq-h" style="margin-bottom:28px">{t['pp_faq_h']}</h2>
    {faq_html([FAQ[lang][i] for i in (0, 1, 3, 5, 6, 7)])}
  </div>
</section>

<section class="dark">
  <div class="wrap" style="text-align:center">
    <p class="kicker">Edizione limitata</p>
    <h2 style="margin:0 auto">{t['pp_final_h']}</h2>
    <p class="lede" style="margin:22px auto 32px">{t['pp_final_p']}</p>
    <a class="btn" href="#reserve" data-buy="{key}">{t['buy']} {key.upper()}, <span data-price="{key}">${PRICE[key]}</span></a>
  </div>
</section>
</main>
"""
    mbar = f'<div class="mbar"><span class="t"><span data-price="{key}">${PRICE[key]}</span><small>{key.upper()}. {t["free_ship"]}</small></span><a class="btn" href="#reserve" data-buy="{key}">{t["buy"]}</a></div>'
    write(lang, page, h + body + foot(lang, page, mbar))


def legal(lang, page):
    title, desc, updated, sections = LEGAL[lang][page]
    body = "".join(f"<h2>{h2}</h2>" + "".join(p if p.startswith("<") else f"<p>{p}</p>" for p in ps) for h2, ps in sections)
    html = head(lang, page, f"{title} | Chocopump", desc)
    html += f'<main class="legalpage"><h1>{title}</h1><p class="upd">{updated}</p>{body}</main>'
    write(lang, page, html + foot(lang, page))


def thanks(lang):
    t = T[lang]; page = "thanks"
    html = head(lang, page, f"Grazie | Chocopump", t["thanks_h"], noindex=True)
    html += (f'<main class="dark" style="min-height:70vh;display:flex;align-items:center"><div class="wrap" style="max-width:780px;padding-top:80px;padding-bottom:80px">'
             f'<p class="kicker">Grazie mille</p><h1 style="font-size:clamp(44px,6vw,76px)">{t["thanks_h"]}</h1>'
             f'<p class="lede" style="margin-top:24px">{t["thanks_p"]}</p><p style="margin-top:30px"><a class="btn" href="{link(lang, page, lang, "home")}">{t["thanks_btn"]}</a></p></div></main>')
    write(lang, page, html + foot(lang, page))


def sitemap():
    urls = ""
    for page in PAGES:
        if page == "thanks":
            continue
        for l in LANGS:
            alts = "".join(f'<xhtml:link rel="alternate" hreflang="{x}" href="{url(x, page)}"/>' for x in LANGS)
            urls += f"<url><loc>{url(l, page)}</loc>{alts}</url>"
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">' + urls + "</urlset>\n")


if __name__ == "__main__":
    for old in ["pro", "deluxe", "it", "es", "terms", "privacy", "shipping-returns", "warranty", "thank-you"]:
        shutil.rmtree(ROOT / old, ignore_errors=True)
    (ROOT / "thank-you.html").unlink(missing_ok=True)
    for l in LANGS:
        home(l); product(l, "pro"); product(l, "deluxe")
        for p in ["terms", "privacy", "shipping", "warranty"]:
            legal(l, p)
        thanks(l)
    sitemap()
    print("built", sum(1 for _ in ROOT.rglob("index.html")), "pages")
