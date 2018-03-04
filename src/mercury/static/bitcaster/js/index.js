let _ = {};

_.toggleSidebar = function () {
    let that = $("#sidebar");
    that.style.flex = "auto";
    that.style["max-width"] = "none";
};

export default _;
