import json as js

class Game():
	"The class the bot use let users to play..."

	def __init__(self):
		self.moves = 0 #Counting number of moves...
		self.numbers = set() #A set with all numbers played...
		self.players_moves = {} #A dictionary which maps numbers with players...
		self.players_ids = set() #The set of all players in a round...

	#Saving a move...
	def save_move(self, number, player, id):
		moving = False
		if not id in self.players_ids:
			moving = True
			self.moves += 1
			self.numbers.add(number)
			self.players_ids.add(id)
			try:
				self.players_moves[number].append((player, id))
			except:
				self.players_moves[number] = [(player, id)]
		return moving

	#Looking for a winner...
	def end_game(self):
		unique = False
		winner = "NOBODY"
		id = None
		number = -1
		for n in range(1,1000):
			if n in self.numbers:
				if len(self.players_moves[n]) == 1:
					number = n
					winner = self.players_moves[n][0][0]
					id = self.players_moves[n][0][1]
					break
		return str(number), winner, id

	#Returning the ids from the loosers of a round to inform the result...
	def get_loosers(self, winner_id):
		self.players_ids.discard(winner_id)
		return self.players_ids

	#Returning the actual state of a round...
	def game_info(self):
		m = "<b>Estado del juego</b>\n" + \
			"Cantidad de jugadas: " + str(self.moves) + "\n" + \
			"Jugadas: " + str(self.numbers)
		return m

	#Getting ready for a new round...
	def reset(self):
		self.moves = 0
		self.numbers.clear()
		self.players_moves.clear()
		self.players_ids.clear()
