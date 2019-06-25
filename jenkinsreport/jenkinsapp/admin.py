from .models import  Build_status_count,Download_csv_report
from django.contrib import admin
from django.contrib.sessions.models import Session



class StoreAdmin(admin.ModelAdmin):

      list_display = ('Job_name','Time_from','Time_to','Successful','Failure','Unstable','Aborted')
      search_fields=('Job_name',)
      list_filter = ('Job_name',)

admin.site.register(Build_status_count, StoreAdmin)

class DownloadCSVAdmin(admin.ModelAdmin):
	list_display=['Time_from','Time_to']
admin.site.register(Download_csv_report,DownloadCSVAdmin)


      

