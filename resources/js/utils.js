function slugify(s) {
    //s = 'Was wäre daß® für ein + unnützer Tést?';
 
    var slug = s;

    slug = slug.toLowerCase();
    slug = slug.replace(/\s+/g,'-');
 
    tr = { 
        'ä':'a',
        'å':'a',
        'ö':'o',
        '/':'-'
    }
 
    for ( var key in tr )
    {
        slug = slug.replace(new RegExp(key, 'g'), tr[key]);
    }
 
    slug = slug.replace(/[^a-zA-Z0-9\-]/g,'');
    slug = slug.replace(/-+/g, '-');
 
    return slug;
}

(function(w) {
    var timeout_counter = 0,
        timeouts = {};
    w.smartTimeout = function(id, callback, timeout) {
        if (id in timeouts) {
            clearTimeout(timeouts[id]);
        }
        if (callback) {
            var to = setTimeout(function() {
                    delete timeouts[id];
                    return callback.call(this);
                }, timeout);
            timeouts[id] = to;
            return to;
        }
    }
})(window);

function query_get(key) {
    var re = RegExp('[\&?]' + key + '(?:\=([^\&]+)|\&|$)'),
        m = location.search.match(re);
    if (m) {
        return (m[1] ? unescape(m[1]) : true);
    } else {
        return false
    }
}

function query_replace(key, value) {
    var re = RegExp('([\&?])(' + key + ')=([^\&]+)'),
        org = location.search;
    if (org.search(re) >= 0) {
        return org.replace(re, (value ? ('$1$2=' + escape(value)) : '$1$2'));
    } else {
        return ((org.length > 0) ? org + '&' : '?') + key + (value ? ('=' + escape(value)) : '');
    }
}

function query_remove(key) {
    var re = RegExp('([\&]|^)(' + key + '=)([^\&]+)'),
        org = location.search.slice(1);
    return '?' + org.replace(re, '').replace(/^\&|\&^/, '');
}