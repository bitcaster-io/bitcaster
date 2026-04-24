window.initInstall = function(params) {
    if (typeof InstallModel !== 'undefined') {
        const pageModel = new InstallModel(params);
        ko.applyBindings(pageModel);
        pageModel.start();
    } else {
        console.error('InstallModel not defined. Make sure install.js is loaded.');
    }
};
