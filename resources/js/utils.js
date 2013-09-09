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
