from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

urlpatterns = patterns('nr_contributions.views',
    (r'^$', 'contribution_list'),
    (r'^list/$', redirect_to, {'url': "/contribute"}),
    (r'^submit/$', 'submit'),
    (r'^submitjs/$', 'submitjs'),
    (r'^thanks/$', 'thanks'),
)
