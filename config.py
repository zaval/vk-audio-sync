#!/usr/bin/env python3

from vk import Vk
import configparser
import os


def main():
	
	login = input('Enter vk.com username: ')
	password = input('Enter vk.com password: ')
	
	vk = Vk('3742196')
	
	res = vk.login(login, password)
	
	if not res:
		print('Incorrect login or password')
		exit()
	
	if not vk.oauth():
		print("Can't get access token")
		exit()
	
	cnf = configparser.ConfigParser()
	
	cnf['main'] = {
		'token': vk.token,
		'uids': vk.my_uid,
		}
	
	savePath = '{}/Music'.format(os.getenv('HOME'))
	
	d = input('Directory for saving audios [{}]: '.format(savePath))
	if d:
		savePath = d
	
	cnf['main']['path'] = savePath
	
	if not os.path.exists(savePath):
		os.makedirs(savePath)
	
	res = input('Do you want to add another uids except {}? [y/n]: '.format(vk.my_uid))
	
	if res.lower() == 'y':
		ids = input('Enter uids seperate by comma: ')
		cnf['main']['uids'] += ',' + ids.strip()
	
	with open('config.ini', 'w') as f:
		cnf.write(f)
	
	return 0

if __name__ == '__main__':
	main()

