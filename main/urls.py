from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.tenants, name="tenants"),
    url(r'^tenant-cashflows/(?P<tenant_id>\d+)/$',
        views.tenant_cashflows, name="tenant_cashflows"),
]
