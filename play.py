import json as js
import logging
import random as rd
import datetime as dt

class Play():
	"The class the bot use let users to play..."

	def __init__(self, path):
		self.output_path = path
		self.minor_moves = 0 #Counting number of moves...
		self.minor_numbers = set() #A set with all numbers played...
		self.minor_players_moves = {} #A dictionary which maps numbers with players...
		self.minor_players_ids = set() #The set of all players in a round...
		self.last_firewall = 0 #The last firewall which was sent...
		self.firewall = open("assets/firewall.csv").readlines()[1:]
		self.available = len(self.firewall) #Total firewalls available...
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

	#Saving minor game result...
	def save_minor(self, winner, winner_n):
		file = open(self.output_path, "a")
		t = dt.datetime.now()
		line = str(t.year) + "-" + str(t.month) + "-" + str(t.day)
		line += str(self.minor_moves) + ";"
		line += str(len(self.minor_numbers)) + ";"
		line += winner + ";"
		line += str(winner_n) + ";"
		line += str(self.minor_numbers) + "\n"
		file.write(line)
		file.close()

	#Getting ready for a new minor number round...
	def minor_reset(self):
		self.logger.info("Reseteando ronda del menor número: " + str(self.minor_moves) + " jugadas, " + str(len(self.minor_numbers)) + " números.")
		self.minor_moves = 0
		self.minor_numbers.clear()
		self.minor_players_moves.clear()
		self.minor_players_ids.clear()

	#Deciding if a move in firewalls game is good...
	def check_firewall(self, algorithm, move, parameters=[]):
		if algorithm == 0:
			try:
				n = int(move)
				return self.check_firewall_range(n, parameters)
			except:
				return False
		elif algorithm == 1:
			try:
				n = int(move)
				return self.check_firewall_remainder(n, parameters)
			except:
				return False
		elif algorithm == 2:
			return self.check_firewall_letter_count(move, parameters[0])
		elif algorithm == 3:
			return self.check_firewall_letter_ends(move, parameters)
		elif algorithm == 4:
			return self.check_firewall_split(move, parameters)
		elif algorithm == 5:
			return self.check_firewall_positions(move, parameters)

	#Checking a move in firewall's game: number range type...
	def check_firewall_range(self, move, range):
		good_move = False
		if move > range[0] and move < range[1]:
			good_move = True
		return good_move

	#Checking a move in firewall's game: number remainder type...
	def check_firewall_remainder(self, move, values):
		good_move = False
		if move%values[0] == values[1]:
			good_move = True
		return good_move

	#Checking a move in firewall's game: letter count type...
	def check_firewall_letter_count(self, move, count):
		good_move = False
		if len(move) == count:
			good_move = True
		return good_move

	#Checking a move in firewall's game: letter ends type...
	def check_firewall_letter_ends(self, move, letters):
		good_move = False
		if move[0] == letters[0] and move[len(move)-1] == letters[1]:
			good_move = True
		return good_move

	#Checking a move in firewall's game: symbol count type...
	def check_firewall_split(self, move, values):
		good_move = False
		if len(move.split(values[1])) == int(values[0]):
			good_move = True
		return good_move

	#Checking a move in firewall's game: symbol position type...
	def check_firewall_positions(self, move, parameters):
		good_move = False
		loop_size = len(parameters)//2
		count = 0
		try:
			for i in range(loop_size):
				if move[int(parameters[2*i])] == parameters[2*i+1]:
					count += 1
		except:
			pass
		if count == loop_size:
			good_move = True
		return good_move

	#Building a firewall's challenge for words of n letters...
	def get_firewall_game(self):
		self.next_to_send()
		data = self.firewall[self.last_firewall].split(";")
		round = {}
		round["command"] = data[0]
		round["type"] = data[1]
		round["algorithm"] = int(data[2])
		round["ex_pass"] = data[3]
		round["ex_notpass"] = data[4]
		round["in_type"] = data[5]
		round["parameters"] = self.firewall_parameters(data[6], data[7])
		return round

	#Building a firewalls challenge parameters list...
	def firewall_parameters(self, parameters_type, data):
		in_l = data.split(",")
		out_l = []
		if parameters_type == "numbers":
			for i in in_l:
				out_l.append(int(i))
		else:
			out_l = in_l
		return out_l

	#Selecting next firewall to send...
	def next_to_send(self):
		self.last_firewall = (self.last_firewall + rd.randint(1,7)) % self.available
