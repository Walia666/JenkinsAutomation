from django.db import models
# Create your models here.
class Build_status_count(models.Model):

        Job_name=models.CharField(max_length=100)
	Time_from=models.DateTimeField(null=True, blank=True)
	Time_to=models.DateTimeField(null=True, blank=True)
        Successful=models.CharField(max_length=100,default=0)
        Failure=models.CharField(max_length=100,default=0)
        Unstable=models.CharField(max_length=100,default=0)
	Aborted=models.CharField(max_length=100,default=0)


class Download_csv_report(models.Model):
	Time_from=models.DateTimeField(null=True, blank=True)
	Time_to=models.DateTimeField(null=True, blank=True)

HOUR_CHOICES=(
    	('12', '12PM'),
    	('13', '1PM'),
    	('14', '2PM'),
    	('15', '3PM'),
	('16','4PM'),
	('17','5PM'),
	('18','6PM')
		)
STATUS=(
        ('active', 'active'),
        ('inactive', 'inactive'),
                )


class build_ite_issue(models.Model):
	hour = models.CharField(max_length=2,choices=HOUR_CHOICES)
	minute=models.CharField(max_length=100)
	status=models.CharField(max_length=10,choices=STATUS)

class build_ite_issue_counter(models.Model):
        hour = models.CharField(max_length=100)
        minute=models.CharField(max_length=100)

