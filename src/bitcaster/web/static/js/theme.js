
document.addEventListener("DOMContentLoaded", function () {
    const toggler = document.getElementById("theme-toggler");
    const HTML = document.getElementsByTagName('html')[0];
    const stored = localStorage.getItem("theme") || "dark"

    HTML.dataset.theme = stored;
    toggler.checked = (HTML.dataset.theme === "dark");
    HTML.dataset.theme = localStorage.theme || "dark";
    localStorage.setItem("theme", HTML.dataset.theme);
    toggler.addEventListener("click", () => {
        HTML.dataset.theme = toggler.checked ? "dark" : "light"
        localStorage.theme = HTML.dataset.theme;
    })
})
