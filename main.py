import config
import json
import logic
import random
import re
import requests
import sys
import time

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

head={'X-IG-Capabilities':'36rXAw==',
'User-Agent':'Instagram 22.0.0.10.68 (iPad5,4; iOS 10_2; en_DE; en-GB; scale=2.00; gamut=normal; 640x960) AppleWebKit/420+'}

class Instagram(object):
	def __init__(self,user,passw):
		self.user=user
		self.passw=passw
		self.device='%s-%s-%s-%s-%s'%(logic._generate_device(8),logic._generate_device(4),logic._generate_device(4),logic._generate_device(4),logic._generate_device(12))
		self.s=requests.session()
		self.s.verify=False
		self.s.headers.update(head)
		self.uid=0
		self.csfr=None
		self.base_api='https://i.instagram.com'

	def login(self):
		data={}
		data['username']=self.user
		data['password']=self.passw
		data['device_id']=self.device
		data['login_attempt_count']='0'
		data=logic._generate_body(data)
		r=self.s.post(self.base_api+'/api/v1/accounts/login/',data=data)
		res= json.loads(r.content)
		self.uid=res['logged_in_user']['pk']
		self.csfr=self.s.cookies['csrftoken']
		return res
	
	def reels_tray(self):
		return json.loads(self.s.get(self.base_api+'/api/v1/feed/reels_tray/').content)
	
	def seen(self,str1,str2):
		data={}
		data['_csrftoken']=self.csfr
		data['_uuid']=self.device
		data['_uid']=self.uid
		data['reels']={}
		data['live_vods']={str1:[str2]}
		data=logic._generate_body(data)
		return self.s.post(self.base_api+'/api/v2/media/seen/?reel=1&live_vod=0',data=data)
	
	def watchStories(self):
		stories=self.reels_tray()['tray']
		for i in stories:
			pk=i['user']['pk']
			if 'items' in i:
				items=i['items']
				for o in items:
					id=o['id']
					taken_at=o['taken_at']
					str1='%s_%s'%(id,pk)
					str2='%s_%s'%(taken_at,int(time.time()))
					self.seen(str1,str2)
	
	def liked_posts(self):
		r=self.s.get(base_api+'feed/liked/')
		data=json.loads(r.content)
		if data['num_results'] > 0:
			for item in data['items']:
				print item['id'],item['user']['pk']
				self.unlike(item['id'],item['user']['pk'])
				time.sleep(random.randint(1,7))
		else:
			exit(0)

	def unlike(self,id,tid):
		url='media/%s/unlike/'%(id)
		data=logic._generate_body('{"_csrftoken":"","media_id":"%s","module_name":"photo_view","user_id":"%s","_uuid":"%s","_uid":"%s"}'%(id,tid,self.device,self.uid,))
		r=self.s.post(self.base_api+url,data=data)
		data= json.loads(r.content)
		if data['status']=='fail':
			print '[-] blocked'
			exit(1)

if __name__ == '__main__':
	if len(sys.argv) == 3:
		i=Instagram(sys.argv[1],sys.argv[2])
		login_data=i.login()
		print 'user:%s, user_id:%s'%(login_data['logged_in_user']['username'],login_data['logged_in_user']['pk'])
		i.watchStories()
		exit(1)
		while(True):
			print '[!] removing likes'
			i.liked_posts()
	else:
		print '[-] .py username password'