// Masii — Shared Nav & Footer
// Single source of truth. Every page includes this instead of inline nav/footer.

(function () {
    // Detect subdirectory depth from root (website/)
    const path = window.location.pathname;
    const inBlog = path.includes('/blog/');
    const inArchive = path.includes('/archive/');
    const prefix = (inBlog || inArchive) ? '../' : '';

    // --- NAV ---
    const nav = document.getElementById('site-nav');
    if (nav) {
        nav.outerHTML = `
    <nav class="nav">
        <a href="${prefix}index.html" class="nav-logo">Masii 🪷</a>
        <button class="nav-toggle" aria-label="Menu"><span></span><span></span><span></span></button>
        <ul class="nav-links">
            <li><a href="${prefix}index.html#how">How it works</a></li>
            <li><a href="${prefix}know-your-masii.html">Meet Masii</a></li>
            <li><a href="${prefix}pricing.html">Pricing</a></li>
            <li><a href="${prefix}blog/">Blog</a></li>
            <li><a href="${prefix}one-cup.html" class="nav-cta">Talk to Masii</a></li>
        </ul>
    </nav>`;
    }

    // --- FOOTER ---
    const footer = document.getElementById('site-footer');
    if (footer) {
        footer.outerHTML = `
    <footer>
        <div class="container-wide">
            <div class="footer-content">
                <span>Masii &copy; 2026 🪷</span>
                <ul class="footer-links">
                    <li><a href="${prefix}know-your-masii.html">About</a></li>
                    <li><a href="${prefix}blog/">Blog</a></li>
                    <li><a href="#">Privacy</a></li>
                    <li><a href="#">Terms</a></li>
                </ul>
            </div>
        </div>
    </footer>`;
    }

    // --- MOBILE NAV TOGGLE ---
    const toggle = document.querySelector('.nav-toggle');
    const navLinks = document.querySelector('.nav-links');
    if (toggle && navLinks) {
        toggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            toggle.classList.toggle('active');
        });
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('active');
                toggle.classList.remove('active');
            });
        });
    }
})();
