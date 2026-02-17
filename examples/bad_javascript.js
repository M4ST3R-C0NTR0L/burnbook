// An intentionally terrible JavaScript file for testing BurnBook

// STYLE: Using var instead of const/let (JS002)
var x = 1;
var y = 2;
var z = 3;

// SECURITY: Using eval() (JS006)
function runUserCode(userInput) {
    eval(userInput);
}

// COMPLEXITY: Callback hell / Pyramid of Doom (JS001)
function fetchData(callback) {
    fetch('/api/data').then(function(response) {
        response.json().then(function(data) {
            processData(data, function(processed) {
                validateData(processed, function(valid) {
                    if (valid) {
                        saveData(valid, function(saved) {
                            callback(saved, function(final) {
                                console.log(final);
                            });
                        });
                    }
                });
            });
        });
    });
}

// STYLE: Loose equality (JS004)
function compare(a, b) {
    if (a == b) {
        return true;
    }
    if (a == null) {
        return false;
    }
    return a == String(b);
}

// STYLE: console.log in production (JS003)
function debugLog(message) {
    console.log("DEBUG: " + message);
    console.debug("Debug info:", message);
}

// STYLE: Excessive promise chaining (JS007)
fetch('/api')
    .then(r => r.json())
    .then(d => d.items)
    .then(items => items.map(i => i.id))
    .then(ids => ids.filter(id => id > 0))
    .then(validIds => validIds.map(id => fetch(`/api/item/${id}`)))
    .then(requests => Promise.all(requests))
    .then(responses => console.log(responses));

// TODO: Implement proper error handling
// FIXME: This breaks in IE11
// HACK: Tim's workaround, do not delete
