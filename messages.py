import json as js

class Messages():
	"The class the bot use to know what to say..."

	def __init__(self):
		self.msg = js.load(open("messages_es.json"))

	#Returning a message from self.msg dictionary...
	def get_message(self, key):
		return self.msg[key]

	#Formating message with html <i> tag...
	def italic(self, m):
		return "<i>" + m + "</i>"

	#Formating message with html <b> tag...
	def bold(self, m):
		return "<b>" + m + "</b>"

	#Building the message to start a rebus challenge...
	def build_rebus_message(self, w):
		if w == "1":
			m = "<b>REBÚS:</b> " + w + " palabra"
		else:
			m = "<b>REBÚS:</b> " + w + " palabras"
		return m

	#Building the message to start an acertijo challenge...
	def build_acertijo_message(self, t, statement):
		m = "<b>ADIVINANZA</b>\n\n"
		m += "<i>" + statement + "</i>"
		return m

	#Building the message to send a hint...
	def build_hint_message(self, hint):
		m = "<b>Pista:</b> " + hint
		return m

	#Building congratulation message inviting the user to play again...
	def build_congrats_message(self, solution, type):
		m = self.get_message("good_answer") + "\n\n"
		m += "¿Quérés seguir? Mandá /" + type
		return m

	#Building the message to send when a challenge is ended...
	def build_end_challenge_message(self, solution, type):
		m = self.get_message("end_challenge") + "\n\n"
		m += "¿Quérés seguir? Mandá /" + type
		return m

	#Building the message to send the solution from a challenge...
	def build_solution_message(self, solution, type):
		m = "<b>Solución:</b> " + solution + "\n\n"
		m += "¿Quérés seguir? Mandá /" + type
		return m

	#Building the message to share a youtube video...
	def build_video_message(self, video_data):
		data = video_data.split(";")
		m = "Del <b>" + data[0] + " Festival del Ingenio</b>, elegí la charla de " + \
			"<b>" + data[2] + "</b>:" + "\n\n" + \
			"<b><a href='" + data[5] + "'>" + data[3] + "</a></b>\n" + \
			"<i>" + data[4] + "</i>"
		return m

	#The message triggered with /info command...
	def build_info_message(self):
		m = "El <b>Festival del Ingenio</b> es un encuentro para aprender y divertirse con acertijos, juegos, " + \
			"rompecabezas y magia. Lo hacemos para celebrar el ingenio de <b>Martin Gardner</b> y <b>Jaime Poniachik</b>. " + \
			"Podés enterarte de todas las novedades del festival en <a href='https://www.instagram.com/festivaldelingenio/'>" + \
			"Instagram</a>.\n\n" + \
			"Mi contenido incluye algunos palíndromos y acertijos populares pero también contenido original de varios " + \
			"autores: <b>Rodolfo Kurchan</b>, <b>Esteban Grinbank</b>.\n\n" + \
			"Mi administrador es @rvalla, escribile si me encontrás algún problema."
		return m

	#The message triggered with /help command...
	def build_help_message(self):
		m = "Podés pedirme distintas cosas. Acá te dejo mis comandos más divertidos:\n\n" + \
			"> Mandame /rebus o /acertijo para que te desafíe acá mismo\n" + \
			"> Mandame /palindromo para que te sorprenda con una oración que se lee al derecho y al revés\n" + \
			"> Mandame /reversible seguido de un número si querés ver un número escrito de manera reversible\n" + \
			"> Mandame /video si querés que comparta con vos un video de algunas de las charlas del festival"
		return m
