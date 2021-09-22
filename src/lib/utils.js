// This file should just contain general utility functions like:
// formatting string or numbers
// checkers


// String formatting via placeholders: has troubles with placeholders injections
// e.g. flecart: ho fatto una prova e sembra trasformare "test" in <b>"test"</b>
// Ma non so la logica con cui lo faccia....
// Non ho capito come funziona, ma funziona. :))))))
const formatter = function () {
    var s = arguments[0].slice();
    for (var i = 0; i < arguments.length - 1; ++i) {
        s = s.replace(new RegExp("\\{" + i + "\\}", "gm"), arguments[i + 1]);
    }
    return s;
}

// BUG: non funziona non so perché
const assert = (value, test, boolean=true) => {
    if ( (boolean && value !== test) || (!boolean && value === test) ) {
        console.log(`assert with ${value} and ${test} failed`)
        throw TypeError();
    }

    return;
}

module.exports = {
    formatter: formatter,
	assert: assert
}
