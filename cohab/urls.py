from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cohab2.views.home', name='home'),
    # url(r'^cohab2/', include('cohab2.foo.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^login$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name="login"),
    url(r'^logout$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    url(r'^', include('hab.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
)
