/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";


// Sticky header — adds .is-scrolled past 40px
publicWidget.registry.HeaderScroll = publicWidget.Widget.extend({
    selector: "#ca-header",

    start() {
        this._onScroll = this._onScroll.bind(this);
        window.addEventListener("scroll", this._onScroll, { passive: true });
        this._onScroll();
        return this._super(...arguments);
    },

    destroy() {
        window.removeEventListener("scroll", this._onScroll);
        this._super(...arguments);
    },

    _onScroll() {
        if (window.scrollY > 40) {
            this.el.classList.add("is-scrolled");
        } else {
            this.el.classList.remove("is-scrolled");
        }
    },
});


// Scroll reveal — adds .is-visible to [data-reveal] elements as they enter viewport
publicWidget.registry.ScrollReveal = publicWidget.Widget.extend({
    selector: "main",

    start() {
        const targets = this.el.querySelectorAll("[data-reveal]");
        if (!targets.length) return this._super(...arguments);

        if (!("IntersectionObserver" in window)) {
            targets.forEach((el) => el.classList.add("is-visible"));
            return this._super(...arguments);
        }

        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                }
            });
        }, {
            rootMargin: "0px 0px -8% 0px",
            threshold: 0.05,
        });

        targets.forEach((el) => observer.observe(el));
        return this._super(...arguments);
    },
});


// FAQ accordion
publicWidget.registry.FaqAccordion = publicWidget.Widget.extend({
    selector: ".ca-faq",

    start() {
        const items = this.el.querySelectorAll(".ca-faq-item");
        items.forEach((item) => {
            const q = item.querySelector(".ca-faq-q");
            if (!q) return;
            q.addEventListener("click", (e) => {
                e.preventDefault();
                item.classList.toggle("open");
            });
        });
        return this._super(...arguments);
    },
});


// Contact path tabs (Sellers vs Buyers)
publicWidget.registry.ContactPaths = publicWidget.Widget.extend({
    selector: "#ca-paths",

    start() {
        const paths = this.el.querySelectorAll(".ca-path");
        const sellerFields = document.querySelector(".ca-form-seller-only");
        const buyerFields = document.querySelector(".ca-form-buyer-only");
        const inquiryType = document.getElementById("inquiry_type");

        paths.forEach((btn) => {
            btn.addEventListener("click", (e) => {
                e.preventDefault();
                paths.forEach((b) => b.classList.remove("active"));
                btn.classList.add("active");
                const path = btn.getAttribute("data-path");
                if (inquiryType) inquiryType.value = path;
                if (path === "buyer") {
                    if (sellerFields) sellerFields.classList.add("ca-hidden");
                    if (buyerFields) buyerFields.classList.remove("ca-hidden");
                } else {
                    if (buyerFields) buyerFields.classList.add("ca-hidden");
                    if (sellerFields) sellerFields.classList.remove("ca-hidden");
                }
            });
        });
        return this._super(...arguments);
    },
});


// Mark active language pill
publicWidget.registry.LangActive = publicWidget.Widget.extend({
    selector: "#ca-lang",

    start() {
        const html = document.documentElement.getAttribute("lang") || "";
        const match = html.toLowerCase().startsWith("es") ? "es" : "en";
        this.el.querySelectorAll("a").forEach((a) => {
            if (a.getAttribute("data-lang") === match) a.classList.add("active");
        });
        return this._super(...arguments);
    },
});


export default {
    HeaderScroll: publicWidget.registry.HeaderScroll,
    ScrollReveal: publicWidget.registry.ScrollReveal,
    FaqAccordion: publicWidget.registry.FaqAccordion,
    ContactPaths: publicWidget.registry.ContactPaths,
    LangActive: publicWidget.registry.LangActive,
};
