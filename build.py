#!/usr/bin/env python3
"""Karaköse Boyacılık statik site üreticisi.

Kullanım:  python3 build.py   ->  dist/ klasörüne hazır siteyi üretir.

- Ortak ayarlar (telefon, fiyatlar, bölgeler, yorum linki): config.json
- Sayfa içerikleri: pages/*.html  (ilk satırda JSON başlık bilgisi)
- Statik dosyalar (css, js, görseller, .htaccess): static/
Her sayfa tam HTML olarak üretilir; Google içeriği JavaScript beklemeden görür.
"""
import hashlib
import html
import json
import re
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
CFG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
BASE = CFG["baseUrl"].rstrip("/")
TODAY = date.today().isoformat()

# ---------------------------------------------------------------- ikonlar
ICONS = {
    "phone": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>',
    "wa": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.5 14.4c-.3-.1-1.8-.9-2-1s-.5-.1-.7.1-.8 1-1 1.2-.4.2-.7.1a8.1 8.1 0 0 1-4-3.5c-.3-.5.3-.5.9-1.6.1-.2 0-.4 0-.5l-.9-2.2c-.2-.6-.5-.5-.7-.5h-.6a1.1 1.1 0 0 0-.8.4 3.4 3.4 0 0 0-1 2.5 5.9 5.9 0 0 0 1.2 3.1 13.5 13.5 0 0 0 5.2 4.6c1.9.8 2.7.9 3.6.8a3.1 3.1 0 0 0 2-1.4 2.5 2.5 0 0 0 .2-1.4c-.1-.1-.3-.2-.7-.4zM12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2z"/></svg>',
    "calc": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="4" y="2" width="16" height="20" rx="2"/><path d="M8 6h8M8 11h.01M12 11h.01M16 11h.01M8 15h.01M12 15h.01M16 15v3M8 18h4"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/></svg>',
    "clock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>',
    "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12l5 5L20 7"/></svg>',
    "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/></svg>',
    "drop": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2.7l5.7 5.6a8 8 0 1 1-11.4 0z"/></svg>',
    "calendar": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>',
    "home": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 10.5L12 3l9 7.5V21a1 1 0 0 1-1 1h-5v-7h-6v7H4a1 1 0 0 1-1-1z"/></svg>',
    "star": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2l3.1 6.3 6.9 1-5 4.9 1.2 6.8L12 17.8 5.8 21l1.2-6.8-5-4.9 6.9-1z"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
}

NAV = [
    ("/", "Ana Sayfa"),
    ("/hizmetlerimiz/", "Hizmetler"),
    ("/portfolyo/", "Uygulamalar"),
    ("/isicilik-hesapla/", "Fiyat Hesapla"),
    ("/hakkimizda/", "Hakkımızda"),
    ("/iletisim/", "İletişim"),
]

SERVICES = [
    {"url": "/esyali-ev-boyama/", "img": "esyali", "title": "Eşyalı Ev Boyama",
     "text": "Mobilyalar ortada toplanır, naylonla sarılır; prizler ve süpürgelikler bantlanır. Eviniz boya lekesiz teslim edilir.",
     "alt": "Atakum'da eşyalı ev boyama: yatak ve dolap naylonla korunmuş, süpürgelikler bantlanmış"},
    {"url": "/daire-boyama/", "img": "bos-daire", "title": "Daire Boyama",
     "text": "1+1'den 4+1'e boş daire, kiralık ev ve taşınma öncesi boyama. Çoğu daire 1–2 günde biter.",
     "alt": "Atakum'da kırık beyaza boyanmış boş daire odası"},
    {"url": "/ofis-boyama/", "img": "ofis", "title": "Ofis ve İş Yeri",
     "text": "Ofis, klinik, mağaza ve apartman merdiven boşlukları. İşinizi en az aksatacak şekilde planlıyoruz.",
     "alt": "Atakum'da gri ve yeşil boyanmış ofis, yeşil vurgu duvarı"},
    {"url": "/hizmetlerimiz/#renk-danismanligi", "img": "renk", "title": "Renk Danışmanlığı",
     "text": "Ölçüye geldiğimizde karteladan evinizin ışığına ve mobilyanıza uyan tonları birlikte seçiyoruz.",
     "alt": "Renk kartelası ile duvar rengi seçimi"},
]

FAQ = [
    ("Samsun'un nemli havasına karşı nasıl bir boya kullanıyorsunuz?",
     "Atakum sahil şeridinde nem yüksektir. Bu yüzden nefes alan, silinebilir, küf ve kabarmaya dirençli su bazlı iç cephe boyaları kullanıyoruz. Nem lekesi olan duvarlarda önce yüzeyi kurutup uygun astarla hazırlıyoruz."),
    ("Eşyalı evimi boyatmak istiyorum, eşyalarım kirlenir mi?",
     "Hayır. Başlamadan önce mobilyaları odanın ortasında toplayıp koruyucu naylonla sarıyor, zemini örtüyor, priz ve süpürgelikleri maskeleme bandıyla kapatıyoruz. İş bitince evi temizleyip eşyaları yerine koyarak teslim ediyoruz."),
    ("Boya badana işi kaç gün sürer?",
     "Ortalama 3+1 bir daire boşsa 1–2 gün, eşyalıysa koruma ve toparlama zaman aldığı için 2–3 gün sürer. Kesin süreyi ölçüye geldiğimizde söylüyoruz ve sözleştiğimiz gün bitiriyoruz."),
    ("Fiyatlara boya malzemesi dahil mi?",
     "Tercihinize göre. Çoğunlukla malzeme dahil, anahtar teslim fiyat veriyoruz. Dilerseniz boyayı siz alırsınız, biz yalnızca işçilik ücreti alırız. Sitedeki hesaplama aracı yalnızca işçiliği gösterir."),
    ("Ölçüye gelmeniz ücretli mi?",
     "Hayır. Atakum'un tüm mahallelerinde ölçüye gelmemiz ücretsizdir. Evi görüp ölçü aldıktan sonra net fiyatı yazılı olarak iletiyoruz."),
    ("Hangi boya markalarını kullanıyorsunuz?",
     "Polisan, Filli Boya ve Marshall gibi kendini kanıtlamış markaların iç cephe ürünlerini kullanıyoruz. Bütçenize göre silinebilir, ipek mat veya ekonomik seçenekleri ölçüye geldiğimizde anlatıyoruz."),
    ("Renk seçiminde yardımcı oluyor musunuz?",
     "Evet. Ölçüye geldiğimizde yanımızda getirdiğimiz kartelalarla, evinizin ışık alma durumuna ve mobilyalarınıza uyan tonları (kum beji, lületaşı, gri ve yeşil tonları gibi) birlikte seçiyoruz."),
]


def esc(s):
    return html.escape(str(s), quote=True)


def tel_href():
    return "tel:+" + CFG["phoneIntl"]


def wa_href(text="Merhaba Birol Usta, boya badana için fiyat almak istiyorum."):
    from urllib.parse import quote
    return "https://wa.me/" + CFG["phoneIntl"] + "?text=" + quote(text)


def img(name, alt, sizes="(max-width: 760px) 100vw, 50vw", eager=False, cls="", lazy=True):
    attrs = 'fetchpriority="high"' if eager else ('loading="lazy" decoding="async"' if lazy else 'decoding="async"')
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="/img/{name}.webp?v={VERSION}" srcset="/img/{name}-800.webp?v={VERSION} 800w, /img/{name}.webp?v={VERSION} 1600w" '
            f'sizes="{sizes}" width="1600" height="893" alt="{esc(alt)}" {attrs}>')


# ---------------------------------------------------------------- bloklar
def block_services():
    cards = []
    for s in SERVICES:
        cards.append(f'''<a class="card reveal" href="{s["url"]}">
  <div class="card-media">{img(s["img"] + "", s["alt"], "(max-width: 640px) 100vw, (max-width: 1000px) 50vw, 25vw", lazy=False)}</div>
  <div class="card-body"><h3>{esc(s["title"])}</h3><p>{esc(s["text"])}</p><span class="card-link">Detaylar</span></div>
</a>''')
    return '<div class="grid grid-4">' + "\n".join(cards) + "</div>"


def block_faq():
    items = []
    for i, (q, a) in enumerate(FAQ):
        op = " open" if i == 0 else ""
        items.append(f'<details{op}><summary>{esc(q)}</summary><div class="answer"><p>{esc(a)}</p></div></details>')
    return '<div class="faq">' + "\n".join(items) + "</div>"


def block_areas():
    return '<ul class="chips">' + "".join(f"<li>{esc(a)}</li>" for a in CFG["areas"]) + "</ul>"


def block_review():
    return f'''<div class="review-box reveal">
  <div><div class="stars" aria-hidden="true">★★★★★</div><strong>Müşterilerimiz Google'da anlatıyor</strong><p class="small" style="margin:4px 0 0">Bizimle çalıştıysanız birkaç kelimelik yorumunuz bize çok yardımcı olur.</p></div>
  <div class="btn-row"><a class="btn btn-ghost" href="{esc(CFG["mapsUrl"])}" target="_blank" rel="noopener">Yorumları oku</a><a class="btn btn-primary" data-review href="{esc(CFG["reviewUrl"])}" target="_blank" rel="noopener">Yorum yaz</a></div>
</div>'''


def block_cta():
    return f'''<section class="section-sm"><div class="wrap"><div class="cta-band reveal">
  <div><h2>Ücretsiz ölçü için arayın</h2><p>Atakum'da evinize gelip ölçü alalım, net fiyatı yazılı verelim. {esc(CFG["hours"]["daysText"])} {CFG["hours"]["opens"]}–{CFG["hours"]["closes"]}.</p></div>
  <div class="btn-row"><a class="btn btn-light" href="{tel_href()}">{ICONS["phone"]} {esc(CFG["phoneDisplay"])}</a><a class="btn btn-wa" href="{wa_href()}">{ICONS["wa"]} WhatsApp</a></div>
</div></div></section>'''


def block_calc():
    return f'''<form id="calc-form" class="calc" novalidate>
  <label class="field-label" for="area">Evin net alanı (m²)</label>
  <input id="area" name="area" type="number" inputmode="decimal" min="10" max="1000" step="1" placeholder="Örn: 110" required>
  <p class="small" style="margin:8px 0 26px">Tapudaki brüt değil, odaların toplam taban alanı. 2+1 ≈ 85, 3+1 ≈ 110, 4+1 ≈ 140 m².</p>
  <fieldset><legend>Evin durumu</legend><div class="options">
    <label><input type="radio" name="status" value="furnished" checked><span>Eşyalı<small>Koruma ve toparlama dahil</small></span></label>
    <label><input type="radio" name="status" value="unfurnished"><span>Boş<small>Taşınma öncesi / sonrası</small></span></label>
  </div></fieldset>
  <fieldset><legend>Renk değişimi</legend><div class="options">
    <label><input type="radio" name="color" value="light_to_light" checked><span>Açıktan açığa</span></label>
    <label><input type="radio" name="color" value="light_to_dark"><span>Açıktan koyuya</span></label>
    <label><input type="radio" name="color" value="dark_to_light"><span>Koyudan açığa<small>Ek kat boya gerekir</small></span></label>
    <label><input type="radio" name="color" value="dark_to_dark"><span>Koyudan koyuya</span></label>
  </div></fieldset>
  <p id="calc-error" class="calc-error" role="alert"></p>
  <button class="btn btn-accent btn-block" type="submit">{ICONS["calc"]} Tahmini işçiliği hesapla</button>
  <div id="calc-result" class="calc-result" hidden aria-live="polite">
    <div class="label">Tahmini işçilik</div>
    <div id="calc-price" class="price"></div>
    <p class="note">Malzeme hariçtir. Kesin fiyat evinizi ücretsiz gördükten sonra verilir.</p>
    <a id="calc-wa" class="btn btn-wa" href="{wa_href()}">{ICONS["wa"]} Bu hesapla WhatsApp'tan teklif iste</a>
  </div>
</form>'''


def block_map():
    return (f'<div class="map"><iframe src="{esc(CFG["mapsEmbed"])}" title="Karaköse Boyacılık Google Haritalar konumu" '
            f'loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></div>')


def block_contact():
    h = CFG["hours"]
    return f'''<div class="contact-card">
  <ul class="contact-list">
    <li>{ICONS["phone"]}<div><strong>Telefon</strong><a href="{tel_href()}">{esc(CFG["phoneDisplay"])}</a></div></li>
    <li>{ICONS["wa"]}<div><strong>WhatsApp</strong><a href="{wa_href()}">Mesaj gönderin, fotoğraf atın</a></div></li>
    <li>{ICONS["pin"]}<div><strong>Adres ve hizmet bölgesi</strong>{esc(CFG["streetAddress"])}, {CFG["postalCode"]} {esc(CFG["district"])}/{esc(CFG["city"])}<br>Atakum'un tüm mahallelerinde hizmet veriyoruz.<br><a href="{esc(CFG["mapsUrl"])}" target="_blank" rel="noopener">Google Haritalar'da aç</a></div></li>
    <li>{ICONS["clock"]}<div><strong>Çalışma saatleri</strong>{esc(h["daysText"])}, {h["opens"]}–{h["closes"]}</div></li>
  </ul>
  <div class="btn-row"><a class="btn btn-primary" href="{tel_href()}">{ICONS["phone"]} Hemen ara</a><a class="btn btn-wa" href="{wa_href()}">{ICONS["wa"]} WhatsApp</a></div>
</div>'''


BLOCKS = {
    "services": block_services, "faq": block_faq, "areas": block_areas, "review": block_review,
    "cta": block_cta, "calc": block_calc, "map": block_map, "contact": block_contact,
}


# ---------------------------------------------------------------- şema (JSON-LD)
def business_schema():
    h = CFG["hours"]
    return {
        "@type": "HousePainter",
        "@id": BASE + "/#isletme",
        "name": CFG["siteName"],
        "alternateName": "Karaköse Boyacılık – Birol Usta",
        "description": "Samsun Atakum'da eşyalı ev, daire ve ofis iç cephe boya badana hizmeti.",
        "url": BASE + "/",
        "telephone": "+" + CFG["phoneIntl"],
        "image": [BASE + "/img/og.jpg", BASE + "/img/hero.webp"],
        "logo": BASE + "/assets/icons/icon-512.png",
        "priceRange": "₺₺",
        "currenciesAccepted": "TRY",
        "paymentAccepted": "Nakit, Havale/EFT",
        "foundingDate": str(CFG["foundingYear"]),
        "founder": {"@type": "Person", "name": CFG["owner"]},
        "address": {"@type": "PostalAddress", "streetAddress": CFG["streetAddress"], "addressLocality": CFG["district"], "addressRegion": CFG["city"],
                    "postalCode": CFG["postalCode"], "addressCountry": "TR"},
        "geo": {"@type": "GeoCoordinates", "latitude": CFG["geo"]["lat"], "longitude": CFG["geo"]["lng"]},
        "hasMap": CFG["mapsUrl"],
        "sameAs": [CFG["mapsUrl"]],
        "areaServed": [{"@type": "AdministrativeArea", "name": "Atakum, Samsun"}] + [{"@type": "Place", "name": a + ", Atakum, Samsun"} for a in CFG["areas"]],
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": h["days"], "opens": h["opens"], "closes": h["closes"]}],
        "knowsAbout": ["iç cephe boyama", "eşyalı ev boyama", "daire boyama", "ofis boyama", "alçı ve macun tamiri", "renk danışmanlığı"],
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Boya badana hizmetleri", "itemListElement": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["title"], "url": BASE + s["url"].split("#")[0]}} for s in SERVICES]},
    }


def page_schema(meta, url):
    graph = [business_schema(), {"@type": "WebSite", "@id": BASE + "/#site", "url": BASE + "/", "name": CFG["siteName"], "inLanguage": "tr-TR", "publisher": {"@id": BASE + "/#isletme"}}]
    graph.append({"@type": "WebPage", "@id": url + "#sayfa", "url": url, "name": meta["title"], "description": meta["description"],
                  "isPartOf": {"@id": BASE + "/#site"}, "about": {"@id": BASE + "/#isletme"}, "inLanguage": "tr-TR",
                  "primaryImageOfPage": BASE + "/img/" + meta.get("image", "hero") + ".webp", "dateModified": TODAY})
    if meta["path"] != "/":
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Ana Sayfa", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": meta["crumb"], "item": url}]})
    if meta.get("service"):
        graph.append({"@type": "Service", "name": meta["service"], "serviceType": meta["service"], "url": url,
                      "provider": {"@id": BASE + "/#isletme"}, "areaServed": {"@type": "AdministrativeArea", "name": "Atakum, Samsun"}})
    if meta.get("faq"):
        graph.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]})
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))


# ---------------------------------------------------------------- iskelet
def header(active):
    links = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == active else ""
        links.append(f'<a href="{href}"{cur}>{label}</a>')
    return f'''<a class="skip" href="#icerik">İçeriğe geç</a>
<header class="site-header"><div class="wrap header-inner">
  <a class="logo" href="/" aria-label="Karaköse Boyacılık ana sayfa"><span class="logo-mark">K</span><span class="logo-text"><strong>Karaköse Boyacılık</strong><span>Birol Usta · Atakum</span></span></a>
  <button class="menu-btn" aria-label="Menüyü aç" aria-expanded="false" aria-controls="site-nav">{ICONS["menu"]}</button>
  <nav id="site-nav" class="nav" aria-label="Ana menü">{"".join(links)}<a class="btn btn-primary" href="{tel_href()}">{ICONS["phone"]} {esc(CFG["phoneDisplay"])}</a></nav>
</div></header>'''


def footer():
    svc = "".join(f'<li><a href="{s["url"]}">{esc(s["title"])}</a></li>' for s in SERVICES[:3])
    return f'''<footer class="site-footer"><div class="wrap">
  <div class="footer-grid">
    <div><a class="logo" href="/"><span class="logo-mark">K</span><span class="logo-text"><strong>Karaköse Boyacılık</strong><span>Birol Usta · Atakum</span></span></a>
      <p style="margin-top:18px;max-width:320px">{CFG["foundingYear"]}'dan beri Samsun Atakum'da temiz, titiz ve sözünde iç cephe boya badana.</p></div>
    <div><h3>Hizmetler</h3><ul>{svc}<li><a href="/isicilik-hesapla/">Fiyat hesapla</a></li></ul></div>
    <div><h3>Kurumsal</h3><ul><li><a href="/hakkimizda/">Hakkımızda</a></li><li><a href="/portfolyo/">Uygulamalar</a></li><li><a href="/iletisim/">İletişim</a></li><li><a href="{esc(CFG["reviewUrl"])}" target="_blank" rel="noopener" data-review>Google'da yorum yaz</a></li></ul></div>
    <div><h3>İletişim</h3><ul><li><a href="{tel_href()}">{esc(CFG["phoneDisplay"])}</a></li><li><a href="{wa_href()}">WhatsApp</a></li><li>{esc(CFG["streetAddress"])}<br>{CFG["postalCode"]} {esc(CFG["district"])}/{esc(CFG["city"])}</li><li>{esc(CFG["hours"]["daysText"])}<br>{CFG["hours"]["opens"]}–{CFG["hours"]["closes"]}</li></ul></div>
  </div>
  <div class="footer-bottom"><span>© {date.today().year} Karaköse Boyacılık · Samsun Atakum boyacı</span><span>Hizmet bölgesi: Atakum / Samsun</span></div>
</div></footer>
<nav class="mobile-bar" aria-label="Hızlı iletişim">
  <a class="call" href="{tel_href()}">{ICONS["phone"]}Ara</a>
  <a class="wa" href="{wa_href()}">{ICONS["wa"]}WhatsApp</a>
  <a href="/isicilik-hesapla/">{ICONS["calc"]}Fiyat hesapla</a>
</nav>'''


def head(meta, url):
    robots = meta.get("robots", "index, follow, max-image-preview:large")
    og_img = BASE + "/img/og.jpg"
    gtm = CFG["gtmId"]
    gtm_js = "" if meta.get("noGtm") else f"""<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);}})(window,document,'script','dataLayer','{gtm}');</script>"""
    preload = f'<link rel="preload" as="image" href="/img/{meta["preload"]}.webp?v={VERSION}" imagesrcset="/img/{meta["preload"]}-800.webp?v={VERSION} 800w, /img/{meta["preload"]}.webp?v={VERSION} 1600w" imagesizes="(max-width: 900px) 100vw, 50vw">' if meta.get("preload") else ""
    schema = "" if meta.get("noSchema") else f'<script type="application/ld+json">{page_schema(meta, url)}</script>'
    cfg_keys = ("phoneIntl", "prices", "reviewUrl", "reviewMessage") if meta.get("app") else ("phoneIntl", "prices")
    js_cfg = {k: CFG[k] for k in cfg_keys}
    if meta.get("app"):
        js_cfg["reviewUrl"] = CFG.get("appReviewUrl") or CFG["reviewUrl"]
    js_cfg = json.dumps(js_cfg, ensure_ascii=False)
    manifest = CFG["appPath"] + "manifest.webmanifest" if meta.get("app") else "/manifest.webmanifest"
    app_meta = '<meta name="apple-mobile-web-app-capable" content="yes">\n<meta name="apple-mobile-web-app-title" content="Yorum İste">\n<meta name="mobile-web-app-capable" content="yes">' if meta.get("app") else ""
    return f'''<!DOCTYPE html>
<html lang="tr" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(meta["title"])}</title>
<meta name="description" content="{esc(meta["description"])}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#1f4d47">
<meta name="geo.region" content="TR-55">
<meta name="geo.placename" content="Atakum, Samsun">
<meta name="geo.position" content="{CFG["geo"]["lat"]};{CFG["geo"]["lng"]}">
<meta property="og:type" content="website">
<meta property="og:locale" content="tr_TR">
<meta property="og:site_name" content="{esc(CFG["siteName"])}">
<meta property="og:title" content="{esc(meta.get("ogTitle", meta["title"]))}">
<meta property="og:description" content="{esc(meta["description"])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/assets/icons/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/icons/apple-touch-icon.png">
<link rel="manifest" href="{manifest}">
{app_meta}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap">
<link rel="stylesheet" href="/assets/css/site.css?v={VERSION}">
{preload}
{schema}
<script>window.KB_CONFIG={js_cfg};</script>
{gtm_js}
</head>'''


def render(page_file):
    raw = page_file.read_text(encoding="utf-8")
    m = re.match(r"\s*<!--\s*(\{.*?\})\s*-->\s*", raw, re.S)
    meta = json.loads(m.group(1))
    if meta.get("app"):
        meta["path"] = CFG["appPath"]
        meta["file"] = CFG["appPath"].strip("/") + "/index.html"
    body = raw[m.end():]
    body = re.sub(r"\{\{\s*block:(\w+)\s*\}\}", lambda x: BLOCKS[x.group(1)](), body)
    body = re.sub(r"\{\{\s*icon:(\w+)\s*\}\}", lambda x: ICONS[x.group(1)], body)
    body = re.sub(r"\{\{\s*img:([\w-]+)\|([^|}]*)(?:\|(eager))?\s*\}\}", lambda x: img(x.group(1), x.group(2), eager=bool(x.group(3))), body)
    repl = {"tel": tel_href(), "wa": wa_href(), "phone": esc(CFG["phoneDisplay"]), "maps": esc(CFG["mapsUrl"]),
            "review": esc(CFG["reviewUrl"]), "year": str(CFG["foundingYear"]),
            "years": str(date.today().year - CFG["foundingYear"])}
    body = re.sub(r"\{\{\s*(\w+)\s*\}\}", lambda x: repl[x.group(1)], body)

    url = BASE + meta["path"]
    gtm_ns = "" if meta.get("noGtm") else f'<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={CFG["gtmId"]}" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>'
    scripts = '<script src="/assets/js/site.js?v=' + VERSION + '" defer></script>'
    for extra in meta.get("scripts", []):
        scripts += f'\n<script src="{extra}?v={VERSION}" defer></script>'
    if meta.get("app"):
        scripts += f'\n<script>if("serviceWorker" in navigator)navigator.serviceWorker.register("{CFG["appPath"]}sw.js",{{scope:"{CFG["appPath"]}"}});</script>'
    chrome = not meta.get("bare")
    doc = head(meta, url) + "\n<body>\n" + gtm_ns + "\n"
    if chrome:
        doc += header(meta["path"]) + "\n"
    doc += '<main id="icerik">\n' + body.strip() + "\n</main>\n"
    if chrome:
        doc += footer() + "\n"
    doc += scripts + "\n</body>\n</html>\n"
    return meta, doc


def build():
    global VERSION
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(ROOT / "static", DIST)
    files = sorted((ROOT / "static/assets").rglob("*.*")) + sorted((ROOT / "static/img").glob("*.*"))
    VERSION = hashlib.md5(b"".join(p.read_bytes() for p in files)).hexdigest()[:8]
    sitemap = []
    for pf in sorted((ROOT / "pages").glob("*.html")):
        meta, doc = render(pf)
        out = DIST / meta["file"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(doc, encoding="utf-8")
        if meta.get("sitemap", True):
            sitemap.append((BASE + meta["path"], meta.get("priority", "0.7")))
    app_dir = DIST / CFG["appPath"].strip("/")
    (app_dir / "manifest.webmanifest").write_text(json.dumps({
        "name": "Yorum İste – Karaköse", "short_name": "Yorum İste", "id": CFG["appPath"],
        "start_url": CFG["appPath"], "scope": CFG["appPath"], "display": "standalone",
        "background_color": "#f8f5ef", "theme_color": "#1f4d47", "lang": "tr",
        "icons": [{"src": "/assets/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/assets/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}]},
        ensure_ascii=False, indent=2), encoding="utf-8")
    for php in sorted((ROOT / "server").glob("*.php")):
        shutil.copy(php, app_dir / php.name)
    (app_dir / "sw.js").write_text("const C='yorum-" + VERSION + "';self.addEventListener('install',e=>{self.skipWaiting();e.waitUntil(caches.open(C).then(c=>c.addAll(['./'])))});self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x)))).then(()=>self.clients.claim())));self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;if(e.request.url.indexOf('.php')>-1)return;e.respondWith(fetch(e.request).then(r=>{const cp=r.clone();caches.open(C).then(c=>c.put(e.request,cp));return r}).catch(()=>caches.match(e.request)))});\n", encoding="utf-8")
    sitemap.sort(key=lambda x: -float(x[1]))
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, pr in sitemap:
        xml.append(f"  <url><loc>{loc}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority></url>")
    xml.append("</urlset>")
    (DIST / "sitemap.xml").write_text("\n".join(xml) + "\n", encoding="utf-8")
    print(f"{len(sitemap)} sayfa sitemap'te, dist/ hazır.")


VERSION = "1"
if __name__ == "__main__":
    build()
