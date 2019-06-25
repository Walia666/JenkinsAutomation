from django.shortcuts import render,redirect
from django.http import HttpResponse
import jenkins
import datetime
import time
from .models import Build_status_count
import json
import csv

# Create your views here
def refresh(request):
        server = jenkins.Jenkins('http://180.179.184.230:8080',username='C2445',password='Shopclues@321')
        jobs = server.get_jobs()
        job_name_list=[]
        build_number_list=[]
        build_info_list=[]
        status_list_dict={}
        tme=time.time()
	time_now=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tme))	
        tmelastmonth=tme-2592000
	time_from=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tmelastmonth))
        tmemiliseconds=tmelastmonth*1000
        #print dir(server)
        for i in range(len(jobs)):
                job_name=jobs[i]['name']
                job_name_list.append(job_name)
        for i in range(len(job_name_list)):
                job_info=server.get_job_info(job_name_list[i])
                lastbuilt=job_info['lastSuccessfulBuild']
                if lastbuilt:
                        b_number=job_info['lastSuccessfulBuild']['number']
                        build_number_list.append(b_number)
                build_zipped=zip(job_name_list,build_number_list)
        for i ,j in build_zipped:
                success=0
                failure=0
                unstable=0
                aborted=0
                try:
			for k in range(j,1,-1):
                                build_info=server.get_build_info(i,k)
                                if build_info['timestamp']<tmemiliseconds:
                                        break
                                build_info_list.append(build_info)
                                status=build_info['result']
                                if status=="SUCCESS":
                                        success+=1
                                elif status=="FAILURE":
                                        failure+=1
                                elif status=="UNSTABLE":
                                        unstable+=1
                                else:
                                        aborted+=1
                                statuscount=[success,failure,unstable,aborted]
                                status_list_dict[i]=statuscount

                except:
                        pass
        	
	for job in status_list_dict:
		build_status_object = Build_status_count.objects.filter(Job_name=job)
		if not build_status_object:
			build_status_count = Build_status_count()
    			build_status_count.Job_name =job 
    			build_status_count.Time_from = time_from
			build_status_count.Time_to= time_now
			build_status_count.Successful=status_list_dict[job][0]
			build_status_count.Failure=status_list_dict[job][1]
			build_status_count.Unstable=status_list_dict[job][2]
			build_status_count.Aborted=status_list_dict[job][3]
    	       	 	build_status_count.save()
		else:
			for obj in build_status_object:
    				obj.Time_from = time_from
				obj.Time_to=time_now
				obj.Successful=status_list_dict[job][0]
                        	obj.Failure=status_list_dict[job][1]
                        	obj.Unstable=status_list_dict[job][2]
                        	obj.Aborted=status_list_dict[job][3]

    				obj.save()
      			
	return redirect('jenkinsreport')

def jenkinsreport(request):
	Build=Build_status_count.objects.all()
	status_list_dict={}
	testdict={}
	for build in Build:
		job_name=build.Job_name
		jb=job_name.encode("utf-8")
		success=build.Successful
		sc=success.encode("utf-8")
		scint=int(sc)
		failure=build.Failure
		Unstable=build.Unstable
		Aborted=build.Aborted
		status_list=[int(success),int(failure),int(Unstable),int(Aborted)]
		status_list_dict[jb]=scint 
		testdict[jb]=status_list
	          

	return render(request,'jenkinsapp/index.html',{'status_count_list': json.dumps(status_list_dict),'testdict': json.dumps(testdict)})

def download(request):
	server = jenkins.Jenkins('http://180.179.184.230:8080',username='C2445',password='Shopclues@321')
	if request.method == 'POST':
		datefrom=request.POST.get('datefrom','')
		dateto=request.POST.get('dateto','')
		dropdown=request.POST.get('dropdown','')
		if dropdown=="other":
			pattern = '%Y-%m-%dT%H:%M'
        		datefromsec = int(time.mktime(time.strptime(datefrom, pattern)))
			datetosec= int(time.mktime(time.strptime(dateto, pattern)))
			datefrommilisec=datefromsec*1000
			datetomilisec=datetosec*1000
        		jobs = server.get_jobs()
        		job_name_list=[]
        		build_number_list=[]
        		build_info_list=[]
       			status_list_dict={}
			for i in range(len(jobs)):
                		job_name=jobs[i]['name']
                		job_name_list.append(job_name)
        		for i in range(len(job_name_list)):
                		job_info=server.get_job_info(job_name_list[i])
                		lastbuilt=job_info['lastSuccessfulBuild']
                		if lastbuilt:
                        		b_number=job_info['lastSuccessfulBuild']['number']
                        		build_number_list.append(b_number)
                		build_zipped=zip(job_name_list,build_number_list)
			print build_zipped
        		for i ,j in build_zipped:
                		success=0
                		failure=0
                		unstable=0
                		aborted=0
				try:
                        		for k in range(j,1,-1):
                                		build_info=server.get_build_info(i,k)
                               			if build_info['timestamp']<datetomilisec and build_info['timestamp']>datefrommilisec:
                                			status=build_info['result']
                                			if status=="SUCCESS":
                                        			success+=1
                                			elif status=="FAILURE":
                                        			failure+=1
                                			elif status=="UNSTABLE":
                                        			unstable+=1
                                			else:
                                        			aborted+=1
					
							statuscount=[success,failure,unstable,aborted]
                                			status_list_dict[i]=statuscount
						elif  build_info['timestamp']<datefrommilisec:
							break


                                

        			except:
                       			pass	

			my_list = [[key, value[0],value[1],value[2],value[3]] for key, value in status_list_dict.items()]
			abc=[["Server","Successful","Failure","Aborted","Unstable"]]
			with open('build_info.csv', 'w') as myfile:
    				writer = csv.writer(myfile)
				writer.writerows(abc)
    				writer.writerows(my_list)
			with open('build_info.csv', 'rb') as myfile:
                                response = HttpResponse(myfile, content_type='text/csv')
                                response['Content-Disposition'] = 'attachment; filename=build_info.csv'
                                return  response


		else:
			timeframe={"1m":2592000,
				  "2m":5184000,
				  "3m":7776000
					}
			tme=time.time()
			timediff=timeframe[dropdown]
			tmefromintsec=tme-timediff
                	time_from=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tmefromintsec))
                	tmemiliseconds=tmefromintsec*1000
			time_to=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tme))
			server = jenkins.Jenkins('http://180.179.184.230:8080',username='C2445',password='Shopclues@321')
        		jobs = server.get_jobs()
        		job_name_list=[]
        		build_number_list=[]
        		build_info_list=[]
        		status_list_dict={}
			for i in range(len(jobs)):
                		job_name=jobs[i]['name']
                		job_name_list.append(job_name)
        		for i in range(len(job_name_list)):
                		job_info=server.get_job_info(job_name_list[i])
                		lastbuilt=job_info['lastSuccessfulBuild']
                		if lastbuilt:
                        		b_number=job_info['lastSuccessfulBuild']['number']
                        		build_number_list.append(b_number)
                		build_zipped=zip(job_name_list,build_number_list)
        		for i ,j in build_zipped:
                		success=0
                		failure=0
                		unstable=0
                		aborted=0
                		try:
                        		for k in range(j,1,-1):
                                		build_info=server.get_build_info(i,k)
                                		if build_info['timestamp']<tmemiliseconds:
                                        		break
                                		build_info_list.append(build_info)
                                		status=build_info['result']
                                		if status=="SUCCESS":
                                        		success+=1
                                		elif status=="FAILURE":
                                        		failure+=1
                                		elif status=="UNSTABLE":
                                        		unstable+=1
                                		else:
                                        		aborted+=1
                                		statuscount=[success,failure,unstable,aborted]
                                		status_list_dict[i]=statuscount

                		except:
                        		pass
			my_list = [[key, value[0],value[1],value[2],value[3]] for key, value in status_list_dict.items()]
			print my_list
                        abc=[["Server","Successful","Failure","Aborted","Unstable"]]
                        with open('build_info.csv', 'w') as myfile:
                                writer = csv.writer(myfile)
                                writer.writerows(abc)
                                writer.writerows(my_list)
                        with open('build_info.csv', 'rb') as myfile:
                                response = HttpResponse(myfile, content_type='text/csv')
                                response['Content-Disposition'] = 'attachment; filename=build_info.csv'
                                return  response



			
	
	return render(request,'jenkinsapp/index.html')
