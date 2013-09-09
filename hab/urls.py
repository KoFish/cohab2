from django.conf.urls import patterns, url

from hab.views import *

urlpatterns = patterns('',
    url(r'^$', RootView.as_view(), name='root'),
    url(r'^templates/$', AssignmentTemplatesList.as_view(), name='templates-list'),
    url(r'^template/(?P<pk>\d+)/instanciate$', instanciate_template, name='instanciate-template'),
    url(r'^template/(?P<pk>\d+)/remove$', remove_template, name='remove-template'),
    url(r'^tasks/$', AssignmentsList.as_view(), name='assignments-list'),
    url(r'^tasks/(?P<slug>\S+)/$', AssignmentViewList.as_view(), name='assignment-view-list'),
    url(r'^tasks/(?P<slug>\S+)/add$', CreateViewAssignmentView.as_view(), name='assignment-view-add'),
    url(r'^task/(?P<pk>\d+)/complete$', complete_assignment, name='complete-assignment'),
    url(r'^task/(?P<pk>\d+)/clear$', clear_assignment, name='clear-assignment'),
    url(r'^task/(?P<pk>\d+)/assign$', assign_assignment, name='assign-assignment'),
    url(r'^task/(?P<pk>\d+)/suspend$', suspend_assignment, name='suspend-assignment'),
    url(r'^task/(?P<pk>\d+)/reopen$', reopen_assignment, name='reopen-assignment'),
    url(r'^get/template/(?P<pk>\d+)/$', TemplateDetails.as_view(), name='get-template'),
    url(r'^get/task/(?P<pk>\d+)/$', AssignmentDetails.as_view(), name='get-assignment'),
    url(r'^add/task/$', CreateAssignmentView.as_view(), name='add-assignment'),
    url(r'^get/(?P<key>\S+)/$', get, name='get'),
    url(r'^users/$', UserList.as_view(), name='users-list'),
)