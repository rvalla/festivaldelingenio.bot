import json as js
import logging

class Game():
	"The class the bot use let users to play..."

	def __init__(self):
		self.minor_moves = 0 #Counting number of moves...
		self.minor_numbers = set() #A set with all numbers played...
		self.minor_players_moves = {} #A dictionary which maps numbers with players...
		self.minor_players_ids = set() #The set of all players in a round...
		self.logger = logging.getLogger(__name__)

	#Saving a minor number move...
	def save_minor_number(self, number, player, id):
		moving = False
		if not id in self.minor_players_ids:
			moving = True
			self.minor_moves += 1
			self.minor_numbers.add(number)
			self.minor_players_ids.add(id)
			try:
				self.minor_players_moves[number].append((player, id))
			except:
				self.minor_players_moves[number] = [(player, id)]
			self.logger.info(player + " registró una jugada del menor número: " + str(number))
		else:
			self.logger.info(player + " intentó registrar una 2da jugada del menor número")
		return moving

	#Looking for a minor number round winner...
	def end_minor_game(self):
		winner_exist = False
		winner = "Jaime Poniachik"
		number = "pi * ln(e)"
		id = None
		for n in range(1,300):
			if n in self.minor_numbers:
				if len(self.minor_players_moves[n]) == 1:
					number = str(n)
					winner = self.minor_players_moves[n][0][0]
					id = self.minor_players_moves[n][0][1]
					winner_exist = True
					break
		if winner_exist:
			self.logger.info(winner + " ganó una ronda del menor número (" + number + ")")
		else:
			self.logger.info("Termina una ronda del menor número sin ganador")
		return winner_exist, number, winner, id

	#Returning the ids from the loosers of a minor number round to inform the result...
	def get_minor_loosers(self, winner_id):
		self.minor_players_ids.discard(winner_id)
		return self.minor_players_ids

	#Returning the actual state of a minor number round...
	def minor_info(self):
		m = "<b>Estado del juego</b>\n" + \
			"Cantidad de jugadas: " + str(self.minor_moves) + "\n" + \
			"Cantidad de números: " + str(len(self.minor_numbers)) + "\n" + \
			"Jugadas: " + str(self.minor_numbers)
		return m

	#Getting ready for a new minor number round...
	def minor_reset(self):
		self.logger.info("Reseteando ronda del menor número: " + str(self.minor_moves) + " jugadas, " + str(len(self.minor_numbers)) + " números.")
		self.minor_moves = 0
		self.minor_numbers.clear()
		self.minor_players_moves.clear()
		self.minor_players_ids.clear()
