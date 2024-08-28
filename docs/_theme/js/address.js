const clickHandler = function(){
    let currentAddr = Cookies.get('address') || "https://127.0.0.1/";
    let addr = prompt("Set your bitcaster server address", currentAddr);
    Cookies.set('address', addr, currentAddr);
    location.reload();
};
const setAddress = function (){
    let cookieAddr = Cookies.get('address');
    if (!cookieAddr){
        cookieAddr = "[SERVER_ADDRESS]"
    }
    for (const cell of  document.getElementsByTagName('code')){
        cell.innerHTML = cell.innerHTML.replace('[SERVER_ADDRESS]', cookieAddr);
    }
};
addEventListener('load', function(e) {
    setAddress();
    let btn = document.getElementById("set-address");
    if (btn){
        btn.addEventListener('click', clickHandler);
    }
});
console.log(111111, window.$)
