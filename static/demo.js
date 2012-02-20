/*
 * Utilities for the demo form on the front page.
 */

var USER_ID_BLURB = 'user id (optional)';
var ACCESS_TOKEN_RE = new RegExp('access_token=([^&]+)');
var OAUTH_INPUT_IDS = ['access_token', 'access_token_key', 'access_token_secret'];

function render_form() {
  // the user id field's style depends on whether it has a value, and whether it
  // has focus, and whether @all or @self is selected.
  var all_or_self = document.getElementById('all_or_self').value;
  var userid_elem = document.getElementById('userid');
  var userid = userid_elem.value;

  if (all_or_self == 'self') {
    userid_elem.disabled = 'disabled';
    userid_elem.style.display = 'none';
  } else {
    userid_elem.disabled = null;
    userid_elem.style.display = 'inline';
    if (userid == '' || userid == USER_ID_BLURB) {
      if (document.activeElement == userid_elem) {
        userid_elem.value = '';
        userid_elem.style.color = 'black';
      } else {
        userid_elem.value = USER_ID_BLURB;
        userid_elem.style.color = 'gray';
      }
    }
  }

  // the oauth access token field styles depend on whether they have values.
  var oauth_inputs = new Array();
  OAUTH_INPUT_IDS.map(function(id) {
    elem = document.getElementById(id);
    if (elem)
      oauth_inputs.push(elem);
  })

  oauth_inputs.map(function(input) {
    label = document.getElementById(input.id + '_label');
    label.style.color = (input.value) ? 'black' : 'gray';
  });

  // construct URL
  var url = '/poco/@me/@' + all_or_self + '/';
  if (userid_elem.disabled != 'disabled' && userid != USER_ID_BLURB)
    url += userid;

  url += '?'
  oauth_inputs.map(function(input) {
    if (input.value)
      url += input.name + '=' + input.value + '&';
  })

  document.getElementById('url').innerHTML = url;
  document.getElementById('demo').action = url;
}
                   

/* Only used for Facebook's client side OAuth flow, which returns the access
 * token in the URL fragment.
 */
function access_token_from_fragment() {
  var input = document.getElementById('access_token');
  var match = window.location.hash.match(ACCESS_TOKEN_RE);
  if (input && match)
    input.value = match[1];
}
