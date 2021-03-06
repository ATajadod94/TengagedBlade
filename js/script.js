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
$('.visibility').css("visibility","visible");
try {
var User = '?param1=' + $(".form-control")[1].value.toLocaleUpperCase()
}
catch(err){
var User = '?param1=' + $(".form-control")[0].value.toLocaleUpperCase()
}
$ajaxUtils.sendGetRequest(
  statshtml,
  function (responseText) {
     document.querySelector(".thanks").remove()
     document.querySelector(".replace").innerHTML = responseText;
  },
  false);

var all_badges =  $('.badge');

$ajaxUtils.sendGetRequest(
  base_python + User,
  function (responseText) {
        responseText = responseText.split(" ");
        $(".media-object")[0].setAttribute('src', responseText[0]);
        $('.badge')[0].innerHTML = responseText[1];
        $(".badge")[1].innerHTML = responseText[2];
        $(".badge")[2].innerHTML = responseText[3];
  },
  false);
$ajaxUtils.sendGetRequest(
  game_python + User,
  function (responseText) {
      responseText = responseText.split(" ");
      $('.badge')[3].innerHTML = responseText[1];
      $(".media-object")[1].setAttribute('src', responseText[0]);
  },
  false);
$ajaxUtils.sendGetRequest(
  gift_python+ User,
  function (responseText) {
      responseText = responseText.split(" ");
      $('.badge')[4].innerHTML = responseText[1];
      $('.badge')[5].innerHTML = responseText[2];
      $(".media-object")[2].setAttribute('src', responseText[0]); },
  false)});

global.$dc = dc;

})(window);
