/**
 * TMS-fNIRS Educational Website - Main JavaScript
 * Enhances user experience with interactive features
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // ===== Back to top button functionality =====
    const backToTopButton = document.getElementById('back-to-top');
    
    // Show/hide back to top button based on scroll position
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopButton.classList.add('visible');
        } else {
            backToTopButton.classList.remove('visible');
        }
    });
    
    // Smooth scroll to top when button is clicked
    backToTopButton.addEventListener('click', function(e) {
        e.preventDefault();
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    // ===== Mobile navigation toggle =====
    const hamburgerMenu = document.querySelector('.hamburger-menu');
    const navMenu = document.getElementById('nav-menu');
    
    if (hamburgerMenu) {
        hamburgerMenu.addEventListener('click', function() {
            navMenu.classList.toggle('show');
            // Toggle aria-expanded attribute for accessibility
            const isExpanded = navMenu.classList.contains('show');
            hamburgerMenu.setAttribute('aria-expanded', isExpanded);
        });
    }
    
    // ===== Highlight active section in navigation =====
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('nav a');
    
    // Add active class to navigation links based on scroll position
    function highlightNavigation() {
        let scrollPosition = window.scrollY + 100; // Offset for fixed header
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            const sectionId = section.getAttribute('id');
            
            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${sectionId}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }
    
    window.addEventListener('scroll', highlightNavigation);
    
    // ===== Smooth scrolling for navigation links =====
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            if (this.getAttribute('href') !== '#') {
                e.preventDefault();
                
                // Close mobile menu if open
                if (navMenu && navMenu.classList.contains('show')) {
                    navMenu.classList.remove('show');
                    if (hamburgerMenu) {
                        hamburgerMenu.setAttribute('aria-expanded', 'false');
                    }
                }
                
                // Scroll to target
                const targetId = this.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                
                if (targetElement) {
                    const headerOffset = 70; // Adjust based on fixed header height
                    const elementPosition = targetElement.getBoundingClientRect().top;
                    const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                    
                    window.scrollTo({
                        top: offsetPosition,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
    
    // ===== Table of Contents toggle for mobile =====
    const tocHeading = document.querySelector('.toc h3');
    const tocList = document.querySelector('.toc ul');
    
    if (tocHeading && tocList) {
        // Add toggle functionality on mobile
        if (window.innerWidth < 768) {
            tocList.style.display = 'none';
            tocHeading.style.cursor = 'pointer';
            tocHeading.innerHTML += ' <span class="toggle-icon">+</span>';
            
            tocHeading.addEventListener('click', function() {
                if (tocList.style.display === 'none') {
                    tocList.style.display = 'block';
                    this.querySelector('.toggle-icon').textContent = '-';
                } else {
                    tocList.style.display = 'none';
                    this.querySelector('.toggle-icon').textContent = '+';
                }
            });
        }
    }
    
    // ===== Image zoom functionality =====
    const contentImages = document.querySelectorAll('.image-container img');
    
    contentImages.forEach(img => {
        img.addEventListener('click', function() {
            this.classList.toggle('zoomed');
        });
        
        // Add keyboard accessibility
        img.setAttribute('tabindex', '0');
        img.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.classList.toggle('zoomed');
            }
        });
    });
    
    // ===== Print button functionality =====
    const printButton = document.getElementById('print-page');
    
    if (printButton) {
        printButton.addEventListener('click', function(e) {
            e.preventDefault();
            window.print();
        });
    }
    
    // ===== Initialize on page load =====
    highlightNavigation(); // Set initial active state
    
    // ===== Handle window resize =====
    window.addEventListener('resize', function() {
        // Reset mobile menu on resize to desktop
        if (window.innerWidth > 768 && navMenu) {
            navMenu.classList.remove('show');
            if (hamburgerMenu) {
                hamburgerMenu.setAttribute('aria-expanded', 'false');
            }
        }
    });
});