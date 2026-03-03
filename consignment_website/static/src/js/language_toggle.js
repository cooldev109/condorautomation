// Language Toggle Script for Consignment Website
(function() {
    'use strict';

    console.log('[Language Toggle] Script loaded');

    function initLanguageDropdown() {
        console.log('[Language Toggle] Initializing...');

        // Get current language from URL or default to English
        const urlParams = new URLSearchParams(window.location.search);
        const currentLang = urlParams.get('lang') || 'en_US';
        console.log('[Language Toggle] Current language:', currentLang);

        // Language Dropdown Toggle
        const langDropdown = document.querySelector('.ca-lang-dropdown');
        const langToggleBtn = document.querySelector('.ca-lang-toggle-btn');
        const langCurrentText = document.querySelector('.ca-lang-current');
        const langOptions = document.querySelectorAll('.ca-lang-option');

        if (!langDropdown || !langToggleBtn) {
            console.error('[Language Toggle] Elements not found!');
            return;
        }

        console.log('[Language Toggle] Found elements:', {
            dropdown: !!langDropdown,
            button: !!langToggleBtn,
            currentText: !!langCurrentText,
            options: langOptions.length
        });

        // Set initial language text
        if (langCurrentText) {
            langCurrentText.textContent = currentLang === 'es_ES' ? 'Español' : 'English';
            console.log('[Language Toggle] Set language text to:', langCurrentText.textContent);
        }

        // Toggle dropdown on button click
        langToggleBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            langDropdown.classList.toggle('active');
            console.log('[Language Toggle] Dropdown toggled, active:', langDropdown.classList.contains('active'));
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!langDropdown.contains(e.target)) {
                langDropdown.classList.remove('active');
            }
        });

        // Highlight active language
        langOptions.forEach(function(option) {
            const optionLang = option.getAttribute('data-lang');
            if ((currentLang === 'en_US' && optionLang === 'en') ||
                (currentLang === 'es_ES' && optionLang === 'es')) {
                option.classList.add('active');
                console.log('[Language Toggle] Marked as active:', optionLang);
            }
        });

        // Handle language selection
        langOptions.forEach(function(option) {
            option.addEventListener('click', function(e) {
                e.preventDefault();
                const targetLang = this.getAttribute('data-lang');
                const langCode = targetLang === 'en' ? 'en_US' : 'es_ES';

                console.log('[Language Toggle] Switching to:', langCode);

                // Update URL with language parameter
                const currentUrl = new URL(window.location.href);
                currentUrl.searchParams.set('lang', langCode);
                window.location.href = currentUrl.toString();
            });
        });

        console.log('[Language Toggle] Initialization complete!');
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initLanguageDropdown);
    } else {
        // DOM is already ready
        initLanguageDropdown();
    }

})();
