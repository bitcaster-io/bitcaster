let _ = {};


_.show = function (sender) {
    var $target = $($(sender).data("toggle"));
    $(sender).removeClass('fa-eye-slash').addClass('fa-eye');
    $target.attr('type', 'text');
};

_.hide = function (sender) {
    var $target = $($(sender).data("toggle"));
    $(sender).removeClass('fa-eye').addClass('fa-eye-slash');
    $target.attr('type', 'password');
};


module.exports = _;
