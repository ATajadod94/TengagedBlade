(function (global) {

var dc = {};

var statshtml = "stats.html";
var statsid = "stats_content";
var py_gamescript = "./cgi-bin/gamestats.py";
var py_giftscript = "./cgi-bin/giftstats.py";
var py_blogscript = "./cgi-bin/blogstats.py";

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
$('button').bind("click",function() {
// On first load, show home view
var User = $('#inputbox input').val();
showLoading("#content");
$ajaxUtils.runPyScript(
  py_gamescript+'param1='+User,
  function() {
     $ajaxUtils.sendGetRequest(
        statshtml,
        function (responseText) {
          responseText =  insertProperty(responseText, "User_game", User);
          document.querySelector('#content')
              .id = 'stats_content'
              document.querySelector('#stats_content')
                .innerHTML = responseText;
        },
        false)},
     false)
$ajaxUtils.runPyScript(
  py_blogscript+'param1='+User,
  function() {
     $ajaxUtils.sendGetRequest(
        statshtml,
        function (responseText) {
          responseText =  insertProperty(responseText, "User_blog", User);
          document.querySelector('#content')
              .id = 'stats_content'
              document.querySelector('#stats_content')
                .innerHTML = responseText;
        },
        false)},
     false)

})


global.$dc = dc;

})(window);
