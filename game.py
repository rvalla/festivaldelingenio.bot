import json as js
import logging

class Game():
	"The class the bot use let users to play..."

	def __init__(self):
		self.moves = 0 #Counting number of moves...
		self.numbers = set() #A set with all numbers played...
		self.players_moves = {} #A dictionary which maps numbers with players...
		self.players_ids = set() #The set of all players in a round...
		self.logger = logging.getLogger(__name__)

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
			self.logger.info(player + " registró una jugada: " + str(number))
		else:
			self.logger.info(player + " intentó registrar una 2da jugada")
		return moving

	#Looking for a winner...
	def end_game(self):
		winner_exist = False
		winner = "Jaime Poniachik"
		number = "pi * ln(e)"
		id = None
		for n in range(1,250):
			if n in self.numbers:
				if len(self.players_moves[n]) == 1:
					number = str(n)
					winner = self.players_moves[n][0][0]
					id = self.players_moves[n][0][1]
					winner_exist = True
					break
		if winner_exist:
			self.logger.info(winner + " ganó una ronda (" + number + ")")
		else:
			self.logger.info("Termina una ronda sin ganador")
		return winner_exist, number, winner, id

	#Returning the ids from the loosers of a round to inform the result...
	def get_loosers(self, winner_id):
		self.players_ids.discard(winner_id)
		return self.players_ids

	#Returning the actual state of a round...
	def game_info(self):
		m = "<b>Estado del juego</b>\n" + \
			"Cantidad de jugadas: " + str(self.moves) + "\n" + \
			"Cantidad de números: " + str(len(self.numbers)) + "\n" + \
			"Jugadas: " + str(self.numbers)
		return m

	#Getting ready for a new round...
	def reset(self):
		self.logger.info("Reseteando ronda: " + str(self.moves) + " jugadas, " + str(len(self.numbers)) + " números.")
		self.moves = 0
		self.numbers.clear()
		self.players_moves.clear()
		self.players_ids.clear()
