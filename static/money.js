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

function abort_dialog() {
    $('#mi-dialog').hide()
    shortcut.remove("Escape");
}

function dialog(url) {
    $('#mi-dialog').show()
    $('#mi-dialog').html('<h1>loading</h1>');
    jQuery.ajax({
        "url": url,
        "method": "GET",
        "format": "text",
        "success": function(data) {
            $('#mi-dialog').html(data);
            shortcut.add("Escape", function() {
                abort_dialog();
            }, {
                'type': 'keydown',
                'propagate': true,
                'target': document
            });
        },
        "error": function(status) {
            window.alert("Something when wrong. Error : " + status);
            $('#mi-dialog').hide()
        },
    })
}
