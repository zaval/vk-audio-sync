#!/usr/local/bin/python3
import re
from requests import *
import stagger

class Vk:

	def __init__(self, client_id, token=''):
		
		self.request = Session()
		self.my_uid = ''
		self.client_id = client_id
		self.token = token
		self.is_login = False


	def login(self, login, password):

		try:
			r = self.request.get('https://vk.com/')
		except:
			return False

		ip_h = re.search(r'ip_h" value="([^"]+)', r.text)

		if not ip_h:
			print("Can't find 'ip_h'")
			return False


		data = {
			'act': 'login',
			'role': 'al_frame',
			'expire': '',
			'captcha_sid': '',
			'captcha_key': '',
			'_origin': 'https://vk.com',
			'ip_h': ip_h.group(1),
			'email': login,
			'pass': password,
		}

		#~ print(data)

		try:
			r = self.request.post('https://login.vk.com/?act=login', data=data)
		except:
			return False

		redirect = re.search(r"onLoginDone\('/([^']+)", r.text)

		if redirect:
			try:
				r = self.request.get('https://vk.com/{}'.format(redirect.group(1)))
			except:
				return False
				
			uid = re.search(r'"uid":(\d+)', r.text)
			if uid:
				self.my_uid = uid.group(1)
				self.is_login = True
				return True
			else:
				return False
		else:
			return False


	def oauth(self):
		
		if self.token:
			try:
				r = self.request.get('https://api.vk.com/method/friends.get?v=5.24&access_token={}'.format(self.token))
			except:
				return False
			
			r = r.json()
			if 'error' not in r:
				return True
		try:
			r = self.request.get('https://oauth.vk.com/authorize?client_id={}&redirect_uri=https%3A%2F%2Foauth.vk.com%2Fblank.html&scope=1123330&response_type=token'.format(self.client_id))
		except:
			return False
		
		token = re.search(r'#access_token=(.+?)&', r.url)
		if token:
			self.token = token.group(1)
			return True
		
		direct_hash = re.search(r'direct_hash=([0-9a-f]+)', r.text)
		if not direct_hash:
			print('cant get direct_hash')
			return False
		direct_hash = direct_hash.group(1)
		
		ip_h = re.search(r'ip_h=([0-9a-f]+)', r.text)
		if not ip_h:
			print('cant get ip_h')
			return False
		ip_h = ip_h.group(1)
		
		_hash = re.search(r'&hash=([0-9a-f]+)', r.text)
		if not _hash:
			print('cant get hash')
			return False
		_hash = _hash.group(1)

		try:
			r = self.request.get('https://login.vk.com/?act=grant_access&client_id={}&settings=1123330&redirect_uri=https%3A%2F%2Foauth.vk.com%2Fblank.html&response_type=token&direct_hash={}&token_type=0&v=&state=&display=page&ip_h={}&hash={}&https=1'.format(client_id, direct_hash, ip_h, _hash))
		except:
			return False
		
		token = re.search(r'#access_token=(.+?)&', r.url)
		if token:
			self.token = token.group(1)
			return True
		else:
			print('cant oauth')
			return False
		
			

	def get_audios(self, uid=''):
		
		if not uid:
			uid = self.my_uid
		
		url = 'https://api.vk.com/method/audio.get?{}id={}v=5.24&access_token={}'.format('g' if uid.startswith('-') else 'u', uid.replace('-', ''), self.token)

		try:
			r = self.request.get(url)
		except:
			return False
		
		#~ print(r.url)
		
		try:
			r = r.json()
		except:
			return False
		
		return r
	

