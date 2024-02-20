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
            m = self.bold(type + ": ") + w + " palabra"
        else:
            m = self.bold(type + ": ") + w + " palabras"
        return m

    #Building the message to start an acertijo challenge...
    def build_acertijo_message(self, t, statement):
        m = self.bold("ADIVINANZA") + "\n\n"
        m += self.italic(statement)
        return m

    #Building the message to send a hint...
    def build_hint_message(self, hint):
        m = self.bold("Pista: ") + hint
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
        m = self.bold("Solución: ") + solution + "\n"
        if not explanation == None:
            m += explanation + "\n\n"
        m += "¿Quérés seguir? Mandá /" + type
        return m

    #Building the message to start a firewall round...
    def build_start_firewall_message(self, ex_pass, ex_notpass):
        m = self.get_message("start_firewall")
        m += "El mensaje " + self.bold("| " + ex_pass + " | ") + " logra atravesar el " + self.italic("firewall") + \
            ".\nEn cambio, el mensaje " + self.bold("| " + ex_notpass + " | ") + "es bloqueado."
        return m

    #Building the message to answer a firewall move...
    def answer_firewall_message(self, correct, message, success, attempts):
        m = ""
        if correct:
            m = self.bold("| " + message.capitalize() + " | ")
            m += rd.choice(self.get_message("correct_firewall_answer").split(";"))
        else:
            m = rd.choice(self.get_message("wrong_firewall_answer").split(";"))
        m += "\n\nMensajes enviados: " + self.bold(str(success)) + "\nBloqueos restantes: " + self.bold(str(attempts))
        return m
    
    #Building hint firewall message...
    def hint_firewall_message(self, hint):
        m = self.bold("Pista: ") + hint
        return m
    
    #Building solution firewall message...
    def solution_firewall_message(self, solution):
        m = self.bold("Solución: ") + solution
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
    
    #Building level Levenshtein message...
    def new_leveshtein_level_message(self, tale, author, level):
        m1 = self.bold("Desafío de Levenshtein: NIVEL " + str(level))
        m2 = "Seleccioné una palabra del cuento "
        m2 += self.bold(tale) + " de " + self.bold(author) + ". ¿Podés encontrarla?"
        return m1, m2
    
    #Building Levenshtein hint message...
    def levenshtein_hint_message(self, hint):
        m = "Acá tenés una pista: <b>" + hint + "</b>."
        return m
    
    #Building Levenshtein move message...
    def levenshtein_move_message(self, word, distance, remaining_attempts):
        m = self.bold(word.capitalize()) + " está a distancia " + self.bold(str(distance)) + " de la palabra que buscás.\n"
        m += "Te quedan " + self.bold(str(remaining_attempts)) + " intentos."
        return m

    #Building Levenshtein words list...
    def levenshtein_played_words(self, words_list):
        m = "Durante esta partida te desafié con las siguientes palabras: "
        words_count = len(words_list)
        for i in range(words_count):
            m += words_list[i]
            if i < words_count - 1:
                m += ", "
            else:
                m += "."
        return m

    #Building the message to share a youtube video...
    def build_video_message(self, video_data):
        data = video_data.split(";")
        m = "Del " + self.bold(data[0] + " Festival del Ingenio") + ", elegí la charla de " + \
            self.bold(data[2]) + ":\n\n" + \
            self.bold("<a href='" + data[5] + "'>" + data[3] + "</a>\n") + \
            self.italic(data[4])
        return m

    #Building the message to confirm a game move...
    def build_minor_move_message(self, number, name):
        m = self.get_message("play_minor_number_move") + "\n"
        m += "Tu nombre: " + self.bold(name) + "\n"
        m += "Tu número: " + self.bold(str(number))
        return m

    #Building the message to inform a winner to the admin...
    def build_minor_game_message(self, winner_exist, number, winner):
        m = self.bold("Ronda del juego finalizada\n")
        if winner_exist:
            m += "El ganador de esta ronda es " + \
                self.bold(winner + " ") + \
                "con el número " + self.bold(number) + "."
        else:
            m += "DESIERTA"
        return m

    #Building the message to inform a victory...
    def build_minor_victory_message(self, number):
        m = self.get_message("play_minor_number_victory") + "\n" + \
            "Tu número ganador fue el " + self.bold(number) + "."
        return m

    #Building the message to inform a victory...
    def build_minor_loose_message(self, winner_exist, name, number):
        m = self.get_message("play_minor_number_loose") + "\n"
        if winner_exist:
            m += "Ganó " + self.bold(name) + "  con el número " + self.bold(number) + "."
        else:
            m += "Esta ronda quedó desierta. " + self.bold(name) + " jugó " + self.bold(number) + "."
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
            "> Mandame /firewall o /levenshtein para jugar un rato.\n" + \
			"> Mandame /palindromo para que te sorprenda con una oración que se lee al derecho y al revés.\n" + \
            "> Mandame /reversible seguido de un número si querés ver un número escrito de manera reversible.\n" + \
            "> Mandame /jugarmenor seguido de un número para participar de una ronda del <i>juego del menor número</i>.\n" + \
            "> Mandame /video si querés que comparta con vos un video de algunas de las charlas del festival.\n\n" + \
            "Podés mandarme /help seguido de <i>menor</i>, <i>promedio</i>, <i>firewall</i> o <i>levenshtein</i> si necesitás ayuda " + \
            "con alguno de esos juegos. También podés usar el comando /error para reportar cualquier falla que me encuentres."
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
                "ganás una ronda. ¡Me olvidaba! Tenés 15 oportunidades.\n\n" + \
                "Mandame /firewall y empezá a jugar."
        elif type == "levenshtein":
            m = "La <b>distancia de Levenshtein</b> mide la distancia entre dos palabras buscando cómo se pueden transformar una " + \
                "en la otra usando la mínima cantidad de operaciones posible. Considera 3 operaciones distintas y cada una suma 1.\n" + \
                "La <i>insersión</i> consiste en <i>insertar</i> una letra en la palabra (casa > ca<b>n</b>sa). " + \
                "La <i>eliminación</i> consiste en <i>eliminar</i> una letra (la<b>d</b>ro > lado). " + \
                "El <i>cambio</i> consiste en <i>cambiar</i> una letra por otra (<b>r</b>uta > <b>m</b>uta).\n" + \
                "Así la distancia entre <b>resto</b> y <b>estado</b> es 3 (resto > esto > estao > estado). Y la distancia entre " + \
                "libro y liebre es 2 (libro > liebro > liebre). Ver más en <a href='https://es.wikipedia.org/wiki/Distancia_de_Levenshtein'>wikipedia</a>.\n\n" + \
                "En el <b>Desafío de Levenshtein</b> yo elijo una palabra y vos intentás adivinarla. " + \
                "Tras cada intento lo único que te voy a decir es a qué <b>distancia</b> está tu palabra de la que yo elegí.\n\n" + \
                "Mandame /levenshtein y empezá a jugar."
        return m

    #Printing Messages()...
    def __str__(self):
        return "- Festival del ingenio Bot\n" + \
                "  I am the class in charge of formating text messages...\n" + \
                "  gitlab.com/rodrigovalla/festivaldelingeniobot\n" + \
                "  rodrigovalla@protonmail.ch"