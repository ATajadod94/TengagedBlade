(function (global) {

var dc = {};

var statshtml = "stats.html";
var statsid = "stats_content";
// Convenience function for inserting innerHTML for 'select'
var insertHtml = function (selector, html) {
  var targetElem = document.querySelector(selector);
  targetElem.innerHTML = html;
};



var insertProperty = function (string, propName, propValue) {
    var propToReplace = "{{" + propName + "}}";
        string = string
          .replace(new RegExp(propToReplace, "g"), propValue);
        return string;
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
var User = $('#inputbox input').val();
showLoading("#content");
$ajaxUtils.sendGetRequest(
  statshtml,
  function (responseText) {
    responseText =  insertProperty(responseText, "User", User);
    document.querySelector('#content')
        .id = 'stats_content'
        document.querySelector('#stats_content')
          .innerHTML = responseText;
  },
  false);
});


global.$dc = dc;

})(window);
