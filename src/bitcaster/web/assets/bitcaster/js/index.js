// import "./jquery.formset.js";
// import "./password.input.js";

let _ = {};

_.toggleSidebar = function () {
    let that = $("#sidebar");
    that.toggleClass('active');
    Cookies.set('sidebar',
        that.hasClass('active') ? "active" : "",
        {path: '/'}
    );


};
_.passwords = require("./password.input.js");
_.paginator = require("./paginator.js");
module.exports = _;
