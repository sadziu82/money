function go(url) {
    if (url.match(/^http:\/\//g)) {
        window.location.href = url;
    } else if (url.match(/^#/)) {
        window.location.href = window.location.href.replace(/#.*/, url);
    } else if (url.match(/^\//)) {
        window.location.pathname = url
    } else {
        window.alert('url "' + url + '" not suported!')
        return false;
    }
}

function dialog(url) {
    $('#dialog').html('<h1>loading</h1>');
    window.location.href = window.location.href + '#dialog';
    jQuery.ajax({
        "url": url,
        "method": "GET",
        "format": "text",
        "success": function(data) {
            $('#dialog').html(data);
            shortcut.add("Escape", function() {
                window.location.href = window.location.href.replace('#dialog', '#');
                shortcut.remove("Escape");
            }, {
                'type': 'keydown',
                'propagate': true,
                'target': document
            });
        },
        "error": function(status) {
            window.alert("Something when wrong. Error : " + status);
            window.location.href = window.location.href.replace('#dialog', '#');
        },
    })
}
