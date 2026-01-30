document.addEventListener('DOMContentLoaded', () => {
    // 1. Highlight active sidebar link
    const currentPath = window.location.pathname;
    const sidebarLinks = document.querySelectorAll('.sidebar-nav a');

    sidebarLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // 2. Simple fade-in animation for main content
    const mainContent = document.querySelector('.col-sm-10');
    if (mainContent) {
        mainContent.style.opacity = 0;
        mainContent.style.transition = 'opacity 0.5s ease-in-out';
        requestAnimationFrame(() => {
            mainContent.style.opacity = 1;
        });
    }
});
