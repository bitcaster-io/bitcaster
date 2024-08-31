TOKEN1='[SERVER_ADDRESS]'
TOKEN2='https:\/\/SERVER_ADDRESS'
var regEx = new RegExp(TOKEN2, "ig");

const clickHandler = function () {
    let currentAddr = Cookies.get('address') || "https://127.0.0.1/";
    let addr = prompt("Set your bitcaster server address", currentAddr);
    Cookies.set('address', addr, currentAddr);
    location.reload();
};
const setAddress = function () {
    let cookieAddr = Cookies.get('address');
    if (!cookieAddr) {
        cookieAddr = TOKEN
    }
    for (const cell of document.getElementsByTagName('code')) {
        cell.innerHTML = cell.innerHTML.replace(TOKEN1, cookieAddr);
    }
    for (const cell of document.getElementsByTagName('a')) {
        cell.href = cell.href.replace(regEx, cookieAddr);
        cell.innerHTML = cell.innerHTML.replace(regEx, cookieAddr);
    }
};

addEventListener('load', function (e) {
    setAddress();
    let btn = document.getElementById("set-address");
    if (btn) {
        btn.addEventListener('click', clickHandler);
    }
});

document$.subscribe(function() {
    console.warn("Initialize third-party libraries here")
    setAddress();
})
