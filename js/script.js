(function (global) {

var dc = {};

var statshtml = "stats.html";
var statsid = "stats_content";
// Convenience function for inserting innerHTML for 'select'
var insertHtml = function (selector, html) {
  var targetElem = document.querySelector(selector);
  targetElem.innerHTML = html;
};

var insertCSS = function (selector, css) {
  var targetElem = document.querySelector(selector);
  targetElem.id = css;
};

// Show loading icon inside element identified by 'selector'.
var showLoading = function (selector) {
  var html = "<div class='text-center'>";
  html += "<img src='images/ajax-loader.gif'></div>";
  insertHtml(selector, html);
};

// On page load (before images or CSS)
$('button').bind("click",function(event) {
// On first load, show home view
showLoading("#content");
$ajaxUtils.sendGetRequest(
  statshtml,
  function (responseText) {
    document.querySelector('#content')
        .id = 'stats_content'
        document.querySelector('#stats_content')
          .innerHTML = responseText;
  },
  false);
});


global.$dc = dc;

})(window);
