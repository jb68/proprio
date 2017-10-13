from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from proprio import views
import re

admin.autodiscover()

media_regex = r'^%s(?P<path>.*)$' % re.escape(settings.MEDIA_URL.lstrip('/'))
urlpatterns = [
    url(r'^$', RedirectView.as_view(url='main/', permanent=True)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^main/', include('main.urls')),
    url(r'^import/', include('bank_import.urls')),
    url(r'^accounts/login/$', auth_views.login),
    url(r'^accounts/logout/$', lambda request: auth_views.logout(request, '/')),
    url(media_regex, views.serve_static, name='static files'),
]
