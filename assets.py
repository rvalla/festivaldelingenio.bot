import os
import random as rd

class Assets():
	"The class the bot use to access the assets..."

	def __init__(self):
		self.img_path = "assets/img/"
		self.rebuses = open("assets/img/rebuses/rebuses.csv").readlines()[1:]
		self.adivinanzas = open("assets/text/adivinanzas.csv").readlines()[1:]
		self.palindromos = open("assets/text/palindromos.txt").readlines()
		self.stickers_ids = self.build_sticker_matrix("assets/text/stickers.csv")
		self.videos = open("assets/videos.csv").readlines()[1:]

	#Returning a text line from rebuses.csv database...
	def get_rebus_data(self):
		return rd.choice(self.rebuses)

	#Returning the image from a rebus...
	def get_rebus_image(self, path):
		return open(path, "rb")

	#Returning a line in adivinanzas.csv database...
	def get_adivinanza_data(self):
		return rd.choice(self.adivinanzas)

	#Returning a random palindromo...
	def get_palindromo(self):
		return rd.choice(self.palindromos)

	#Returning a line in videos.csv database...
	def get_video_data(self):
		return rd.choice(self.videos)

	#Returning file_id of a sticker of the requested category (victory, hint, loose)...
	def get_sticker_id(self, code):
		return rd.choice(self.stickers_ids[code])

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
