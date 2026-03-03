/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.HeroCarousel = publicWidget.Widget.extend({
    selector: '.ca-carousel',

    start() {
        this.currentSlide = 0;
        this.autoPlayInterval = null;
        this.slides = this.el.querySelectorAll('.ca-carousel-item');
        this.indicators = this.el.querySelectorAll('.ca-indicator');

        console.log('Carousel initialized with', this.slides.length, 'slides');

        if (this.slides.length === 0) {
            console.error('No carousel slides found!');
            return this._super(...arguments);
        }

        this._setupEventListeners();
        this._startAutoPlay();

        return this._super(...arguments);
    },

    _setupEventListeners() {
        // Previous button
        const prevBtn = this.el.querySelector('.ca-carousel-prev');
        if (prevBtn) {
            prevBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this._prev();
            });
        }

        // Next button
        const nextBtn = this.el.querySelector('.ca-carousel-next');
        if (nextBtn) {
            nextBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this._next();
            });
        }

        // Indicators
        this.indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', (e) => {
                e.preventDefault();
                this._goTo(index);
            });
        });

        // Pause on hover
        this.el.addEventListener('mouseenter', () => {
            this._stopAutoPlay();
        });

        this.el.addEventListener('mouseleave', () => {
            this._startAutoPlay();
        });

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') {
                this._prev();
            } else if (e.key === 'ArrowRight') {
                this._next();
            }
        });

        // Touch/swipe support
        let touchStartX = 0;
        let touchEndX = 0;

        this.el.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        });

        this.el.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            this._handleSwipe(touchStartX, touchEndX);
        });
    },

    _goTo(index) {
        // Remove active class from current slide
        this.slides[this.currentSlide].classList.remove('active');
        this.indicators[this.currentSlide].classList.remove('active');

        // Update current slide
        this.currentSlide = index;

        // Add active class to new slide
        this.slides[this.currentSlide].classList.add('active');
        this.indicators[this.currentSlide].classList.add('active');

        console.log('Moved to slide', index);

        // Reset auto-play
        this._resetAutoPlay();
    },

    _next() {
        const next = (this.currentSlide + 1) % this.slides.length;
        this._goTo(next);
    },

    _prev() {
        const prev = (this.currentSlide - 1 + this.slides.length) % this.slides.length;
        this._goTo(prev);
    },

    _startAutoPlay() {
        console.log('Auto-play started');
        this.autoPlayInterval = setInterval(() => {
            this._next();
        }, 5000);
    },

    _stopAutoPlay() {
        if (this.autoPlayInterval) {
            clearInterval(this.autoPlayInterval);
            console.log('Auto-play stopped');
        }
    },

    _resetAutoPlay() {
        this._stopAutoPlay();
        this._startAutoPlay();
    },

    _handleSwipe(startX, endX) {
        const swipeThreshold = 50;

        if (endX < startX - swipeThreshold) {
            // Swiped left - go to next
            this._next();
        } else if (endX > startX + swipeThreshold) {
            // Swiped right - go to previous
            this._prev();
        }
    },
});

export default publicWidget.registry.HeroCarousel;
