/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, { enumerable: true, get: getter });
/******/ 		}
/******/ 	};
/******/
/******/ 	// define __esModule on exports
/******/ 	__webpack_require__.r = function(exports) {
/******/ 		if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 			Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 		}
/******/ 		Object.defineProperty(exports, '__esModule', { value: true });
/******/ 	};
/******/
/******/ 	// create a fake namespace object
/******/ 	// mode & 1: value is a module id, require it
/******/ 	// mode & 2: merge all properties of value into the ns
/******/ 	// mode & 4: return value when already ns object
/******/ 	// mode & 8|1: behave like require
/******/ 	__webpack_require__.t = function(value, mode) {
/******/ 		if(mode & 1) value = __webpack_require__(value);
/******/ 		if(mode & 8) return value;
/******/ 		if((mode & 4) && typeof value === 'object' && value && value.__esModule) return value;
/******/ 		var ns = Object.create(null);
/******/ 		__webpack_require__.r(ns);
/******/ 		Object.defineProperty(ns, 'default', { enumerable: true, value: value });
/******/ 		if(mode & 2 && typeof value != 'string') for(var key in value) __webpack_require__.d(ns, key, function(key) { return value[key]; }.bind(null, key));
/******/ 		return ns;
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = 0);
/******/ })
/************************************************************************/
/******/ ({

/***/ "./bitcaster/bitcaster.js":
/*!********************************!*\
  !*** ./bitcaster/bitcaster.js ***!
  \********************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


window.bitcaster = __webpack_require__(/*! ./js/index */ "./bitcaster/js/index.js");


/***/ }),

/***/ "./bitcaster/js/index.js":
/*!*******************************!*\
  !*** ./bitcaster/js/index.js ***!
  \*******************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

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
_.passwords = __webpack_require__(/*! ./password.input.js */ "./bitcaster/js/password.input.js");
_.paginator = __webpack_require__(/*! ./paginator.js */ "./bitcaster/js/paginator.js");
module.exports = _;


/***/ }),

/***/ "./bitcaster/js/paginator.js":
/*!***********************************!*\
  !*** ./bitcaster/js/paginator.js ***!
  \***********************************/
/*! no static exports found */
/***/ (function(module, exports) {

var paginator = function (current_page, total_pages, filters) {
    console.log(current_page, total_pages);
    var skip_pages = 1; //change your number accordingly you want to show numbers

    var factor = Math.floor(current_page / skip_pages);

    $(".page_number").each(function (i, obj) {   //Showing the discrete numbers
        var page = factor * (skip_pages) + i + 1;
        if (current_page % skip_pages === 0) {
            page = (factor - 1) * skip_pages + i + 1;
        }
        if (page - 1 < total_pages) {
            $(this).html(page);
            $(this).attr("href", filters + "&page=" + page);
        } else {
            var x = i + 1;
            $('li[data-offset=' + x + ']').css("display", "none");
        }
    });
    var page = current_page % skip_pages;
    if (page === 0) {
        page = skip_pages;
    }
    $('li[data-offset=' + page + ']').each(function () {   //Deciding the active class
        $('li[data-offset=' + page + ']').addClass("active");
    });

    $(".skip_next").click(function () {   //Skip next ... Function
        if (current_page % skip_pages === 0) {
            factor = factor - 1;
        }
        var page = (factor + 1) * skip_pages + 1;
        if (page < total_pages) {
            $(this).attr("href", filters + "&page=" + page);
        }else {
            $(this).attr("href", filters + "&page=" + total_pages);
        }
    });
    $(".skip_prev").click(function () { //Skip Previous ... Function
        if (current_page % skip_pages === 0){
            factor = factor - 1;
        }
        var page = skip_pages * (factor - 1) + 1;
        if (page > 0) {
            $(this).attr("href", filters + "&page=" + page);
        }else {
            $(this).attr("href", filters + "&page=" + "1");
        }
    })
};

module.exports = paginator;


/***/ }),

/***/ "./bitcaster/js/password.input.js":
/*!****************************************!*\
  !*** ./bitcaster/js/password.input.js ***!
  \****************************************/
/*! no static exports found */
/***/ (function(module, exports) {

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


/***/ }),

/***/ 0:
/*!***********************************!*\
  !*** multi ./bitcaster/bitcaster ***!
  \***********************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

module.exports = __webpack_require__(/*! /data/PROGETTI/saxix/bitcaster/mercury/src/bitcaster/web/assets/bitcaster/bitcaster */"./bitcaster/bitcaster.js");


/***/ })

/******/ });
//# sourceMappingURL=bitcaster.js.map
