import random as rd
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
	def build_rebus_message(self, type, w):
		if w == "1":
			m = "<b>"+ type + ":</b> " + w + " palabra"
		else:
			m = "<b>"+ type + ":</b> " + w + " palabras"
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
	def build_solution_message(self, solution, type, explanation):
		m = "<b>Solución:</b> " + solution + "\n"
		if not explanation == None:
			m += explanation + "\n\n"
		m += "¿Quérés seguir? Mandá /" + type
		return m

	#Building the message to start a firewall round...
	def build_start_firewall_message(self, ex_pass, ex_notpass):
		m = self.get_message("start_firewall")
		m += "El mensaje <b>&lt;&lt;" + ex_pass + "&gt;&gt;</b> logra atravesar el <i>firewall</i>. En cambio, " + \
			"el mensaje <b>&lt;&lt;" + ex_notpass + "&gt;&gt;</b> es bloqueado."
		return m

	#Building the message to answer a firewall move...
	def answer_firewall_message(self, correct, message):
		m = ""
		if correct:
			m = "<b>&lt;&lt;" + message.capitalize() + "&gt;&gt;</b> "
			m += rd.choice(self.get_message("correct_firewall_answer").split(";"))
		else:
			m = rd.choice(self.get_message("wrong_firewall_answer").split(";"))
		return m

	#Building end firewall message...
	def end_firewall_message(self, victory, command):
		m = ""
		if victory:
			m = self.get_message("firewall_victory")
		else:
			m = self.get_message("firewall_defeat")
		m += "\n\n"
		m += "¿Quérés seguir? Mandá /" + command
		return m

	#Building the message to share a youtube video...
	def build_video_message(self, video_data):
		data = video_data.split(";")
		m = "Del <b>" + data[0] + " Festival del Ingenio</b>, elegí la charla de " + \
			"<b>" + data[2] + "</b>:" + "\n\n" + \
			"<b><a href='" + data[5] + "'>" + data[3] + "</a></b>\n" + \
			"<i>" + data[4] + "</i>"
		return m

	#Building the message to confirm a game move...
	def build_minor_move_message(self, number, name):
		m = self.get_message("play_minor_number_move") + "\n"
		m += "Tu nombre: <b>" + name + "</b>\n"
		m += "Tu número: <b>" + str(number) + "</b>"
		return m

	#Building the message to inform a winner to the admin...
	def build_minor_game_message(self, winner_exist, number, winner):
		m = "<b>Ronda del juego finalizada</b>\n"
		if winner_exist:
			m += "El ganador de esta ronda es " + \
				"<b>" + winner + "</b> " + \
				"con el número <b>" + number + "</b>"
		else:
			m += "DESIERTA"
		return m

	#Building the message to inform a victory...
	def build_minor_victory_message(self, number):
		m = self.get_message("play_minor_number_victory") + "\n" + \
			"Tu número ganador fue el <b>" + number + "</b>."
		return m

	#Building the message to inform a victory...
	def build_minor_loose_message(self, winner_exist, name, number):
		m = self.get_message("play_minor_number_loose") + "\n"
		if winner_exist:
			m += "Ganó <b>" + name + "</b> con el número <b>" + number + "</b>"
		else:
			m += "Esta ronda quedó desierta. <b>" + name + "</b> jugó <b>" + number + "</b>."
		return m

	#The message triggered with /info command...
	def build_info_message(self):
		m = "El <b>Festival del Ingenio</b> es un encuentro para aprender y divertirse con acertijos, juegos, " + \
			"rompecabezas y magia. Lo hacemos para celebrar el ingenio de <b>Martin Gardner</b> y <b>Jaime Poniachik</b>. " + \
			"Podés enterarte de todas las novedades del festival en <a href='https://www.instagram.com/festivaldelingenio/'>" + \
			"Instagram</a>.\n\n" + \
			"Mi contenido incluye algunos palíndromos y acertijos populares pero también contenido original de " + \
			"<b>Rodolfo Kurchan</b>, <b>Esteban Grinbank</b> y <b>Los Columnerds</b>.\n\n" + \
			"Mi administrador es @rvalla, escribile si me encontrás algún problema."
		return m

	#The message triggered with /help command...
	def build_help_message(self):
		m = "Podés pedirme distintas cosas. Acá te dejo mis comandos más divertidos:\n\n" + \
			"> Mandame /rebus o /acertijo para que te desafíe acá mismo.\n" + \
			"> Mandame /palindromo para que te sorprenda con una oración que se lee al derecho y al revés.\n" + \
			"> Mandame /reversible seguido de un número si querés ver un número escrito de manera reversible.\n" + \
			"> Mandame /jugarmenor seguido de un número para participar de una ronda del <i>juego del menor número</i>.\n" + \
			"> Mandame /video si querés que comparta con vos un video de algunas de las charlas del festival.\n\n" + \
			"Podés mandarme /help seguido de <i>menor</i>, <i>promedio</i> o <i>firewall</i> si necesitás ayuda " + \
			"con alguno de esos juegos."
		return m

	#The message triggered with /help custom command...
	def build_custom_help_message(self, type):
		m = "No tengo ninguna ayuda especial para el argumento " + type + "."
		if type == "menor":
			m = "Para jugar una ronda del <b>juego del menor número</b> tenés que mandarme:\n" + \
				"/jugar n (n es un número natural).\n" + \
				"Cuando un <i>administrador</i> decide dar por finalizada una ronda yo te voy a mandar un mensaje. " + \
				"Gana el jugador que haya enviado el menor número que haya sido único.\n\nEjemplo: " + \
				"Juan manda el 5, Camila manda el 3, Martín manda el 6, Susana manda el 5 y Jorge manda el 3. " + \
				"Gana Martín, porque el 6 es el menor número enviado una única vez.\n" + \
				"Espero tu jugada. ¡Suerte!"
		elif type == "promedio":
			m = "Perdón pero aún no implementé este juego. En realidad es mi programador quien lo tiene que hacer."
		elif type == "firewall":
			m = "No necesitás compañía para jugar al <b>firewall</b>. La idea es que existe, mientras dura el juego, " + \
				"un <i>firewall</i> que deja pasar sólo algunos de los mensajes que me enviás. Tenés que descubrir " + \
				"qué condición cumplen los mensajes que sí pasan. Si lográs pasar a través del <i>firewall</i> 5 mensajes " + \
				"ganás una ronda. ¡Me olvidaba! Tenés 15 oportunidades.\n" + \
				"Mandame /firewall y empezá a jugar."
		return m
