# Karaköse Boyacılık web sitesi

Samsun Atakum boyacı Birol Usta'nın sitesi: https://karaköseboyacılık.com.tr

## Yapı
- `config.json` — telefon, çalışma saatleri, hizmet bölgeleri, fiyat hesaplama oranları, Google yorum linki ve yorum mesajı. **Çoğu değişiklik sadece buradan yapılır.**
- `pages/*.html` — her sayfanın içeriği. İlk satırdaki JSON başlık; title, description, URL bilgisi.
- `static/` — CSS, JS, görseller, `.htaccess`, `robots.txt` (olduğu gibi kopyalanır).
- `build.py` — sayfaları ortak üst/alt bölüm, SEO etiketleri ve schema.org verisiyle birleştirip `dist/` klasörüne tam HTML üretir. `sitemap.xml` otomatik oluşur.

## Yayın
`main` dalına her gönderimde GitHub Actions `build.py`'yi çalıştırır ve `dist/` içeriğini FTP ile cPanel'deki `public_html`'e yükler.
Gerekli secret'lar: `FTP_SERVER`, `FTP_USERNAME`, `FTP_PASSWORD` (FTP hesabının dizini `public_html`).

## Yerelde deneme
```
python3 build.py && cd dist && python3 -m http.server
```

## Gizli sayfa
`/yorum-iste/` — Birol Usta'nın iş bitince müşteriye Google yorum mesajı gönderdiği araç (arama motorlarına kapalı).
