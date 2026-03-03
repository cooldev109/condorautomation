// Translation System for Consignment Website
(function() {
    'use strict';

    console.log('[Translations] Script loaded');

    // Translation dictionary
    const translations = {
        // Navigation
        'Home': 'Inicio',
        'Why Choose Us': 'Por Qué Elegirnos',
        'Services': 'Servicios',
        'About Us': 'Acerca de Nosotros',
        'Contact': 'Contacto',
        "IT'S URGENT": 'ES URGENTE',

        // Homepage Hero
        'When your machine stops, we move fast.': 'Cuando su máquina se detiene, nos movemos rápido.',
        'Industrial machinery consignment. Connecting buyers with equipment owners through transparent, reliable service.': 'Consignación de maquinaria industrial. Conectando compradores con propietarios de equipos a través de un servicio transparente y confiable.',
        'How It Works': 'Cómo Funciona',

        // Homepage - Services Overview
        'Complete consignment management': 'Gestión completa de consignación',
        'For Sellers': 'Para Vendedores',
        'Consign your industrial equipment. Zero upfront cost. Track everything in real-time through your personal portal.': 'Consigne su equipo industrial. Cero costo inicial. Rastree todo en tiempo real a través de su portal personal.',
        'For Buyers': 'Para Compradores',
        'Access verified industrial machinery. Transparent pricing. Complete equipment history. Fast delivery coordination.': 'Acceso a maquinaria industrial verificada. Precios transparentes. Historial completo del equipo. Coordinación rápida de entrega.',
        'Full Service': 'Servicio Completo',
        'We handle photography, inspection, listing, sales, and payments. 12-month warranty on all services.': 'Manejamos fotografía, inspección, listado, ventas y pagos. Garantía de 12 meses en todos los servicios.',

        // Homepage - How It Works
        'How Our Consignment Process Works': 'Cómo Funciona Nuestro Proceso de Consignación',
        "From listing to payment, we handle everything. Here's your industrial equipment journey from start to finish.": 'Desde el listado hasta el pago, manejamos todo. Este es el recorrido de su equipo industrial de principio a fin.',
        'Inspection & Photography': 'Inspección y Fotografía',
        'We inspect, photograph, and create detailed technical reports.': 'Inspeccionamos, fotografiamos y creamos informes técnicos detallados.',
        'Professional Listing': 'Listado Profesional',
        'Your equipment gets listed with transparent pricing across multiple channels.': 'Su equipo se lista con precios transparentes en múltiples canales.',
        'Sale & Logistics': 'Venta y Logística',
        'We handle negotiations, secure payments, and coordinate shipping logistics.': 'Manejamos negociaciones, pagos seguros y coordinamos la logística de envío.',
        'Payment & Tracking': 'Pago y Seguimiento',
        'Track sales through your portal with automated payments and warranty coverage.': 'Rastree las ventas a través de su portal con pagos automatizados y cobertura de garantía.',
        'Start Your Consignment': 'Iniciar Su Consignación',
        'Questions?': '¿Preguntas?',
        'Contact our team': 'Contacte a nuestro equipo',
        'for a free consultation': 'para una consulta gratuita',

        // Homepage - Trust Section
        'Built for reliability': 'Construido para la confiabilidad',
        '12-month warranty': 'Garantía de 12 meses',
        'Real-time tracking portal': 'Portal de seguimiento en tiempo real',
        'Automated payment processing': 'Procesamiento automatizado de pagos',
        'Verified equipment inspection': 'Inspección de equipo verificada',

        // Homepage - Urgent CTA
        "Production can't wait.": 'La producción no puede esperar.',

        // General Homepage
        'Industrial Machinery Consignment': 'Consignación de Maquinaria Industrial',
        'Made Simple': 'Simplificada',
        'Sell your equipment with confidence. Professional consignment services for industrial machinery owners worldwide.': 'Venda su equipo con confianza. Servicios profesionales de consignación para propietarios de maquinaria industrial en todo el mundo.',
        'Get Free Appraisal': 'Obtener Evaluación Gratuita',
        'Learn More': 'Saber Más',
        'How It Works': 'Cómo Funciona',
        'Simple, transparent process from listing to sale': 'Proceso simple y transparente desde el listado hasta la venta',
        'Submit Your Equipment': 'Envíe Su Equipo',
        'Register your equipment online or contact us for a free consultation.': 'Registre su equipo en línea o contáctenos para una consulta gratuita.',
        'Professional Appraisal': 'Evaluación Profesional',
        'Our experts evaluate and price your machinery based on current market conditions.': 'Nuestros expertos evalúan y fijan el precio de su maquinaria según las condiciones actuales del mercado.',
        'Marketing & Listing': 'Marketing y Listado',
        'Professional photography and worldwide promotion to qualified buyers.': 'Fotografía profesional y promoción mundial a compradores calificados.',
        'Buyer Verification': 'Verificación del Comprador',
        'We screen and verify all potential buyers to ensure legitimate transactions.': 'Verificamos todos los compradores potenciales para garantizar transacciones legítimas.',
        'Sale Completion': 'Finalización de la Venta',
        'Secure payment processing and logistics coordination for seamless delivery.': 'Procesamiento seguro de pagos y coordinación logística para una entrega sin problemas.',
        'Why Choose CondorAutomation': 'Por Qué Elegir CondorAutomation',
        'Industry Expertise': 'Experiencia en la Industria',
        '15+ years specializing in industrial machinery consignment': '15+ años especializados en consignación de maquinaria industrial',
        'Global Reach': 'Alcance Global',
        'Extensive buyer network across 50+ countries': 'Amplia red de compradores en más de 50 países',
        'Transparent Pricing': 'Precios Transparentes',
        'Clear commission structure with no hidden fees': 'Estructura de comisiones clara sin tarifas ocultas',
        'Ready to Sell Your Equipment?': '¿Listo para Vender Su Equipo?',
        'Get started today with a free, no-obligation appraisal of your industrial machinery.': 'Comience hoy con una evaluación gratuita y sin compromiso de su maquinaria industrial.',
        'Contact Us Today': 'Contáctenos Hoy',
        'View Our Services': 'Ver Nuestros Servicios',

        // Why Choose Us page
        'The trusted partner for industrial machinery consignment': 'El socio de confianza para la consignación de maquinaria industrial',
        'What Sets Us Apart': 'Lo Que Nos Diferencia',
        'Experience the difference with our professional consignment services': 'Experimente la diferencia con nuestros servicios profesionales de consignación',
        'Decades of experience in industrial machinery with deep market knowledge and technical understanding.': 'Décadas de experiencia en maquinaria industrial con profundo conocimiento del mercado y comprensión técnica.',
        'Complete Transparency': 'Transparencia Completa',
        'Clear pricing structure with no hidden fees, straightforward terms, and honest appraisals.': 'Estructura de precios clara sin tarifas ocultas, términos directos y evaluaciones honestas.',
        'Global Network': 'Red Global',
        'Access to worldwide buyers through our extensive industry connections and marketing channels.': 'Acceso a compradores mundiales a través de nuestras amplias conexiones industriales y canales de marketing.',
        'Fast Turnaround': 'Retorno Rápido',
        'Efficient processes and active buyer network ensure quick sales and faster returns on your assets.': 'Procesos eficientes y red activa de compradores garantizan ventas rápidas y retornos más rápidos de sus activos.',
        'Dedicated Support': 'Soporte Dedicado',
        'Expert team providing personalized service from initial appraisal through final sale completion.': 'Equipo experto que brinda servicio personalizado desde la evaluación inicial hasta la finalización de la venta.',
        'Secure Transactions': 'Transacciones Seguras',
        'Protected payments, verified buyers, and comprehensive insurance options for peace of mind.': 'Pagos protegidos, compradores verificados y opciones de seguro integral para su tranquilidad.',
        'Years Experience': 'Años de Experiencia',
        'Machines Sold': 'Máquinas Vendidas',
        'Client Satisfaction': 'Satisfacción del Cliente',
        'Countries Reached': 'Países Alcanzados',
        'Ready to Get Started?': '¿Listo para Comenzar?',
        'Join hundreds of satisfied equipment owners who trust us with their machinery consignment.': 'Únase a cientos de propietarios satisfechos que confían en nosotros para la consignación de su maquinaria.',

        // Services page
        'Our Services': 'Nuestros Servicios',
        'Comprehensive consignment solutions for industrial machinery': 'Soluciones integrales de consignación para maquinaria industrial',
        'At CondorAutomation, we provide end-to-end consignment services designed to maximize the value of your industrial machinery. Our expert team handles every aspect of the sales process, allowing you to focus on your core business while we find the right buyers for your equipment.': 'En CondorAutomation, brindamos servicios de consignación completos diseñados para maximizar el valor de su maquinaria industrial. Nuestro equipo experto maneja cada aspecto del proceso de ventas, permitiéndole concentrarse en su negocio principal mientras encontramos los compradores adecuados para su equipo.',
        'Equipment Appraisal': 'Evaluación de Equipos',
        'Professional valuation of your industrial machinery based on current market conditions, equipment specifications, and condition assessment.': 'Valoración profesional de su maquinaria industrial basada en las condiciones actuales del mercado, especificaciones del equipo y evaluación del estado.',
        'Market-based pricing analysis': 'Análisis de precios basado en el mercado',
        'Comprehensive condition reports': 'Informes de estado completos',
        'Competitive positioning strategy': 'Estrategia de posicionamiento competitivo',
        'Listing & Marketing': 'Listado y Marketing',
        'Professional photography, detailed technical specifications, and multi-channel marketing to reach qualified buyers worldwide.': 'Fotografía profesional, especificaciones técnicas detalladas y marketing multicanal para llegar a compradores calificados en todo el mundo.',
        'High-quality equipment photography': 'Fotografía de equipos de alta calidad',
        'Technical documentation preparation': 'Preparación de documentación técnica',
        'Multi-platform promotion': 'Promoción multiplataforma',
        'Buyer Verification': 'Verificación del Comprador',
        'Thorough screening and qualification of potential buyers to ensure secure, legitimate transactions with serious purchasers.': 'Evaluación y calificación exhaustiva de compradores potenciales para garantizar transacciones seguras y legítimas con compradores serios.',
        'Financial capability assessment': 'Evaluación de capacidad financiera',
        'Business background verification': 'Verificación de antecedentes comerciales',
        'Reference checking': 'Verificación de referencias',
        'Negotiation Support': 'Apoyo en Negociación',
        'Expert negotiators handle all buyer communications and price discussions to secure the best possible terms for your equipment.': 'Negociadores expertos manejan todas las comunicaciones con compradores y discusiones de precios para asegurar los mejores términos posibles para su equipo.',
        'Professional price negotiations': 'Negociaciones de precios profesionales',
        'Terms and conditions management': 'Gestión de términos y condiciones',
        'Multiple offer coordination': 'Coordinación de ofertas múltiples',
        'Transaction Management': 'Gestión de Transacciones',
        'Secure payment processing, legal documentation, and escrow services to protect both parties throughout the transaction.': 'Procesamiento seguro de pagos, documentación legal y servicios de custodia para proteger a ambas partes durante la transacción.',
        'Secure payment processing': 'Procesamiento seguro de pagos',
        'Legal documentation handling': 'Manejo de documentación legal',
        'Escrow and fund management': 'Gestión de custodia y fondos',
        'Logistics Coordination': 'Coordinación Logística',
        'Complete shipping and transportation arrangements, including specialized heavy equipment logistics and international delivery.': 'Arreglos completos de envío y transporte, incluyendo logística especializada de equipos pesados y entrega internacional.',
        'Heavy equipment transportation': 'Transporte de equipos pesados',
        'International shipping coordination': 'Coordinación de envíos internacionales',
        'Insurance and tracking services': 'Servicios de seguros y rastreo',
        'Our Service Process': 'Nuestro Proceso de Servicio',
        'A streamlined approach to selling your industrial machinery': 'Un enfoque optimizado para vender su maquinaria industrial',
        'Initial Consultation': 'Consulta Inicial',
        'We discuss your equipment, timeline, and expectations to create a customized sales strategy.': 'Discutimos su equipo, cronograma y expectativas para crear una estrategia de ventas personalizada.',
        'Professional Appraisal': 'Evaluación Profesional',
        'Our experts evaluate your machinery and determine optimal pricing based on market analysis.': 'Nuestros expertos evalúan su maquinaria y determinan el precio óptimo basado en análisis de mercado.',
        'Marketing Launch': 'Lanzamiento de Marketing',
        'We create professional listings and promote your equipment across multiple channels.': 'Creamos listados profesionales y promocionamos su equipo en múltiples canales.',
        'Sale Completion': 'Finalización de la Venta',
        'Handle negotiations, finalize transaction, and coordinate delivery to the buyer.': 'Manejamos negociaciones, finalizamos la transacción y coordinamos la entrega al comprador.',
        'Let our expert team handle the entire consignment process for you. Get started with a free consultation today.': 'Permita que nuestro equipo experto maneje todo el proceso de consignación por usted. Comience con una consulta gratuita hoy.',
        'Get Free Consultation': 'Obtener Consulta Gratuita',
        'Learn About Us': 'Conocer Sobre Nosotros',

        // About page
        'About CondorAutomation': 'Acerca de CondorAutomation',
        'Your trusted partner in industrial machinery consignment since 2010': 'Su socio de confianza en consignación de maquinaria industrial desde 2010',
        'Our Story': 'Nuestra Historia',
        'Founded in 2010, CondorAutomation emerged from a simple observation: the industrial machinery market lacked a trustworthy, transparent consignment partner that truly understood both equipment owners and buyers.': 'Fundada en 2010, CondorAutomation surgió de una observación simple: el mercado de maquinaria industrial carecía de un socio de consignación confiable y transparente que realmente entendiera tanto a los propietarios de equipos como a los compradores.',
        "Over the past 15+ years, we've grown from a small regional operation to a globally recognized platform, facilitating thousands of successful machinery transactions across 50+ countries. Our success is built on unwavering commitment to transparency, expertise, and client satisfaction.": 'En los últimos 15+ años, hemos crecido de una pequeña operación regional a una plataforma reconocida globalmente, facilitando miles de transacciones exitosas de maquinaria en más de 50 países. Nuestro éxito se basa en un compromiso inquebrantable con la transparencia, la experiencia y la satisfacción del cliente.',
        'Today, we serve manufacturers, fabricators, and industrial facilities worldwide, helping them maximize the value of their equipment while connecting buyers with the machinery they need to grow their businesses.': 'Hoy, servimos a fabricantes, talleres y instalaciones industriales en todo el mundo, ayudándoles a maximizar el valor de sus equipos mientras conectamos compradores con la maquinaria que necesitan para hacer crecer sus negocios.',
        'Our Mission': 'Nuestra Misión',
        'To provide transparent, professional consignment services that maximize value for equipment owners while connecting qualified buyers with the industrial machinery they need.': 'Proporcionar servicios de consignación transparentes y profesionales que maximicen el valor para los propietarios de equipos mientras conectamos compradores calificados con la maquinaria industrial que necesitan.',
        'Our Vision': 'Nuestra Visión',
        "To become the world's most trusted industrial machinery consignment platform, recognized for integrity, expertise, and exceptional client service.": 'Convertirnos en la plataforma de consignación de maquinaria industrial más confiable del mundo, reconocida por su integridad, experiencia y servicio excepcional al cliente.',
        'Our Core Values': 'Nuestros Valores Fundamentales',
        'The principles that guide everything we do': 'Los principios que guían todo lo que hacemos',
        'Integrity': 'Integridad',
        'We operate with complete honesty and transparency in every transaction.': 'Operamos con total honestidad y transparencia en cada transacción.',
        'Expertise': 'Experiencia',
        'Deep industry knowledge and technical understanding drive our success.': 'El profundo conocimiento de la industria y la comprensión técnica impulsan nuestro éxito.',
        'Client Focus': 'Enfoque en el Cliente',
        'Your success is our priority. We tailor our services to your unique needs.': 'Su éxito es nuestra prioridad. Adaptamos nuestros servicios a sus necesidades únicas.',
        'Innovation': 'Innovación',
        'We continuously improve our processes and technology to serve you better.': 'Mejoramos continuamente nuestros procesos y tecnología para servirle mejor.',
        'Reliability': 'Confiabilidad',
        'We deliver on our commitments with consistent, dependable service.': 'Cumplimos nuestros compromisos con un servicio consistente y confiable.',
        'Partnership': 'Asociación',
        'We build long-term relationships based on mutual trust and success.': 'Construimos relaciones a largo plazo basadas en confianza mutua y éxito.',
        "Why We're Different": 'Por Qué Somos Diferentes',
        'Industry Specialization': 'Especialización en la Industria',
        'We focus exclusively on industrial machinery, bringing unmatched expertise to every transaction.': 'Nos enfocamos exclusivamente en maquinaria industrial, aportando experiencia incomparable a cada transacción.',
        'No Hidden Fees': 'Sin Tarifas Ocultas',
        'Transparent pricing with straightforward commission structure and no surprise charges.': 'Precios transparentes con estructura de comisiones directa y sin cargos sorpresa.',
        'Extensive buyer network spanning 50+ countries for maximum market exposure.': 'Amplia red de compradores que abarca más de 50 países para máxima exposición en el mercado.',
        'Personal account manager guiding you through every step of the process.': 'Gerente de cuenta personal que lo guía a través de cada paso del proceso.',
        'By the Numbers': 'En Números',
        'Years of Excellence': 'Años de Excelencia',
        'Successful Sales': 'Ventas Exitosas',
        'Countries Served': 'Países Atendidos',
        "Let's Work Together": 'Trabajemos Juntos',
        'Ready to experience the CondorAutomation difference? Contact us today to discuss your equipment consignment needs.': '¿Listo para experimentar la diferencia de CondorAutomation? Contáctenos hoy para discutir sus necesidades de consignación de equipos.',
        'Contact Us': 'Contáctenos',

        // Contact page
        'Get in touch with our team - we\'re here to help': 'Póngase en contacto con nuestro equipo - estamos aquí para ayudar',
        'Send Us a Message': 'Envíenos un Mensaje',
        'Fill out the form below and we\'ll get back to you within 24 hours.': 'Complete el formulario a continuación y nos comunicaremos con usted en 24 horas.',
        'Full Name *': 'Nombre Completo *',
        'Email Address *': 'Correo Electrónico *',
        'Phone Number': 'Número de Teléfono',
        'Message *': 'Mensaje *',
        'Send Message': 'Enviar Mensaje',
        'Contact Information': 'Información de Contacto',
        'We\'re available 24/7 to assist with your equipment needs.': 'Estamos disponibles 24/7 para ayudar con sus necesidades de equipos.',
        'Email': 'Correo Electrónico',
        'Phone': 'Teléfono',
        'Mon-Fri, 8am-6pm EST': 'Lun-Vie, 8am-6pm EST',
        'Office': 'Oficina',
        'Business Hours': 'Horario Comercial',
        '24/7 Support Available': 'Soporte 24/7 Disponible',
        'Emergency assistance anytime': 'Asistencia de emergencia en cualquier momento',
        'Quick Links': 'Enlaces Rápidos',
        'Our Services': 'Nuestros Servicios',
        'About CondorAutomation': 'Acerca de CondorAutomation',

        // Footer
        'Industrial machinery consignment platform.': 'Plataforma de consignación de maquinaria industrial.',
        'Connecting buyers with equipment owners through transparent, reliable service.': 'Conectando compradores con propietarios de equipos a través de un servicio transparente y confiable.',
        'Company': 'Compañía',
        'Support available 24/7': 'Soporte disponible 24/7'
    };

    function normalizeText(text) {
        // Normalize whitespace and apostrophes
        return text
            .trim()
            .replace(/\s+/g, ' ')  // Replace multiple spaces with single space
            .replace(/['']/g, "'"); // Normalize apostrophes
    }

    function translatePage(targetLang) {
        if (targetLang === 'en_US') {
            // Reload page without translations
            return;
        }

        console.log('[Translations] Translating to Spanish...');

        // Create normalized translation map
        const normalizedTranslations = {};
        Object.keys(translations).forEach(function(key) {
            normalizedTranslations[normalizeText(key)] = translations[key];
        });

        // Walk through all text nodes and translate
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            {
                acceptNode: function(node) {
                    // Skip script and style tags
                    if (node.parentElement.tagName === 'SCRIPT' ||
                        node.parentElement.tagName === 'STYLE') {
                        return NodeFilter.FILTER_REJECT;
                    }
                    // Only translate non-empty text
                    if (node.textContent.trim().length > 0) {
                        return NodeFilter.FILTER_ACCEPT;
                    }
                    return NodeFilter.FILTER_REJECT;
                }
            }
        );

        const nodesToTranslate = [];
        let node;
        while (node = walker.nextNode()) {
            nodesToTranslate.push(node);
        }

        let translatedCount = 0;
        // Translate each text node
        nodesToTranslate.forEach(function(textNode) {
            const originalText = textNode.textContent.trim();
            const normalizedText = normalizeText(originalText);

            if (normalizedTranslations[normalizedText]) {
                textNode.textContent = textNode.textContent.replace(
                    originalText,
                    normalizedTranslations[normalizedText]
                );
                console.log('[Translations] ✓', originalText.substring(0, 50) + '...');
                translatedCount++;
            }
        });

        // Translate placeholders
        document.querySelectorAll('[placeholder]').forEach(function(element) {
            const placeholder = element.getAttribute('placeholder');
            if (translations[placeholder]) {
                element.setAttribute('placeholder', translations[placeholder]);
                translatedCount++;
            }
        });

        console.log('[Translations] Translation complete! Translated', translatedCount, 'items.');
    }

    function initTranslations() {
        console.log('[Translations] Initializing...');

        // Get current language from URL
        const urlParams = new URLSearchParams(window.location.search);
        const currentLang = urlParams.get('lang') || 'en_US';

        console.log('[Translations] Current language:', currentLang);

        if (currentLang === 'es_ES') {
            translatePage(currentLang);
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTranslations);
    } else {
        initTranslations();
    }

})();
