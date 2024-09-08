TOKEN1='[SERVER_ADDRESS]'
TOKEN2='https:\/\/SERVER_ADDRESS'
var regEx = new RegExp(TOKEN2, "ig");

const clickHandler = function () {
    let currentAddr = Cookies.get('address') || "";
    let addr = prompt("Set your bitcaster server address", currentAddr);
    if (addr != null && addr.startsWith('http') || addr === '') {
        addr = addr.replace(/\/+$/, "");
        Cookies.set('address', addr, currentAddr);
        location.reload();
    }
    if (addr === '') {
        clearHref()
        location.reload();
    }
};

const clearHref = function () {
    let cookieAddr = Cookies.get('address');
    if (!cookieAddr) {
        cookieAddr = TOKEN1;
    }
    for (const cell of document.getElementsByTagName('a')) {
        if (regEx.test(cell.href)){
            cell.href = "#";
            cell.removeAttribute('target');
        }
        cell.innerHTML = cell.innerHTML.replace(regEx, cookieAddr);
    }
};

const setAddress = function () {
    let cookieAddr = Cookies.get('address');
    if (!cookieAddr) {
        cookieAddr = TOKEN1;
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
    let cookieAddr = Cookies.get('address');
    if (cookieAddr) {
        setAddress();
    }else{
        clearHref();
    }
})
