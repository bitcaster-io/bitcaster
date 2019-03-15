// import "./jquery.formset.js";
// import "./password.input.js";

let _ = {};

_.toggleSidebar = function () {
    let that = $("#sidebar");
    that.style.flex = "auto";
    that.style["max-width"] = "none";
};
_.passwords = require("./password.input.js");
module.exports = _;
