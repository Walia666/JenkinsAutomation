from celery import Celery
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery import shared_task
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from datetime import timedelta
from celery.utils.log import get_task_logger
import jenkins
import jira
from jira import JIRA
from .models import Build_status_count,build_ite_issue
from itertools import groupby
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart 
logger = get_task_logger(__name__)

username="C2445"
password="Shopclues@321"
server = jenkins.Jenkins('http://180.179.184.230:8080',username=username,password=password)
jobs = server.get_jobs()
job_name="Build_JIRA"
jira = JIRA(basic_auth=(username, password), options={'server':'http://jira.shopclues.com/'})


@shared_task
def getissueinfo():
         projects = jira.projects()
         issue_dict={}
         issuelist=[]
         for i in range(len(projects)):
                issues_in_proj = jira.search_issues('project='+str(projects[i]))
                for issue in issues_in_proj:
                        issueobj=jira.issue(issue)
                        svn_branch=issueobj.raw['fields']['customfield_10306']
                        if str(issueobj.fields.status)=="Approved for ITE":
                                ft=issueobj.raw['fields']['customfield_10503']
                                rt=release_type=issueobj.raw['fields']['customfield_11100']
                                if ft is not None and rt is not None and svn_branch is not None:
                                        feature_type=issueobj.raw['fields']['customfield_10503']['value']
                                        release_type=issueobj.raw['fields']['customfield_11100']['value']
                                        if release_type=="Normal ITE":
                                                issue_dict[issueobj]=feature_type
                                                issuelist.append([issueobj.key,feature_type])
         result = {k: [i[0] for i in v ]for k, v in groupby(sorted(issuelist, key=lambda x: x[1]), lambda x: x[1])}
         buildissue(result)




def buildissue(result):
     issuedict=result
     emaillist=[]
     email_list=[]
     for key in issuedict:
        feature_type=key
        if (feature_type=="Mobile" or feature_type=="Admin" or feature_type=="Frontend" or feature_type=="CS_Osticket" or feature_type=="MyAccount" or feature_type=="Vendor" or feature_type=="SOA" or feature_type=="SOA-APP" or feature_type=="Oauth" or feature_type=="SOA-Wiki" or feature_type=="StoreManager" or feature_type=="MerchantHelpdesk" or feature_type=="Login" or feature_type=="smartshipsupport" or feature_type=="clues_network" or feature_type=="API" or feature_type=="Feed" or feature_type=="mastercatalog" or feature_type=="posapp" or feature_type=="ShopCluesBlog" or feature_type=="Automation" or feature_type=="rural-affiliate" or feature_type=="merchantSharp" or feature_type=="Affiliate"or feature_type=="smartship-api"or feature_type=="smartship-frontend"or feature_type=="crmshap" or feature_type=="chat-boat"):
                servertypedict = {'Mobile':'mobile', 'Admin': 'admin','Frontend':'frontend','CS_Osticket':'cs-osticket','MyAccount':'myaccount','Vendor':'vendor','SOA':'soa','SOA-APP':'soa-app','Oauth':'oauth','SOA-Wiki':'soa-wiki','StoreManager':'storemanager','MerchantHelpdesk':'merchanthelpdesk8','Login':'login','smartshipsupport':'smartshipsupport','clues_network':'clues_network','API':'api','Microsite':"microsite","Feed":"feed","mastercatalog":"mastercatalog","posapp":"posapp","ShopCluesBlog":"shopcluesblog","Automation":"shopqa","rural-affiliate":"rural-affiliate","merchantSharp":"merchantsupport","Affiliate":"affiliates","smartship-api":"smartship-api","smartship-frontend":"smartship-frontend","crmshap":"crmshap","chat-boat":"chatbot"}
		server_type=servertypedict[feature_type]
                issue=issuedict[key]
                issue_name= ','.join(issue)
                param={"JiraIDs":issue_name,"Server":server_type,"Build_Type":"ITE","CreateIssue":True}
                job_info=server.get_job_info(job_name)
                lastbuilt=job_info['lastCompletedBuild']
                b_number=job_info['lastCompletedBuild']['number']
                res=server.build_job(job_name,param)
                next_build=b_number+1
                while b_number!=next_build:
                        job_info=server.get_job_info(job_name)
                        b_number=job_info['lastCompletedBuild']['number']
                build_info=server.get_build_console_output(job_name,b_number)
                f = open("build.log", "a")
                f.write(build_info)
                size=len(issue)
                if size==1:
			build_info_str=str(build_info)
                        message=""
                        if "Revision Number Not Found" in build_info_str:
                                message="Revision Number Not Found"
                        elif "Server not matched" in build_info_str:
                                message="Server not matched"
                        elif "feature type not matched" in build_info_str:
                                message="feature type not matched"
                        elif "server and feature type not matched" in build_info_str:
                                message="server and feature type not matched"
                        elif "Build type or Server Missing" in build_info_str:
                                message="Build type or Server Missing"
                        elif "tag creation failure" in build_info_str:
                                message="tag creation failure"
                        elif "switch failure" in build_info_str:
                                message="switch failure"
                        elif "update failure" in build_info_str:
                                message="update failure"
                        elif "repository is not present" in build_info_str:
                                message="repository is not present"
                        elif "conflict found in the fILE" in build_info_str:
                                message="conflict found in the fILE"
                        elif "switch2 failure" in build_info_str:
                                message="switch2 failure"
                        elif "checkCommit failure" in build_info_str:
                                message="checkCommit failure"
                        elif "revision number is not present" in build_info_str:
                                message="revision number is not present"
                        else:
                                message=""
			lastsuccessbuilt=job_info['lastSuccessfulBuild']['number']
                        if lastsuccessbuilt!=b_number:
                                name_of_issue=issue[0]
                                issueobj=jira.issue(name_of_issue)
                                emailobj1=issueobj.raw['fields']['assignee']
                                if emailobj1 is not None:
                                        email1=emailobj1['emailAddress']
                                        email_list.append(email1)
                                emailobj2=issueobj.raw['fields']['customfield_10402']
                                if emailobj2 is not None:
                                        email2=emailobj2['emailAddress']
                                        email_list.append(email2)
                                emailobj3=issueobj.raw['fields']['customfield_10312']
                                if emailobj3 is not None:
                                        email3=emailobj3['emailAddress']
                                        email_list.append(email3)
                                emailobj4=issueobj.raw['fields']['customfield_10311']
                                if emailobj4 is not None:
                                        email4=emailobj4['emailAddress']
                                        email_list.append(email4)
                                emailobj5=emailobj4=issueobj.raw['fields']['reporter']
                                if emailobj5 is not None:
                                        email5=emailobj5['emailAddress']
                                        email_list.append(email5)
                                emailobj6=issueobj.raw['fields']['customfield_10301']
                                if emailobj6 is not None:
                                        email6=emailobj6['emailAddress']
                                        email_list.append(email6)
                                emailobj7=issueobj.raw['fields']['customfield_10300']
                                if emailobj7 is not None:
                                        email7=emailobj7['emailAddress']
                                        email_list.append(email7)
                                emailobj8=issueobj.raw['fields']['customfield_10303']
                                if emailobj8 is not None:
                                        email8=emailobj8['emailAddress']
                                        email_list.append(email8)
                                for email in email_list:
                                        if email not in emaillist:
						 emaillist.append(email)
                                sendnotification(emaillist,name_of_issue,message)

                else:
                        build_info_str=str(build_info)
                        message=""
                        if "Revision Number Not Found" in build_info_str:
                                message="Revision Number Not Found"
                        elif "Server not matched" in build_info_str:
                                message="Server not matched"
                        elif "feature type not matched" in build_info_str:
                                message="feature type not matched"
                        elif "server and feature type not matched" in build_info_str:
                                message="server and feature type not matched"
                        elif "Build type or Server Missing" in build_info_str:
                                 message="Build type or Server Missing"
                        elif "tag creation failure" in build_info_str:
                                message="tag creation failure"
                        elif "switch failure" in build_info_str:
                                message="switch failure"
                        elif "update failure" in build_info_str:
                                message="update failure"
                        elif "repository is not present" in build_info_str:
                                message="repository is not present"
                        elif "conflict found in the fILE" in build_info_str:
                                message="conflict found in the fILE"
                        elif "switch2 failure" in build_info_str:
                                message="switch2 failure"
                        elif "checkCommit failure" in build_info_str:
                                message="checkCommit failure"
                        elif "revision number is not present" in build_info_str:
                                message="revision number is not present"
                        else:
                                message=""
                        lastsuccessbuilt=job_info['lastSuccessfulBuild']['number']
                        if lastsuccessbuilt!=b_number:
				name_of_issue=issue[0]
                                issueobj=jira.issue(name_of_issue)
                                emailobj1=issueobj.raw['fields']['assignee']
                                if emailobj1 is not None:
                                        email1=emailobj1['emailAddress']
                                        email_list.append(email1)
                                emailobj2=issueobj.raw['fields']['customfield_10402']
                                if emailobj2 is not None:
                                        email2=emailobj2['emailAddress']
                                        email_list.append(email2)
                                emailobj3=issueobj.raw['fields']['customfield_10312']
                                if emailobj3 is not None:
                                        email3=emailobj3['emailAddress']
                                        email_list.append(email3)
                                emailobj4=issueobj.raw['fields']['customfield_10311']
                                if emailobj4 is not None:
                                        email4=emailobj4['emailAddress']
                                        email_list.append(email4)
                                emailobj5=emailobj4=issueobj.raw['fields']['reporter']
                                if emailobj5 is not None:
                                        email5=emailobj5['emailAddress']
                                        email_list.append(email5)
                                emailobj6=issueobj.raw['fields']['customfield_10301']
                                if emailobj6 is not None:
                                        email6=emailobj6['emailAddress']
                                        email_list.append(email6)
                                emailobj7=issueobj.raw['fields']['customfield_10300']
                                if emailobj7 is not None:
                                        email7=emailobj7['emailAddress']
                                        email_list.append(email7)
                                emailobj8=issueobj.raw['fields']['customfield_10303']
                                if emailobj8 is not None:
                                        email8=emailobj8['emailAddress']
                                        email_list.append(email8)
                                for email in email_list:
                                        if email not in emaillist:
                                                emaillist.append(email)
                                sendnotification(emaillist,name_of_issue,message)
			else:
                                issuefailure=[]
                                for issuename in issue:
                                        issueobj=jira.issue(issuename)
                                        BS_id=issueobj.raw['fields']['customfield_10902']
                                        if BS_id is None:
                                                issuefailure.append(issuename)

                                for issuename1 in issuefailure:
                                        name_of_issue=issuename1
                                        issueobj=jira.issue(name_of_issue)
                                        emailobj1=issueobj.raw['fields']['assignee']
                                        if emailobj1 is not None:
                                                email1=emailobj1['emailAddress']
                                                email_list.append(email1)
                                        emailobj2=issueobj.raw['fields']['customfield_10402']
                                        if emailobj2 is not None:
                                                email2=emailobj2['emailAddress']
                                                email_list.append(email2)
                                        emailobj3=issueobj.raw['fields']['customfield_10312']
                                        if emailobj3 is not None:
                                                email3=emailobj3['emailAddress']
                                                email_list.append(email3)
                                        emailobj4=issueobj.raw['fields']['customfield_10311']
                                        if emailobj4 is not None:
                                                email4=emailobj4['emailAddress']
                                                email_list.append(email4)
                                        emailobj5=emailobj4=issueobj.raw['fields']['reporter']
                                        if emailobj5 is not None:
                                                email5=emailobj5['emailAddress']
                                                email_list.append(email5)
                                        emailobj6=issueobj.raw['fields']['customfield_10301']
                                        if emailobj6 is not None:
                                                email6=emailobj6['emailAddress']
                                                email_list.append(email6)
                                        emailobj7=issueobj.raw['fields']['customfield_10300']
                                        if emailobj7 is not None:
                                                email7=emailobj7['emailAddress']
                                                email_list.append(email7)
                                        emailobj8=issueobj.raw['fields']['customfield_10303']
                                        if emailobj8 is not None:
                                                email8=emailobj8['emailAddress']
                                                email_list.append(email8)
                                        for email in email_list:
                                                if email not in emaillist:
                                                        emaillist.append(email)
                                        sendnotification(emaillist,issuename1,message)                                 
						
def sendnotification(emaillist,issue_name,message):
                file1 = open("pass.txt","r+")
                password=file1.read()
                msg = MIMEMultipart()
                email_user = 'anshul.walia@shopclues.com'
                email_password = password
                email_send = emaillist
                subject = 'Jenkins build failed'
                msg['From'] = email_user
                msg['To'] = ", ".join(email_send)
                msg['Subject'] = subject
                body =  """ 
                 <html> 
                 <body>
                 <style>
                 table, th, td { 
                   border: 1px solid black;
                                } 
                  </style> 
                  <table>
                  <tr>
                  <th> Build Failed on ticket</th> 
                  <td> """ + issue_name + """ </td> 
                  </tr>
                  <tr>
                  <th>Failure Reason</th>
                  <td> """ + message + """ </td>
                  </tr>
                  </body>
                  </html>
                       """

                msg.attach(MIMEText(body,'html'))
                text = msg.as_string()
                server1=''
                try:
			server1 = smtplib.SMTP('smtp-mail.outlook.com',587)
                        #server.set_debuglevel(1) 
                        server1.starttls()
                        server1.login(email_user,email_password)
                        server1.sendmail(email_user,email_send,text)
                finally:
                        server1.quit()



getissueinfo()
			
