(function() {
    let deferredPrompt;
    let pwaOptions = {};

    function hideElement(id) {
        const el = document.getElementById(id);
        if (el) {
            console.log('[PWA] Hiding element:', id);
            el.style.setProperty('display', 'none', 'important');
            el.classList.add('hidden');
        }
    }

    function showElement(id) {
        const el = document.getElementById(id);
        if (el) {
            console.log('[PWA] Showing element:', id);
            el.style.setProperty('display', 'block', 'important');
            el.classList.remove('hidden');
            // Re-attach events when showing, to be absolutely sure
            attachEvents();
        }
    }

    function handleDismissInstall(e) {
        if (e) e.preventDefault();
        console.log('[PWA] Button clicked: Maybe later');
        try {
            localStorage.setItem('pwa_install_dismissed', 'true');
        } catch (err) {}
        hideElement('pwa-install-banner');
    }

    function handleDismissOpenApp(e) {
        if (e) e.preventDefault();
        console.log('[PWA] Button clicked: Stay here');
        try {
            localStorage.removeItem('pwa_is_installed');
        } catch (err) {}
        hideElement('pwa-open-app-banner');
    }

    function handleInstall(e) {
        if (e) e.preventDefault();
        console.log('[PWA] Button clicked: Install');
        if (!deferredPrompt) return;
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted' && pwaOptions.installedUrl) {
                window.location.href = pwaOptions.installedUrl;
            }
            deferredPrompt = null;
            hideElement('pwa-install-banner');
            hideElement('pwa-install-section');
        });
    }

    function handleOpenInApp(e) {
        if (e) e.preventDefault();
        const pwaUrl = pwaOptions.indexUrl || '/pwa/';
        window.open(pwaUrl, '_blank');
        setTimeout(() => { window.location.href = pwaUrl; }, 500);
    }

    function checkInstallBanner() {
        const isStandalone = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone;

        if (isStandalone) {
            try { localStorage.setItem('pwa_is_installed', 'true'); } catch (e) {}
            hideElement('pwa-install-section');
            return;
        }

        let isInstalled = false;
        try { isInstalled = localStorage.getItem('pwa_is_installed') === 'true'; } catch (e) {}

        if (isInstalled) {
            showElement('pwa-open-app-banner');
            hideElement('pwa-install-section');
        } else {
            const isiOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
            let hasDismissed = false;
            try { hasDismissed = localStorage.getItem('pwa_install_dismissed') === 'true'; } catch (e) {}

            // On Preferences page we show the install button even if dismissed before
            const isPrefsPage = window.location.pathname.includes('/prefs/');

            if (isiOS) {
                if (!isPrefsPage && hasDismissed) return;

                showElement('pwa-install-banner');
                showElement('pwa-install-section');

                const btnInstall = document.getElementById('pwa-btn-install');
                const btnInstallSection = document.getElementById('pwa-install-button');

                [btnInstall, btnInstallSection].forEach(btn => {
                    if (btn && pwaOptions.iosInstallText) {
                        btn.innerText = pwaOptions.iosInstallText;
                        btn.onclick = (e) => {
                            e.preventDefault();
                            alert(pwaOptions.iosAlertText);
                        };
                    }
                });
            } else if (deferredPrompt) {
                if (!isPrefsPage && hasDismissed) return;
                showElement('pwa-install-banner');
                showElement('pwa-install-section');
            } else {
                // If not iOS and no prompt, we can't install
                hideElement('pwa-install-section');
            }
        }
    }

    function attachEvents() {
        const btnDismissInstall = document.getElementById('pwa-btn-dismiss-install');
        const btnInstall = document.getElementById('pwa-btn-install');
        const btnDismissOpen = document.getElementById('pwa-btn-dismiss-open');
        const btnOpenApp = document.getElementById('pwa-btn-open-app');
        const btnInstallSection = document.getElementById('pwa-install-button');

        if (btnDismissInstall) btnDismissInstall.onclick = handleDismissInstall;
        if (btnInstall && !btnInstall.onclick) btnInstall.onclick = handleInstall;
        if (btnDismissOpen) btnDismissOpen.onclick = handleDismissOpenApp;
        if (btnOpenApp) btnOpenApp.onclick = handleOpenInApp;
        if (btnInstallSection && !btnInstallSection.onclick) btnInstallSection.onclick = handleInstall;
    }

    window.initPwaInstall = function(options) {
        console.log('[PWA] pwa_install.js loaded v4');
        pwaOptions = options;

        window.addEventListener('beforeinstallprompt', (e) => {
            console.log('[PWA] beforeinstallprompt event fired');
            try { localStorage.removeItem('pwa_is_installed'); } catch (err) {}
            e.preventDefault();
            deferredPrompt = e;
            checkInstallBanner();
        });

        window.addEventListener('appinstalled', () => {
            try { localStorage.setItem('pwa_is_installed', 'true'); } catch (err) {}
            hideElement('pwa-install-banner');
            hideElement('pwa-install-section');
        });

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', attachEvents);
        } else {
            attachEvents();
        }

        // Periodically check if prompt arrived (useful for settings page)
        let checks = 0;
        const checkInterval = setInterval(() => {
            checkInstallBanner();
            checks++;
            if (deferredPrompt || checks > 10) clearInterval(checkInterval);
        }, 1000);

        if (options.swUrl && 'serviceWorker' in navigator) {
            navigator.serviceWorker.register(options.swUrl, { scope: '/pwa/' })
                .then(reg => console.log('[PWA] SW Registered'))
                .catch(err => console.error('[PWA] SW Failed', err));
        }
    };
})();
