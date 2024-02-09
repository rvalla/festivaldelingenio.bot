import datetime as dt

class Usage():
	"The class to save usage data..."

	def __init__(self, usage_path, errors_path):
		self.output_path = usage_path
		self.errors_path = errors_path
		self.reset()

	#Resseting data variables...
	def reset(self):
		self.last_save = dt.datetime.now() #the start up time...
		self.start = 0
		self.rebus = [0,0,0,0,0] #count, victory, loose, solution, cancelled
		self.acertijo = [0,0,0,0,0] #count, victory, loose, solution, cancelled
		self.firewall = [0,0,0,0,0] #count, victory, loose, cheated, cancelled
		self.levenshtein = [0,0,0,0,0] #count, level_victory, victory, loose, cancelled
		self.jugarmenor = 0
		self.jugarpromedio = 0
		self.palindromo = 0
		self.reversible = 0
		self.video = 0
		self.help = [0,0,0,0] #help, minor, average, firewall
		self.info = 0
		self.wrong_message = 0
		self.error_reports = 0
		self.errors = 0

	#Building usage information message...
	def build_usage_message(self):
		m = "<b>Datos de uso:</b>" + "\n" + \
			"start: " + str(self.start) + "\n" + \
			"rebus: " + str(self.rebus) + "\n" + \
			"acertijo: " + str(self.acertijo) + "\n" + \
			"firewall: " + str(self.firewall) + "\n" + \
			"levenshtein: " + str(self.levenshtein) + "\n" + \
			"jugarmenor: " + str(self.jugarmenor) + "\n" + \
			"jugarpromedio: " + str(self.jugarpromedio) + "\n" + \
			"palindromo: " + str(self.palindromo) + "\n" + \
			"reversible: " + str(self.reversible) + "\n" + \
			"video: " + str(self.video) + "\n" + \
			"help: " + str(self.help) + "\n" + \
			"info: " + str(self.info) + "\n" + \
			"wrong_message: " + str(self.wrong_message) + "\n" \
			"error reports: " + str(self.error_reports) + "\n" \
			"errors: " + str(self.errors)
		return m

	#Saving usage to file...
	def save_usage(self):
		file = open(self.output_path, "a")
		t = dt.datetime.now()
		i = t - self.last_save
		date = str(t.year) + "-" + str(t.month) + "-" + str(t.day)
		interval = str(i).split(".")[0]
		line = self.build_usage_line(date, interval)
		file.write(line)
		file.close()
		self.reset()

	#Building a data line to save...
	def build_usage_line(self, date, interval):
		line = date + ";"
		line += interval + ";"
		line += str(self.start) + ";"
		line += str(self.rebus) + ";"
		line += str(self.acertijo) + ";"
		line += str(self.firewall) + ";"
		line += str(self.levenshtein) + ";"
		line += str(self.jugarmenor) + ";"
		line += str(self.jugarpromedio) + ";"
		line += str(self.palindromo) + ";"
		line += str(self.reversible) + ";"
		line += str(self.video) + ";"
		line += str(self.help) + ";"
		line += str(self.info) + ";"
		line += str(self.wrong_message) + ";"
		line += str(self.error_reports) + ";"
		line += str(self.errors) + "\n"
		return line

	#Registering a new start command...
	def add_start(self):
		self.start += 1

	#Registering a new challenge...
	def add_challenge(self, end, command):
		if command == "rebus":
			self.rebus[0] += 1
			self.rebus[end] += 1
		elif command == "acertijo":
			self.acertijo[0] += 1
			self.acertijo[end] += 1
		elif command == "firewall":
			self.firewall[0] += 1
			self.firewall[end] += 1
		elif command == "levenshtein":
			self.levenshtein[0] += 1
			self.levenshtein[end] += 1

	#Registering a Levenshtein change:
	def add_levenshtein(self, key):
		self.levenshtein[key] += 1

	#Registering a new minor game move...
	def add_jugarmenor(self):
		self.jugarmenor += 1

	#Registering a new average game move...
	def add_jugarpromedio(self):
		self.jugarpromedio += 1

	#Registering a new palindromo command...
	def add_palindromo(self):
		self.palindromo += 1

	#Registering a new reversible command...
	def add_reversible(self):
		self.reversible += 1

	#Registering a new video command...
	def add_video(self):
		self.video += 1

	#Registering a new help command...
	def add_help(self, type):
		if type == "menor":
			self.help[1] += 1
		elif type == "promedio":
			self.help[2] += 1
		elif type == "firewall":
			self.help[3] += 1
		else:
			self.help[0] += 1

	#Registering a new info command...
	def add_info(self):
		self.info += 1

	#Registering a messege out of context...
	def add_wrong_message(self):
		self.wrong_message += 1
	
	#Registering a new error report...
	def add_error_report(self):
		self.error_reports += 1
	
	#Saving en error report...
	def save_error_report(self, command, description, user):
		file = open(self.errors_path, "a")
		t = dt.datetime.now()
		date = str(t.year) + "-" + str(t.month) + "-" + str(t.day)
		file.write(date)
		file.write(command)
		file.write(description)
		file.write(user + "\n")
		file.close()

	#Printing Usage()...
	def __str__(self):
		return "- Festival del ingenio Bot\n" + \
				"  I am the class in charge of working with usage data...\n" + \
				"  gitlab.com/rodrigovalla/festivaldelingeniobot\n" + \
				"  rodrigovalla@protonmail.ch"