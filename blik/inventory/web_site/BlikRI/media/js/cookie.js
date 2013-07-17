function setCookie(name, value, expires, path, domain, secure) {
	if (!name || !value) return false;
	var str = name + '=' + encodeURIComponent(value);
	
	if (expires) str += '; expires=' + expires.toGMTString();
	if (path)    str += '; path=' + path;
	if (domain)  str += '; domain=' + domain;
	if (secure)  str += '; secure';
	
	document.cookie = str;
	return true;
}

function getCookie(name) {
	var pattern = "(?:; )?" + name + "=([^;]*);?";
	var regexp  = new RegExp(pattern);
	
	if (regexp.test(document.cookie))
	return decodeURIComponent(RegExp["$1"]);
	
	return false;
}

function deleteCookie(name, path, domain) {
	setCookie(name, null, new Date(0), path, domain);
	return true;
}