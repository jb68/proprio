from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.forms),
    url(r'^generate-mapping$', views.generate),
    url(r'^submit-mapping$', views.submit),
]
