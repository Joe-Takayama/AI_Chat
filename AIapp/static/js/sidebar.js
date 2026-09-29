const menuButton = document.getElementById("menuButton");
const sidebar = document.getElementById("sidebar");
const sidebarClose = document.getElementById("sidebarClose");
const sidebarOverlay = document.getElementById("sidebarOverlay");


function openSidebar() {

    sidebar.classList.add("open");

    sidebarOverlay.classList.add("show");

    document.body.classList.add("sidebar-open");
}


function closeSidebar() {

    sidebar.classList.remove("open");

    sidebarOverlay.classList.remove("show");

    document.body.classList.remove("sidebar-open");
}


/* 三本線を押す */

menuButton.addEventListener(
    "click",
    openSidebar
);


/* ×を押す */

sidebarClose.addEventListener(
    "click",
    closeSidebar
);


/* サイドバーの外側を押す */

sidebarOverlay.addEventListener(
    "click",
    closeSidebar
);


/* Escキー */

document.addEventListener(
    "keydown",
    function (event) {

        if (event.key === "Escape") {

            closeSidebar();

        }

    }
);