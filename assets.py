import os
import random as rd

class Assets():
	"The class the bot use to access the assets..."

	def __init__(self):
		self.img_path = "assets/img/"
		self.rebuses = open("assets/data_rebuses.csv").readlines()[1:]
		self.acertijos = open("assets/text/acertijos.csv").readlines()[1:]
		self.palindromos = open("assets/text/palindromos.txt").readlines()
		self.reverse_numbers = open("assets/data_reverse_numbers.csv").readlines()[1:]
		self.videos = open("assets/videos.csv").readlines()[1:]
		self.last_sended = [0,0,0,0,0]
		self.available = self.build_available_limits()
		self.stickers_ids = self.build_sticker_matrix("assets/stickers.csv")

	#Returning a text line from rebuses.csv database...
	def get_rebus_data(self):
		self.next_to_send(0)
		return self.rebuses[self.last_sended[0]]

	#Returning the image from a rebus...
	def open_rebus_image(self, path):
		return open(path, "rb")

	#Returning a line in adivinanzas.csv database...
	def get_acertijo_data(self):
		self.next_to_send(1)
		return self.acertijos[self.last_sended[1]]

	#Returning a random palindromo...
	def get_palindromo(self):
		self.next_to_send(2)
		m = self.palindromos[self.last_sended[2]]
		m += m[::-1]
		return m

	#Returning data from a reverse number...
	def get_random_reverse_number(self):
		self.next_to_send(3)
		return self.reverse_numbers[self.last_sended[3]]

	def get_reverse_number(self, n):
		return self.reverse_numbers[n-1]

	#Returning a line in videos.csv database...
	def get_video_data(self):
		self.next_to_send(4)
		return self.videos[self.last_sended[4]]

	#Returning file_id of a sticker of the requested category (victory, hint, loose)...
	def get_sticker_id(self, code):
		return rd.choice(self.stickers_ids[code])

	#Loading number of available assets in each category...
	def build_available_limits(self):
		limits = []
		limits.append(len(self.rebuses))
		limits.append(len(self.acertijos))
		limits.append(len(self.palindromos))
		limits.append(len(self.reverse_numbers))
		limits.append(len(self.videos))
		return limits

	#Deciding what asset to send...
	def next_to_send(self, category):
		self.last_sended[category] = (self.last_sended[category] + rd.randint(1,7)) % self.available[category]

	#Building the matrix to store stickers database...
	def build_sticker_matrix(self, path):
		source = open(path).readlines()[1:]
		victory = []
		hint = []
		loose = []
		for s in source:
			data = s.split(";")
			if int(data[3]) == 0:
				victory.append(data[1])
			elif int(data[3]) == 1:
				hint.append(data[1])
			elif int(data[3]) == 2:
				loose.append(data[1])
		result = []
		result.append(victory)
		result.append(hint)
		result.append(loose)
		return result
