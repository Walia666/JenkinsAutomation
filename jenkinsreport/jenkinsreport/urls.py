from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [

    url(r'^admin/', include(admin.site.urls)),
    url(r'^',include('jenkinsapp.urls')),
    url(r'^accounts/', include('django.contrib.auth.urls')),

]

