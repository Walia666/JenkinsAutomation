from django.conf.urls import url
from . import views

urlpatterns =[

        url(r'^$',views.jenkinsreport,name='jenkinsreport'),
	url(r'^download$',views.download,name='download'),
	url(r'^refresh/$',views.refresh,name='refresh')
	
	]
