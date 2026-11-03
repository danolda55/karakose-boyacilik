// script-v2.js
class KarakosePaintingWebsite {
    constructor() {
        this.contentData = {
            metadata: { phone: "+905052251395" },
            html: '',
            sections: {}
        };
        
        // Mevcut sayfa kontrolü
        const path = window.location.pathname;
        const pageName = path.substring(path.lastIndexOf('/') + 1);
        this.isContentLoadingPage = (pageName === '' || pageName.startsWith('index') || pageName === '/');

        // Sayfa tamamen yüklendiğinde başlat
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    async init() {
        this.setupNavigation();
        this.setupMobileMenu();
        this.setupContactActions();
        
        if (this.isContentLoadingPage) {
            await this.loadContent();
            this.renderContent();
        }

        // Hesaplama aracını başlat
        this.setupLaborCostCalculator();
        
        this.setupScrollAnimations();
        this.setupSchemaMarkup();
        this.setupGTMTracking();
    }

    async loadContent() {
        try {
            const response = await fetch('content.md');
            if (!response.ok) throw new Error('Content not found');
            
            const text = await response.text();
            const parts = text.split('---');
            let markdownContent = text;
            let metadata = { phone: "+905052251395" };

            if (parts.length >= 3 && text.startsWith('---')) {
                try {
                    const parsedMetadata = jsyaml.load(parts[1]);
                    metadata = {...metadata, ...parsedMetadata};
                    markdownContent = parts.slice(2).join('---');
                } catch (e) { console.warn('YAML parse error', e); }
            }
            
            const htmlContent = marked.parse(markdownContent);
            
            this.contentData = {
                metadata,
                html: htmlContent,
                sections: this.parseContentSections(htmlContent)
            };

        } catch (error) {
            console.error('Error:', error);
        }
    }

    parseContentSections(html) {
        const sections = {};
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;

        let currentKey = null;
        let currentHtml = '';

        tempDiv.childNodes.forEach(node => {
            if (node.nodeName === 'H2') {
                if (currentKey) sections[currentKey] = currentHtml.trim();
                currentHtml = '';
                
                const title = node.textContent.toLowerCase();
                if (title.includes('giriş') || title.includes('ana sayfa')) currentKey = 'ana-sayfa';
                else if (title.includes('hakkımızda')) currentKey = 'hakkimizda';
                else if (title.includes('hizmetlerimiz')) currentKey = 'hizmetlerimiz';
                else if (title.includes('portfolyo')) currentKey = 'portfolyo-markdown';
                else if (title.includes('iletişim')) currentKey = 'iletisim';
                else if (title.includes('sss') || title.includes('sorulan')) currentKey = 'sss';
                else currentKey = null;

            } else if (currentKey) {
                currentHtml += node.outerHTML || node.textContent;
            }
        });

        if (currentKey) sections[currentKey] = currentHtml.trim();
        return sections;
    }

    renderContent() {
        if (!this.contentData || !this.isContentLoadingPage) return;
        
        Object.keys(this.contentData.sections).forEach(key => {
            const elId = key === 'portfolyo-markdown' ? 'portfolyo-content-markdown' : `${key}-content`;
            const el = document.getElementById(elId);
            if (el) {
                el.innerHTML = this.contentData.sections[key];
            }
        });

        if (this.contentData.sections['sss']) {
            const faqContainer = document.getElementById('sss-content');
            if (faqContainer) {
                faqContainer.innerHTML = this.contentData.sections['sss'];
                const items = faqContainer.querySelectorAll('h3');
                items.forEach(h3 => {
                    h3.className = 'text-lg font-bold text-slate-900 mt-4 mb-2';
                    if(h3.nextElementSibling && h3.nextElementSibling.tagName === 'P') {
                        h3.nextElementSibling.className = 'text-slate-600 mb-4 pl-4 border-l-2 border-primary/30';
                    }
                });
                this.setupFAQSchema();
            }
        }
        
        this.addInternalLinks(document.body);
    }

    addInternalLinks(element) {
        element.querySelectorAll('a[href^="#"]').forEach(link => {
            link.addEventListener('click', (e) => {
                const targetId = link.getAttribute('href').substring(1);
                const target = document.getElementById(targetId);
                if (target) {
                    e.preventDefault();
                    const headerOffset = 80; 
                    const elementPosition = target.getBoundingClientRect().top;
                    const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
            
                    window.scrollTo({
                        top: offsetPosition,
                        behavior: "smooth"
                    });
                    
                    const mobileMenu = document.getElementById('mobile-menu');
                    if(mobileMenu && !mobileMenu.classList.contains('hidden')) {
                         mobileMenu.classList.add('hidden');
                    }
                }
            });
        });
    }

    setupNavigation() {
        const nav = document.querySelector('nav');
        window.addEventListener('scroll', () => {
            if (window.scrollY > 10) {
                nav.classList.add('shadow-md', 'bg-white/95', 'backdrop-blur-sm');
                nav.classList.remove('shadow-sm');
            } else {
                nav.classList.remove('shadow-md', 'bg-white/95', 'backdrop-blur-sm');
                nav.classList.add('shadow-sm');
            }
        });
    }
    
    setupMobileMenu() {
        const btn = document.getElementById('mobile-menu-btn');
        const menu = document.getElementById('mobile-menu');
        
        if (btn && menu) {
            const newBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(newBtn, btn);
            
            newBtn.addEventListener('click', (e) => {
                e.preventDefault();
                menu.classList.toggle('hidden');
            });
            
            // Menü linklerine tıklayınca menüyü kapat
            menu.querySelectorAll('a').forEach(link => {
                link.addEventListener('click', () => {
                    menu.classList.add('hidden');
                });
            });
        }
    }

    setupLaborCostCalculator() {
        const form = document.getElementById('calculator-form');
        
        // Eğer form yoksa işlemi durdur
        if (!form) return;

        // Eski event listenerları temizlemek için formu klonla ve değiştir
        const newForm = form.cloneNode(true);
        form.parentNode.replaceChild(newForm, form);

        // Yeni forma event listener ekle
        newForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            // DÜZELTME: Sonuç kutularını form gönderildiği ANDA (submit anında) 
            // belgeden yeniden seçiyoruz. Çünkü form klonlanınca eski referanslar çöp oldu.
            const resultContainer = document.getElementById('calculator-result-container');
            const resultDiv = document.getElementById('calculator-result');
            
            const formData = new FormData(newForm);
            const area = parseFloat(formData.get('area'));
            const status = formData.get('property_status');
            const colorType = formData.get('color_change_type');

            if (!area || area <= 0) {
                alert('Lütfen geçerli bir metrekare giriniz.');
                return;
            }

            // --- FİYATLANDIRMA MANTIĞI ---
            let baseRate = 0;
            if (status === 'unfurnished') {
                baseRate = 75; // Boş ev m2
            } else {
                baseRate = 90; // Eşyalı ev m2
            }

            let multiplier = 1.0;
            switch (colorType) {
                case 'light_to_light': multiplier = 1.0; break;
                case 'light_to_dark': multiplier = 1.1; break;
                case 'dark_to_light': multiplier = 1.35; break; 
                case 'dark_to_dark': multiplier = 1.0; break;
                default: multiplier = 1.0;
            }

            const estimatedCost = Math.round(area * baseRate * multiplier);
            
            // Sonucu Göster (Artık doğru elementi hedefliyor)
            resultContainer.classList.remove('hidden');
            resultDiv.innerHTML = `
                <div class="animate-fade-in-up">
                    <p class="text-gray-500 text-sm mb-1 uppercase tracking-wide">Tahmini İşçilik Bedeli</p>
                    <p class="text-4xl font-extrabold text-orange-600">${estimatedCost.toLocaleString('tr-TR')} TL</p>
                    <p class="text-xs text-gray-400 mt-2">*Malzeme hariçtir. Kesin fiyat keşif sonrası verilir.</p>
                </div>
            `;
            
            this.pushGTMEvent('calculator_submit', {
                area: area,
                cost: estimatedCost
            });
        });
    }

    setupContactActions() {
        const defaultPhone = '+905052251395';
        const phone = this.contentData.metadata?.phone || defaultPhone;
        const cleanPhone = phone.replace(/\s+/g, '').replace('+', '');

        document.querySelectorAll('a[href^="tel:"]').forEach(a => {
            a.href = `tel:+${cleanPhone}`;
        });

        document.querySelectorAll('a[href*="wa.me"]').forEach(a => {
            a.href = `https://wa.me/${cleanPhone}?text=Merhaba,%20boya%20badana%20hizmetleri%20hakkında%20bilgi%20almak%20istiyorum.`;
        });
    }

    setupFAQSchema() {
        const faqContainer = document.getElementById('sss-content');
        if (!faqContainer) return;

        const questions = [];
        faqContainer.querySelectorAll('h3').forEach(h3 => {
            const answer = h3.nextElementSibling;
            if (answer && answer.tagName === 'P') {
                questions.push({
                    "@type": "Question",
                    "name": h3.textContent,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": answer.textContent
                    }
                });
            }
        });

        if (questions.length > 0) {
            // Varolan schema scripti varsa temizle (tekrar render durumunda)
            const oldScript = document.getElementById('faq-schema');
            if (oldScript) oldScript.remove();

            const script = document.createElement('script');
            script.id = 'faq-schema';
            script.type = 'application/ld+json';
            script.text = JSON.stringify({
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": questions
            });
            document.head.appendChild(script);
        }
    }

    setupSchemaMarkup() {
        const schema = {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": "Karaköse Boyacılık",
            "image": "https://xn--karakseboyaclk-zpb56gba.com.tr/og-image.png",
            "telephone": "+905052251395",
            "url": "https://xn--karakseboyaclk-zpb56gba.com.tr/",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "Atakum",
                "addressLocality": "Atakum",
                "addressRegion": "Samsun",
                "postalCode": "55200",
                "addressCountry": "TR"
            },
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": 41.3325,
                "longitude": 36.2650
            },
            "openingHoursSpecification": {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
                "opens": "08:00",
                "closes": "19:00"
            },
            "priceRange": "₺₺"
        };
        const script = document.createElement('script');
        script.type = 'application/ld+json';
        script.text = JSON.stringify(schema);
        document.head.appendChild(script);
    }

    setupScrollAnimations() {
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate-fade-in-up');
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.1 });
            document.querySelectorAll('.animate-on-scroll').forEach(el => observer.observe(el));
        }
    }

    setupGTMTracking() {
        window.dataLayer = window.dataLayer || [];
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a');
            if (!link) return;
            
            if (link.href.startsWith('tel:')) {
                this.pushGTMEvent('phone_click', { link_url: link.href });
            } else if (link.href.includes('wa.me')) {
                this.pushGTMEvent('whatsapp_click', { link_url: link.href });
            }
        });
    }

    pushGTMEvent(name, params) {
        if(window.dataLayer) {
            window.dataLayer.push({ event: name, ...params });
        }
    }
}

new KarakosePaintingWebsite();