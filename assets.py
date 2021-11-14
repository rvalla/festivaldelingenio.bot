import os
import random as rd

class Assets():
	"The class the bot use to access the assets..."

	def __init__(self):
		self.img_path = "assets/img/"
		self.rebuses = open("assets/img/rebuses/rebuses.csv").readlines()[1:]
		print(self.rebuses)
		self.palindromos = open("assets/text/palindromos.txt").readlines()
		self.videos = open("assets/videos.csv").readlines()[1:]

	def get_rebus_data(self):
		return rd.choice(self.rebuses)

	def get_rebus_image(self, path):
		return open(path, "rb")

	def get_palindromo(self):
		return rd.choice(self.palindromos)

	def get_video_data(self):
		return rd.choice(self.videos)
