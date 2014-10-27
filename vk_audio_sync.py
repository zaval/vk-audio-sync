#!/usr/local/bin/python3
import configparser
import os
import time
import sys
from as_daemon_class import daemon
from vk import Vk
import stagger


class VkDaemon(daemon):

	client_id = ''#сюда client_id созданного приложения

	def __init__(self, pid):

		try:
			self.log_f = open('/var/log/vk_audio.log', 'a')
		except Exception as e:
			print("Can't open log file: {}".format(e))
		return super().__init__(pid)

	def __del__(self):
		try:
			self.log_f.close()
		except:
			pass

	def log(self, text):
		try:
			self.log_f.write('{} {}\n'.format(time.strftime('%d.%m.%Y %H:%M:%S'), text))
			f.flush()
		except:
			pass

	def start(self):
		self.cnf = configparser.ConfigParser()
		try:
			self.cnf.read('config.ini')
		except:
			self.log('не смогли открыть файл конфига')
			return

		return super().start()

	def run(self):

		

		if 'main' in self.cnf and 'token' in self.cnf['main']:
			self.vk = Vk(self.client_id, self.cnf['main']['token'])
		else:
			self.log('не задан токен в конфиге, запустите config.py')
			return

		try:
			uids = [x.strip() for x in self.cnf['main']['uids'].split(',')]
		except:
			uids = ['']

		try:
			path = self.cnf['main']['path']
		except:
			path = '{}/music'.format(os.getenv('HOME'))

		if not os.path.exists(path):
			os.makedirs(path)

		if not self.vk.oauth():
			self.log('не смогли авторизоваться с указанным токеном, запустите config.py')
			return

		delay = 30
		if 'main' in self.cnf and 'delay' in self.cnf['main']:
			try:
				delay = int(self.cnf['main']['delay'])
			except:
				pass

		while True:

			for uid in uids:
				audios = self.vk.get_audios(uid)

				if not audios:
					continue

				for a in audios['response']:

					fname = '{}/{}_{}.mp3'.format(path, a['owner_id'], a['aid'])
					if os.path.exists(fname):
						continue

					self.log('загружаем аудио {} - {}'.format(a['artist'], a['title']))
					try:
						r = self.vk.request.get(a['url'])
						with open(fname, 'wb') as f:
							f.write(r.content)

						tag = stagger.tags.Tag23()
						tag.artist = a['artist']
						tag.title = a['title']
						tag.write(fname)


					except Exception as e:
						self.log('не смогли загузить {}: {}'.format(a['url'], e))
					
			time.sleep(delay)

if __name__ == "__main__":
		daemon = VkDaemon('/tmp/vk_audio_sync.pid')
		if len(sys.argv) == 2:
				if 'start' == sys.argv[1]:
						daemon.start()
				elif 'stop' == sys.argv[1]:
						daemon.stop()
				elif 'restart' == sys.argv[1]:
						daemon.restart()
				elif 'status' == sys.argv[1]:
						daemon.status()
				else:
						print("Unknown command")
						sys.exit(2)
				sys.exit(0)
		else:
				print( "usage: %s start|stop|restart" % sys.argv[0])
				sys.exit(2)
