import json as js

class Game():
	"The class the bot use let users to play..."

	def __init__(self):
		self.numbers = set()
		self.players = {}
		self.players_ids = {}

	#Saving a move...
	def save_move(self, number, player, id):
		n = int(number)
		self.numbers.add(n)
		try:
			self.players[n].append(player)
			self.players_ids[n].append(id)
		except:
			self.players[n] = [player]
			self.players_ids[n] = [id]

	#Looking for a winner...
	def end_game(self):
		unique = False
		winner = "NOBODY"
		id = None
		number = -1
		for n in range(1,1000):
			if n in self.numbers:
				if len(self.players[n]) == 1:
					number = n
					winner = self.players[n][0]
					id = self.players_ids[n][0]
					break
		self.numbers.clear()
		self.players.clear()
		return str(number), winner, id
