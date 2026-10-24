function isSet(val) {
	return typeof val !== 'undefined';
}

function isObject(val) {
	return typeof val === 'object';
}

function isFunction(val) {
	return typeof val === 'function';
}

function isError(val) {
	return isObject(val) && val instanceof Error;
}

function getClass(obj) {
	if (typeof obj !== 'object' || obj === null) {
		return null;
	}
	var res = obj.constructor.toString().match(/function\s+([^(]+)/);
	return res.length ? res[1].toLowerCase() : null;
}

function log() {

	var val, message = '';

	if (arguments.length === 1) {
		val = arguments[0];
	} else if (arguments.length === 2) {
		message = arguments[0];
		val = arguments[1];
	} else {
		console.error('Wrong arguments number');
		return;
	}

	//noinspection JSUnresolvedVariable
	if (typeof logEnable === 'undefined' || !logEnable) {
		return;
	}

	if (message) {
		console.log(message, val);
	} else {
		console.log(val);
	}
}