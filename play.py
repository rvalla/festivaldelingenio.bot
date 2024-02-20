import json as js
import logging
import random as rd
import datetime as dt

class Play():
    "The class the bot use let users to play..."

    def __init__(self, path):
        self.output_path = path
        self.minor_moves_count = 0 #Counting number of moves...
        self.minor_moves = [] #The list of all moves in minor number game...
        self.minor_numbers = set() #A set with all numbers played...
        self.minor_players_moves = {} #A dictionary which maps numbers with players...
        self.minor_players_ids = set() #The set of all players in a round...
        self.last_firewall = [0,0,0] #The last firewall which was sent...
        self.firewall, self.availables = self.load_firewalls() #Loading firewall database and total availables...
        self.levenshteins = self.load_levenshteins()
        self.logger = logging.getLogger(__name__)

    #Saving a minor number move...
    def save_minor_number(self, number, player, id):
        moving = False
        if not id in self.minor_players_ids:
            moving = True
            self.minor_moves_count += 1
            self.minor_moves.append(number)
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
        winner = "Nadie"
        number = "número único"
        id = None
        for n in range(1,1000):
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
            "Cantidad de jugadas: " + str(self.minor_moves_count) + "\n" + \
            "Cantidad de números: " + str(len(self.minor_numbers)) + "\n" + \
            "Números: " + str(self.minor_numbers) + "\n" + \
            "Jugadas: " + str(self.minor_moves)
        return m

    #Saving minor game result...
    def save_minor(self, winner, winner_n):
        file = open(self.output_path, "a")
        t = dt.datetime.now()
        line = str(t.year) + "-" + str(t.month) + "-" + str(t.day) + ";"
        line += "minor unique number;"
        line += str(self.minor_moves_count) + ";"
        line += str(len(self.minor_numbers)) + ";"
        line += winner + ";"
        line += str(winner_n) + ";"
        line += str(self.minor_numbers) + ";"
        line += str(self.minor_moves) + "\n"
        file.write(line)
        file.close()

    #Getting ready for a new minor number round...
    def minor_reset(self):
        self.logger.info("Reseteando ronda del menor número: " + str(self.minor_moves_count) + " jugadas, " + str(len(self.minor_numbers)) + " números.")
        self.minor_moves_count = 0
        self.minor_moves = []
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
            return self.check_firewall_positions(move, parameters)
        elif algorithm == 4:
            return self.check_firewall_split(move, parameters)
        elif algorithm == 5:
            return self.check_firewall_sum(move, parameters[0])
        elif algorithm == 6:
            return self.check_firewall_positions_sum(move, parameters)

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

    #Checking a move in firewall's game: symbol position type...
    def check_firewall_positions(self, move, parameters):
        good_move = False
        loop_size = len(parameters)//2
        move_size = len(move)
        count = 0
        for i in range(loop_size):
            if move[int(parameters[2*i])%move_size] == parameters[2*i+1]:
                count += 1
        if count == loop_size:
            good_move = True
        return good_move

    #Checking a move in firewall's game: symbol count type...
    def check_firewall_split(self, move, values):
        good_move = False
        if len(move.split(values[1])) == int(values[0]):
            good_move = True
        return good_move

    #Checking a movi in firewall's game: total digit sum...
    def check_firewall_sum(self, move, result):
        good_move = False
        s = 0
        for d in move:
            s += int(d)
        if s == result:
            good_move = True
        return good_move

    #Checking a movi in firewall's game: total digit positions sum...
    def check_firewall_positions_sum(self, move, parameters):
        good_move = False
        loop_size = len(parameters) - 1
        move_size = len(move)
        s = 0
        for i in range(loop_size):
            s += int(move[parameters[i]%move_size])
        if s == parameters[len(parameters)-1]:
            good_move = True
        return good_move

    #Building a firewall's challenge for words of n letters...
    def get_firewall_game(self, difficulty):
        self.next_firewall_to_send(difficulty)
        data = self.firewall[difficulty][self.last_firewall[difficulty]].split(";")
        round = {}
        round["command"] = data[0]
        round["type"] = data[1]
        round["algorithm"] = int(data[2])
        round["ex_pass"] = data[3]
        round["ex_notpass"] = data[4]
        round["in_type"] = data[5]
        round["parameters"] = self.firewall_parameters(data[6], data[7])
        round["hint"] = data[8]
        round["solution"] = data[9]
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
    def next_firewall_to_send(self, difficulty):
        self.last_firewall[difficulty] = (self.last_firewall[difficulty] + rd.randint(1,4)) % self.availables[difficulty]

    #Building firewall database...
    def load_firewalls(self):
        firewalls = []
        easy = []
        medium = []
        hard = []
        file = open("assets/firewall.csv").readlines()[1:]
        for l in file:
            data = l.split(";")
            if int(data[10]) == 0:
                easy.append(l)
            elif int(data[10]) == 1:
                medium.append(l)
            elif int(data[10]) == 2:
                hard.append(l)
        availables = [len(easy), len(medium), len(hard)]
        firewalls.append(easy)
        firewalls.append(medium)
        firewalls.append(hard)
        return firewalls, availables
    
    def levenshtein_word(self, level):
        tale_data = rd.choice(self.levenshteins)
        tale = tale_data[1]
        author = tale_data[0]
        level_size_range = self.levenshtein_word_size_range(level)
        size = rd.randint(level_size_range[0], level_size_range[1])
        word = rd.choice(tale_data[2][size][:len(tale_data[2][size])-1].split(" "))
        return tale, author, word
    
    def levenshtein_word_size_range(self, level):
        level_range = None
        if level < 3:
            level_range = [level - 1, level]
        elif level < 6:
            level_range = [level - 1, level + 1]
        elif level < 9:
            level_range = [level - 2, level + 2]
        else:
            level_range = [level - 2, level + 4]
        return level_range
    
    def levenshtein_letter(self, word):
        size = len(word)
        candidate = rd.randint(0, size-1)
        showed = [False for i in range(size)]
        hint = ""
        if size > 1:
            showed[candidate] = True
        for i in range(size):
            if showed[i]:
                hint += word[i]
            else:
                hint += "*"
        return hint

    def levenshtein_hint(self, word):
        size = len(word)
        candidates = rd.sample(range(size), size // 2)
        showed = [False for i in range(size)]
        for c in candidates:
            showed[c] = True
        hint = ""
        for i in range(size):
            if showed[i]:
                hint += word[i]
            else:
                hint += "*"
        return hint

    #Measuring Levenshtein distance dinamically...
    #https://en.wikipedia.org/wiki/Levenshtein_distance#Iterative_with_full_matrix
    def distance(self, word_a, word_b):
       m = self.compute_matrix(word_a, word_b, len(word_a), len(word_b))
       return m[len(m)-1][len(m[0])-1]

    #Getting details from a distance computation...
    def detailed_distance(self, word_a, word_b):
        m = self.compute_matrix(word_a, word_b, len(word_a), len(word_b))
        s = "Computing distance between " + word_a + " and " + word_b + ":\n\n"
        s += self.get_matrix_string(word_a, word_b, m)
        s += "\n\n"
        s += "Distance = " + str(m[len(m)-1][len(m[0])-1])
        return s

    #Building the matrix to compute Levenshtein distance between two words...
    def compute_matrix(self, word_a, word_b, a, b):
        #We create the matrix of len(word_a) + 1 rows and len(word_b) + 1 columns
        m = self.build_empty_matrix(a, b)
        #Now we compute Levenshtein distance between all prefixes...
        for r in range(a):
            for c in range(b):
                #We check if both characters are equal...
                x = 1
                if word_a[r] == word_b[c]:
                    x = 0
                m[r+1][c+1] = min([
                                m[r+1][c] + 1, #insertion vs deletion vs replacement
                                m[r][c+1] + 1,
                                m[r][c] + x
                            ])
        return m
    
    #Building an empty matrix to work with...
    def build_empty_matrix(self, a, b):
        m = [[n for n in range(b + 1)]]        
        for i in range (1, a + 1):
            m.append([0 for n in range(b+1)])
        for i in range(1,len(m)):
            m[i][0] = i
        return m

    #Loading words for Levenshtein challenges...
    def load_levenshteins(self):
        file = open("assets/levenshtein.csv").readlines()[1:]
        l = []
        for f in file:
            data = f.split(";")
            l.append((data[0], data[1], open(data[2]).readlines()))
        return l
    
    #Saving Levenshtein game result...
    def save_levenshtein(self, name, level, words, attempts):
        file = open(self.output_path, "a")
        t = dt.datetime.now()
        line = str(t.year) + "-" + str(t.month) + "-" + str(t.day) + ";"
        line += "Levenshtein challenge;"
        line += name + ";"
        line += str(level) + ";"
        line += str(words) + ";"
        line += str(attempts[:level-1]) + "\n"
        file.write(line)
        file.close()
    
    #Printing Play()...
    def __str__(self):
        return "- Festival del ingenio Bot\n" + \
                "  I am the class in charge of games...\n" + \
                "  gitlab.com/rodrigovalla/festivaldelingeniobot\n" + \
                "  rodrigovalla@protonmail.ch"