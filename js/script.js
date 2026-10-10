/* =========================================================
   AI CAMPUS PLACEMENT PRO
   SECRET CIRCLE 🔴
   GLOBAL JAVASCRIPT
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    /* =========================
       MOBILE SIDEBAR
       ========================= */

    const menuButton = document.querySelector(".menu-button");
    const sidebar = document.querySelector(".sidebar");

    if (menuButton && sidebar) {

        menuButton.addEventListener("click", function () {

            sidebar.classList.toggle("mobile-open");

        });

    }


    /* =========================
       CLOSE SIDEBAR
       ========================= */

    const sidebarLinks = document.querySelectorAll(
        ".sidebar a"
    );

    sidebarLinks.forEach(function (link) {

        link.addEventListener("click", function () {

            if (window.innerWidth <= 900) {

                if (sidebar) {
                    sidebar.classList.remove("mobile-open");
                }

            }

        });

    });


    /* =========================
       ANIMATION ON SCROLL
       ========================= */

    const animatedElements =
        document.querySelectorAll(".animate");

    if ("IntersectionObserver" in window) {

        const observer =
            new IntersectionObserver(
                function (entries) {

                    entries.forEach(function (entry) {

                        if (entry.isIntersecting) {

                            entry.target.style.opacity = "1";

                            entry.target.style.transform =
                                "translateY(0)";

                            observer.unobserve(
                                entry.target
                            );

                        }

                    });

                },
                {
                    threshold: 0.12
                }
            );

        animatedElements.forEach(
            function (element) {

                observer.observe(element);

            }
        );

    }


    /* =========================
       CURRENT YEAR
       ========================= */

    const yearElement =
        document.querySelector("#current-year");

    if (yearElement) {

        yearElement.textContent =
            new Date().getFullYear();

    }


    /* =========================
       AUTO HIDE FLASH MESSAGE
       ========================= */

    const alerts =
        document.querySelectorAll(".alert");

    alerts.forEach(function (alert) {

        setTimeout(function () {

            alert.style.opacity = "0";

            alert.style.transform =
                "translateY(-10px)";

            setTimeout(function () {

                alert.remove();

            }, 300);

        }, 5000);

    });

});