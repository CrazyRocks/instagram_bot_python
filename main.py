import re
import requests
import json
import string
import random
import time
import config
import sys
import logic

device=''

head={'X-IG-Capabilities':'3wI=',
'User-Agent':'Instagram 9.2.1 (iPad5,4; iPhone OS 9_3_3; en_DE; en-DE; scale=2.00; 640x960) AppleWebKit/420+'}

s=requests.session()
s.verify=False
s.headers.update(head)

#config
base_api='https://i.instagram.com/api/v1/'
#end
	
def login(user,passw):
	data=logic._generate_body('{"username":"%s","password":"%s","device_id":"%s","login_attempt_count":"0"}'%(user,passw,device,))
	r=s.post(base_api+'accounts/login/',data=data)
	return json.loads(r.content)
	
def liked_posts():
	r=s.get(base_api+'feed/liked/')
	data=json.loads(r.content)
	if data['num_results'] > 0:
		for item in data['items']:
			print item['id'],item['user']['pk']
			unlike(item['id'],item['user']['pk'])
			time.sleep(random.randint(1,7))
	else:
		exit(0)

def unlike(id,tid):
	url='media/%s/unlike/'%(id)
	data=logic._generate_body('{"_csrftoken":"","media_id":"%s","module_name":"photo_view","user_id":"%s","_uuid":"%s","_uid":"829667420"}'%(id,tid,device,))
	r=s.post(base_api+url,data=data)
	data= json.loads(r.content)
	if data['status']=='fail':
		print '[-] blocked'
		exit(1)
	
def main():
	if len(sys.argv) == 3:
		global device
		device='%s-%s-%s-%s-%s'%(logic._generate_device(8),logic._generate_device(4),logic._generate_device(4),logic._generate_device(4),logic._generate_device(12))
		login_data= login(sys.argv[1],sys.argv[2])
		print 'user:%s, user_id:%s'%(login_data['logged_in_user']['username'],login_data['logged_in_user']['pk'])
		while(True):
			print '[!] removing likes'
			liked_posts()
	else:
		print '[-] .py username password'
	
if __name__ == '__main__':
	main()