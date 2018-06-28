(function (global) {

var dc = {};

var statshtml = "stats.html";
var base_python = "cgi-bin/basestats.py"
var game_python = "cgi-bin/gamestats.py"
var gift_python = "cgi-bin/giftstats.py"
var blog_python = "cgi-bin/blogstats.py"

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
$ajaxUtils.sendGetRequest(
  statshtml,
  function (responseText) {
    document.querySelector(".container .thanks").remove()
     document.querySelector(".container .replace").innerHTML = responseText;
  },
  false);
$ajaxUtils.sendGetRequest(
  base_python,
  function (responseText) {
    var all_badges = document.querySelectorAll(".container .replace li .badge");
        for( badge in all_badges, value in responseText) {
          all_badges[badge].innerHTML = value;
        }
  },
  false);
$ajaxUtils.sendGetRequest(
  game_python,
  function (responseText) {
      var media = document.querySelectorAll(".media-object");
      media[1].setAttribute('src', responseText);
  },
  false);
$ajaxUtils.sendGetRequest(
  gift_python,
  function (responseText) {
      var media = document.querySelectorAll(".media-object");
      media[2].setAttribute('src', responseText);  },
  false);
$ajaxUtils.sendGetRequest(
  blog_python,
  function (responseText) {
      var media = document.querySelectorAll(".media-object");
      media[3].setAttribute('src', responseText);  },
  false);
});


global.$dc = dc;

})(window);
