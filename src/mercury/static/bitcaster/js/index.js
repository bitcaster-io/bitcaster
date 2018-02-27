/**
 *
 * User: sax
 * Date: 26/02/2018
 * Time: 11:36
 *
 */

let _ = {};

_.toggleSidebar = function () {
    let that = $("#sidebar");
    that.style.flex = "auto";
    that.style["max-width"] = "none";
};

export default _;
