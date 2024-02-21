from telegram.ext import (
			Application, InlineQueryHandler, CommandHandler,
			CallbackQueryHandler, ContextTypes, ConversationHandler,
			MessageHandler, filters
)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
import traceback, logging
import json as js
from usage import Usage
from messages import Messages
from assets import Assets
from play import Play
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

#Filterint warnings about conversation handlers configuration...
filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

logger = logging.getLogger(__name__)
config = js.load(open("config.json")) #The configuration .json file (token included)
us = Usage("usage.csv", "errors.csv") #The class to store usage data...
msg = Messages() #The class which knows what to say...
ass = Assets() #The class to access the different persistent assets...
pl = Play("games.csv") #The class to let the users play some game...
FIREWALL_L, TRYING, FIREWALL, LEVENSHTEIN, ERROR_1, ERROR_2 = range(6) #Conversation states...
rebus_keys = ["command", "type","animated","words","solution","explanation","hint","file_id","path"] #Keys to load rebus data...
acertijo_keys = ["command", "type","words","solution_type","statement","solution","explanation","hint"] #Keys to load acertijo data...
firewall_keys = ["command", "type"]
attempts_limit = 2 #Defining the number of attempts before ending a challenge...
firewall_limits = [5, 13] #Defining victory-loose limits for firewall game...
levenshtein_limits = [8, 10] #Number of attempts for level 1, Number of levels...
vowelsa, vowelsb = "áéíóúü", "aeiouu" #Mapping special characters to check sent solutions...
translation = str.maketrans(vowelsa, vowelsb)

#Starting the chat with a new user...
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	id = update.effective_chat.id
	logging.info(hide_id(id) + " started the bot...")
	us.add_start()
	m = msg.get_message("hello") + "\n\n" + msg.get_message("hello2")
	await context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)

#Starting an acertijo challenge...
async def start_acertijo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	id = update.effective_chat.id
	load_challenge(context.chat_data, ass.get_acertijo_data(), acertijo_keys)
	await context.bot.send_message(chat_id=id, text=msg.get_message("start_challenge"), parse_mode=ParseMode.HTML)
	await context.bot.send_message(chat_id=id, text=msg.build_acertijo_message(context.chat_data["solution_type"], context.chat_data["statement"]), parse_mode=ParseMode.HTML)
	return TRYING

#Starting rebus challenge...
async def start_rebus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	id = update.effective_chat.id
	load_challenge(context.chat_data, ass.get_rebus_data(), rebus_keys)
	await context.bot.send_message(chat_id=id, text=msg.get_message("start_challenge"), parse_mode=ParseMode.HTML)
	await context.bot.send_message(chat_id=id, text=msg.build_rebus_message(context.chat_data["type"], context.chat_data["words"]), parse_mode=ParseMode.HTML)
	try:
		await send_image(context, context.chat_data["animated"], id, context.chat_data["file_id"])
		return TRYING #Entering TRYING state if image was sent succesfully...
	except:
		logging.info("Error: It was imposible to send the image")
		await context.bot.send_message(chat_id=id, text=msg.get_message("error"), parse_mode=ParseMode.HTML)
		return ConversationHandler.END #Ending challenge if image was not sent...

#Sending images and animations...
async def send_image(context: ContextTypes.DEFAULT_TYPE, animated: bool, id: int, file_id: int) -> None:
	if animated == "True":
		await context.bot.send_animation(chat_id=id, animation=file_id)
	else:
		await context.bot.send_photo(chat_id=id, photo=file_id)

#Loading challenge data to CallbackContext
def load_challenge(chat_data, rebus, keys):
	data = rebus.split(";")
	for r, k in zip(data, keys):
		chat_data[k] = r
	chat_data["attempts"] = 0 #Saving number of attempsts...
	chat_data["saw_hint"] = False #A field to know if the user asded for a hint...

#TRYING state check the answers sent by the user...
async def check_try(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	id = update.effective_chat.id
	if is_correct_answer(update.message.text, context.chat_data["solution"], int(context.chat_data["words"])):
		await send_congrats(update, context)
		return ConversationHandler.END #Ending challenge after user succeded...
	else:
		if context.chat_data["attempts"] < attempts_limit:
			context.chat_data["attempts"] += 1
			if context.chat_data["saw_hint"] == False: #Deciding what buttons to send...
				keyboard = [[InlineKeyboardButton(text="Pista", callback_data="hint"),
							InlineKeyboardButton(text="Solución", callback_data="solution")]]
			else:
				keyboard = [[InlineKeyboardButton(text="Solución", callback_data="solution")]]
			reply = InlineKeyboardMarkup(keyboard)
			await context.bot.send_message(chat_id=id, text=msg.get_message("bad_answer"), reply_markup=reply, parse_mode=ParseMode.HTML)
		else:
			await context.bot.send_sticker(chat_id=id, sticker=ass.get_sticker_id(2))
			await end_challenge(update, context)
			return ConversationHandler.END #Ending a challenge after attempts limit...

#Checking if an answer is correct...
def is_correct_answer(message, solution, solution_words):
	input = message.lower().translate(translation)
	solution = solution.lower().translate(translation) #The strings to compare haven't got special characters...
	is_correct = False
	if solution_words == 1:
		input_w = input.split(" ") #Al words sent by the user will be evaluated...
		for w in input_w:
			if w == solution:
				is_correct = True
				break
	else:
		if input == solution:
			is_correct = True
	return is_correct

#Sending congratulation message...
async def send_congrats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	id = update.effective_chat.id
	us.add_challenge(1, context.chat_data["command"])
	if context.chat_data["saw_hint"] == False:
		await context.bot.send_sticker(chat_id=id, sticker=ass.get_sticker_id(0))
	m = msg.build_congrats_message("good_answer", context.chat_data["command"])
	await context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)
	context.chat_data.clear()

#Sending the challenge's hint...
async def send_hint(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	id = update.effective_chat.id
	m = msg.build_hint_message(context.chat_data["hint"])
	await context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)
	await context.bot.send_sticker(chat_id=id, sticker=ass.get_sticker_id(1))
	context.chat_data["saw_hint"] = True

#Sending the solution from a challenge...
async def send_solution(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	id = update.effective_chat.id
	us.add_challenge(3, context.chat_data["command"])
	m = msg.build_solution_message(context.chat_data["solution"], context.chat_data["command"], context.chat_data["explanation"])
	await context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)
	if context.chat_data["saw_hint"] == False:
		await context.bot.send_sticker(chat_id=id, sticker=ass.get_sticker_id(1))
	context.chat_data.clear()

#Ending a challenge...
async def end_challenge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	us.add_challenge(2, context.chat_data["command"])
	m = msg.build_end_challenge_message("end_challenge", context.chat_data["command"])
	await context.bot.send_message(chat_id=update.effective_chat.id, text=m, parse_mode=ParseMode.HTML)
	context.chat_data.clear()
	return ConversationHandler.END

#Canceling the challenge without offering another one...
async def cancel_challenge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	us.add_challenge(4, context.chat_data["command"])
	m = msg.get_message("end_challenge")
	await context.bot.send_message(chat_id=update.effective_chat.id, text=m, parse_mode=ParseMode.HTML)
	context.chat_data.clear()
	return ConversationHandler.END

#Selecting firewall difficulty and starting challenge...
async def selecting_firewall(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	id = update.effective_chat.id
	context.chat_data["command"] = "firewall"
	keyboard = [[InlineKeyboardButton(text="Fácil", callback_data="firewall_0"),
				InlineKeyboardButton(text="Difícil", callback_data="firewall_1"),
				InlineKeyboardButton(text="Durísimo", callback_data="firewall_2")]]
	reply = InlineKeyboardMarkup(keyboard)
	await context.bot.send_message(chat_id=id, text=msg.get_message("present_firewall"), reply_markup=reply, parse_mode=ParseMode.HTML)
	return FIREWALL_L

#Starting a firewall game round...
async def start_firewall(update: Update, context: ContextTypes.DEFAULT_TYPE, difficulty: int) -> None:
	id = update.effective_chat.id
	load_firewall(context.chat_data, difficulty)
	m = msg.build_start_firewall_message(context.chat_data["ex_pass"], context.chat_data["ex_notpass"])
	keyboard = [[InlineKeyboardButton(text="Pista", callback_data="fw_0"),
				InlineKeyboardButton(text="Solución", callback_data="fw_1")]]
	reply = InlineKeyboardMarkup(keyboard)
	await context.bot.send_message(chat_id=id, text=m, reply_markup=reply, parse_mode=ParseMode.HTML)

#Checking a firewall move...
async def check_firewall(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	id = update.effective_chat.id
	input = update.message.text.lower().translate(translation)
	if input not in context.chat_data["moves"]:
		success = trough_firewall(input, context.chat_data)
		if success:
			context.chat_data["success"] += 1
			context.chat_data["moves"].add(input)
		else:
			context.chat_data["attempts"] -= 1
		m = msg.answer_firewall_message(success, input, context.chat_data["success"], context.chat_data["attempts"])
		await context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)
		if context.chat_data["success"] == firewall_limits[0]:
			await end_firewall_game(update, context, True)
			return ConversationHandler.END
		elif context.chat_data["attempts"] < 1:
			await end_firewall_game(update, context, False)
			return ConversationHandler.END
	else:
		await firewall_cheat_detected(update, context)
		return ConversationHandler.END

#Deciding if a message pass trough the firewall...
def trough_firewall(message, chat_data):
	return pl.check_firewall(chat_data["algorithm"], message, chat_data["parameters"])

#Ending a firewall game...
async def end_firewall_game(update: Update, context: ContextTypes.DEFAULT_TYPE, victory: bool) -> None:
	id = update.effective_chat.id
	logging.info(hide_id(id) + " ended a firewall game: " + str(victory))
	m = msg.end_firewall_message(victory, context.chat_data["command"])
	u = None
	if victory:
		sticker = ass.get_sticker_id(0)
		u = 1
	else:
		sticker = ass.get_sticker_id(2)
		u = 2
	us.add_challenge(u, context.chat_data["command"])
	await context.bot.send_sticker(chat_id=id, sticker=sticker)
	await context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)
	context.chat_data.clear()

#Ending a firewall game because the user cheated...
async def firewall_cheat_detected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	id = update.effective_chat.id
	us.add_challenge(3, context.chat_data["command"])
	logging.info(hide_id(id) + " ended a firewall game: CHEAT")
	await context.bot.send_message(chat_id=id, text=msg.get_message("firewall_cheat"), parse_mode=ParseMode.HTML)
	await context.bot.send_sticker(chat_id=id, sticker=ass.get_sticker_id(3))
	context.chat_data.clear()

#Loading firewall round data...
def load_firewall(chat_data, difficulty):
	firewall = pl.get_firewall_game(difficulty)
	keys = list(firewall)
	for k in keys:
		chat_data[k] = firewall[k]
	chat_data["attempts"] = firewall_limits[1]
	chat_data["success"] = 0
	chat_data["saw_hint"] = False
	chat_data["moves"] = set()
	chat_data["moves"].add(chat_data["ex_pass"])

#Sending a firewall hint...
async def firewall_hint(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	id = update.effective_chat.id
	context.chat_data["saw_hint"] = True
	m = msg.hint_firewall_message(context.chat_data["hint"])
	await context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)
	await context.bot.send_sticker(chat_id=id, sticker=ass.get_sticker_id(1))
	return FIREWALL

#Sending a firewall solution...
async def firewall_solution(update: Update, context: ContextTypes.DEFAULT_TYPE)-> int:
	id = update.effective_chat.id
	m = msg.solution_firewall_message(context.chat_data["solution"])
	await context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)
	if context.chat_data["saw_hint"] == False:
		await context.bot.send_sticker(chat_id=id, sticker=ass.get_sticker_id(1))
	m = msg.end_firewall_message(False, context.chat_data["command"])
	await context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)
	context.chat_data.clear()
	return ConversationHandler.END

#Starting a Levenshtein game...
async def start_leveshtein(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	id = update.effective_chat.id
	context.chat_data["command"] = "levenshtein"
	context.chat_data["words"] = []
	await context.bot.send_message(chat_id=id, text=msg.get_message("start_levenshtein"), parse_mode=ParseMode.HTML)
	await start_levenshtein_level(id, context, 1)
	return LEVENSHTEIN

#Starting a Levenshtein level...
async def start_levenshtein_level(id: int, context: ContextTypes.DEFAULT_TYPE, level: int) -> None:
	load_levenshtein(context.chat_data, level)
	m1, m2 = msg.new_leveshtein_level_message(context.chat_data["tale"], context.chat_data["author"], level)
	keyboard = [[InlineKeyboardButton(text="Pista", callback_data="levenshtein_0"),
				InlineKeyboardButton(text="Súper Pista", callback_data="levenshtein_1")]]
	reply = InlineKeyboardMarkup(keyboard)
	await context.bot.send_message(chat_id=id, text=m1, parse_mode=ParseMode.HTML)
	await context.bot.send_message(chat_id=id, text=m2, reply_markup=reply, parse_mode=ParseMode.HTML)

#Checking a levenshtein move...
async def check_levenshtein(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	id = update.effective_chat.id
	move = update.message.text.lower()
	context.chat_data["attempts"] += 1
	distance = pl.distance(move, context.chat_data["word"])
	if distance == 0:
		if context.chat_data["level"] == levenshtein_limits[1]:
			await context.bot.send_message(chat_id=id, text=msg.levenshtein_played_words(context.chat_data["words"]), parse_mode=ParseMode.HTML)
			await context.bot.send_message(chat_id=id, text=msg.get_message("levenshtein_final_victory"), parse_mode=ParseMode.HTML)
			await context.bot.send_sticker(chat_id=id, sticker=ass.get_sticker_id(0))
			us.add_levenshtein(0)
			us.add_levenshtein(2)
			name = build_user_name(update)
			context.chat_data["attempts_history"][levenshtein_limits[1]-1] = context.chat_data["attempts"] 
			pl.save_levenshtein(name, context.chat_data["level"], context.chat_data["words"], context.chat_data["attempts_history"])
			return ConversationHandler.END
		else:
			await context.bot.send_message(chat_id=id, text=msg.get_message("levenshtein_level_victory"), parse_mode=ParseMode.HTML)
			await start_levenshtein_level(id, context, context.chat_data["level"] + 1)
			us.add_levenshtein(1)
			return LEVENSHTEIN
	else:
		if context.chat_data["attempts"] < context.chat_data["loose_time"]: 
			m = msg.levenshtein_move_message(move, distance, context.chat_data["loose_time"] - context.chat_data["attempts"])
			await context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)
			return LEVENSHTEIN
		else:
			await context.bot.send_message(chat_id=id, text=msg.levenshtein_played_words(context.chat_data["words"]), parse_mode=ParseMode.HTML)
			await context.bot.send_message(chat_id=id, text=msg.get_message("levenshtein_final_loose"), parse_mode=ParseMode.HTML)
			await context.bot.send_sticker(chat_id=id, sticker=ass.get_sticker_id(2))
			us.add_levenshtein(0)
			us.add_levenshtein(3)
			name = build_user_name(update)
			pl.save_levenshtein(name, context.chat_data["level"], context.chat_data["words"], context.chat_data["attempts_history"])
			return ConversationHandler.END

#Sending a levenshtein hint...
async def levenshtein_hint(update: Update, context: ContextTypes.DEFAULT_TYPE, hint_type: int) -> int:
	id = update.effective_chat.id
	m = ""
	if hint_type == 0:
		if context.chat_data["letter"] == 1:
			m = msg.get_message("levenshtein_hint_refuse")
		else:
			m = msg.levenshtein_hint_message(pl.levenshtein_letter(context.chat_data["word"]))
		context.chat_data["letter"] += 1
	elif hint_type == 1:
		if context.chat_data["hint"] == 1:
			m = msg.get_message("levenshtein_hint_refuse")
		else:
			m = msg.levenshtein_hint_message(pl.levenshtein_hint(context.chat_data["word"]))
		context.chat_data["hint"] += 1
	await context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)
	return LEVENSHTEIN

#Loading levenshtein round data...
def load_levenshtein(chat_data, level):
	tale, author, word = pl.levenshtein_word(level)
	chat_data["level"] = level
	chat_data["author"] = author
	chat_data["tale"] = tale
	chat_data["word"] = word
	chat_data["loose_time"] = levenshtein_limits[0] + (level- 1) * 2
	chat_data["hint"] = 0
	chat_data["letter"] = 0
	chat_data["words"].append(word)
	if level == 1:
		chat_data["attempts_history"] = [0 for i in range(10)]
	else: 
		chat_data["attempts_history"][level-2] = chat_data["attempts"]
	chat_data["attempts"] = 0

#Sending a palindromo for the user...
async def send_palindromo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	id = update.effective_chat.id
	us.add_palindromo()
	await context.bot.send_message(chat_id=id, text=msg.get_message("palindromo"), parse_mode=ParseMode.HTML)
	await context.bot.send_message(chat_id=id, text=msg.italic(ass.get_palindromo()), parse_mode=ParseMode.HTML)

#Sending a reverse number...
async def send_reverse_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	id = update.effective_chat.id
	in_m = update.message.text.split(" ")
	us.add_reversible()
	if len(in_m) > 1:
		try:
			n = int(in_m[1])
			data = ass.get_reverse_number(n).split(";")
			m = msg.get_message("reverse_number") + "\n\n"
			m += msg.bold(data[1])
			await context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)
			await context.bot.send_photo(chat_id=id, photo=data[2])
		except:
			await context.bot.send_message(chat_id=id, text=msg.get_message("reverse_error"), parse_mode=ParseMode.HTML)
	else:
		data = ass.get_random_reverse_number().split(";")
		m = msg.get_message("reverse_number") + "\n\n"
		m += msg.bold(data[1])
		await context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)
		await context.bot.send_photo(chat_id=id, photo=data[2])

#Sendind a video from the youtube chanel...
async def send_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	id = update.effective_chat.id
	us.add_video()
	await context.bot.send_message(chat_id=id, text=msg.build_video_message(ass.get_video_data()), parse_mode=ParseMode.HTML)

#Using the bot to play a live game...
async def save_minor_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	id = update.effective_chat.id
	m = update.message.text.split(" ")
	if len(m) == 2:
		try:
			number = int(m[1]) #First we check if the user sent us a number
			if number > 0:
				name = build_user_name(update)
				us.add_jugarmenor()
				if pl.save_minor_number(number, name, id): #Saving a move... Returns False if the player played before in the round...
					await context.bot.send_message(chat_id=id, text=msg.build_minor_move_message(number, name), parse_mode=ParseMode.HTML)
				else:
					await context.bot.send_message(chat_id=id, text=msg.get_message("play_double_move"), parse_mode=ParseMode.HTML)
			else:
				await failed_minor_number(context, id)
		except:
			await failed_minor_number(context, id)
	else:
		await failed_minor_number(context, id)

#Notifying the user of a wrong game move...
async def failed_minor_number(context: ContextTypes.DEFAULT_TYPE, id: int) -> None:
	logging.info(hide_id(id) + " failed to play a minor number move...")
	await context.bot.send_message(chat_id=id, text=msg.get_message("play_minor_number_move_error"), parse_mode=ParseMode.HTML)

#Ending a game round...
async def end_minor_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	id = update.effective_chat.id
	m = update.message.text.split(" ")
	if len(m) > 1 and m[1] == config["password"]:
		winner_exist, number, winner, winner_id = pl.end_minor_game()
		logging.info(hide_id(id) + " ending a minor game round...")
		end_m = pl.minor_info() + "\n\n" + \
				msg.build_minor_game_message(winner_exist, number, winner)
		await context.bot.send_message(chat_id=id, text=end_m, parse_mode=ParseMode.HTML)
		try:
			if winner_exist:
				await context.bot.send_message(chat_id=winner_id, text=msg.build_minor_victory_message(number), parse_mode=ParseMode.HTML)
				await context.bot.send_sticker(chat_id=winner_id, sticker=ass.get_sticker_id(0))
				logging.info("Game round victory notification sent")
			loosers = pl.get_minor_loosers(winner_id)
			looser_message = msg.build_minor_loose_message(winner_exist, winner, number)
			logging.info("Notifying loosers of a minor game round")
			for l in loosers:
				await context.bot.send_message(chat_id=l, text=looser_message, parse_mode=ParseMode.HTML)
				await context.bot.send_sticker(chat_id=l, sticker=ass.get_sticker_id(2))
		except:
			logging.info("Problems during game round notifications.")
		pl.save_minor(winner, number)
		pl.minor_reset()
	else:
		logging.info(hide_id(id) + " wanted to end a game round without the password...")
		await context.bot.send_message(chat_id=id, text=msg.get_message("intruder"), parse_mode=ParseMode.HTML)

#Sending game current state...
async def minor_number_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	id = update.effective_chat.id
	m = update.message.text.split(" ")
	if len(m) > 1 and m[1] == config["password"]:
		m = pl.minor_info()
		await context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)
	else:
		logging.info(hide_id(id) + " wanted to check a game round state...")
		await context.bot.send_message(chat_id=id, text=msg.get_message("intruder"), parse_mode=ParseMode.HTML)

#Building a user or chat name...
def build_user_name(update):
	fn = update.effective_chat.first_name
	ln = update.effective_chat.last_name
	gn = update.effective_chat.title
	if not gn == None:
		name = gn + " (grupo)" #Saving the group title in case the chat is a group
	else:
		try:
			name = fn + " " + ln #Saving first_name + last_name in case last_name is not None
		except:
			name = fn
	return name

#Triggering /help command...
async def print_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	id = update.effective_chat.id
	m = update.message.text.split(" ")
	if len(m) == 2:
		selection = m[1].lower().translate(translation)
		us.add_help(selection)
		await context.bot.send_message(chat_id=id, text=msg.build_custom_help_message(selection), disable_web_page_preview=True, parse_mode=ParseMode.HTML)
	else:
		us.add_help(None)
		keyboard = [[InlineKeyboardButton(text="Firewall", callback_data="help_firewall"),
					InlineKeyboardButton(text="Levenshtein", callback_data="help_levenshtein")],
					[InlineKeyboardButton(text="Menor número", callback_data="help_menor"),
					InlineKeyboardButton(text="Promedio", callback_data="help_promedio")]]
		reply = InlineKeyboardMarkup(keyboard)
		await context.bot.send_message(chat_id=id, text=msg.build_help_message(), reply_markup=reply, parse_mode=ParseMode.HTML)

#Triggering /info command...
async def print_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	id = update.effective_chat.id
	us.add_info()
	await context.bot.send_message(chat_id=id, text=msg.build_info_message(), parse_mode=ParseMode.HTML)

#Starting an error report session...
async def trigger_error_submit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	id = update.effective_chat.id
	logging.info(str(hide_id(id)) + " wants to report an error...")
	context.chat_data["command"] = "error"
	await context.bot.send_message(chat_id=id, text=msg.get_message("submit_error_1"), parse_mode=ParseMode.HTML)
	return ERROR_1

#Saving error related command...
async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	id = update.effective_chat.id
	m = update.message.text
	context.chat_data["error_command"] = m
	await context.bot.send_message(chat_id=id, text=msg.get_message("submit_error_2"), parse_mode=ParseMode.HTML)
	return ERROR_2

#Saving error description...
async def report_error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	id = update.effective_chat.id
	m = context.chat_data["error_command"]
	m2 = update.message.text
	context.chat_data["error_description"] = m2
	us.add_error_report()
	us.save_error_report(m, m2, str(hide_id(id)))
	admin_msg = "Error reported:\n-command: /" + m + "\n-description: " + m2
	await context.bot.send_message(chat_id=config["admin_id"], text=admin_msg, parse_mode=ParseMode.HTML)
	await context.bot.send_message(chat_id=id, text=msg.get_message("submit_error_3"), parse_mode=ParseMode.HTML)
	return ConversationHandler.END

#Answering a text message out of any conversation...
async def wrong_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	if update.message.reply_to_message == None:
		id = update.effective_chat.id
		us.add_wrong_message()
		await context.bot.send_message(chat_id=id, text=msg.get_message("wrong"), parse_mode=ParseMode.HTML)

#Deciding what function to trigger after a button click...
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	id = update.effective_chat.id
	query = update.callback_query
	await query.answer()
	if query.data.startswith("help"):
		selection = query.data.split("_")[1]
		us.add_help(selection)
		await context.bot.send_message(chat_id=id, text=msg.build_custom_help_message(selection), disable_web_page_preview=True, parse_mode=ParseMode.HTML)

#Deciding what function to trigger after a button click in a conversation...
async def conversation_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	query = update.callback_query
	await query.answer()
	if query.data == "hint":
		await send_hint(update, context)
		return TRYING
	elif query.data == "solution":
		await send_solution(update, context)
		return ConversationHandler.END
	elif query.data.startswith("firewall"):
		d = int(query.data.split("_")[1])
		await start_firewall(update, context, d)
		return FIREWALL
	elif query.data.startswith("fw"):
		d = int(query.data.split("_")[1])
		if d == 0 and context.chat_data["saw_hint"] == False:
			await firewall_hint(update, context)
			return FIREWALL
		elif d == 1:
			await firewall_solution(update, context)
			return ConversationHandler.END
	elif query.data.startswith("levenshtein"):
		d = int(query.data.split("_")[1])
		await levenshtein_hint(update, context, d)
		return LEVENSHTEIN

#Sending a message to bot admin when an error occur...
async def error_notification(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	id = update.effective_chat.id
	m = "An error ocurred! While comunicating with chat " + hide_id(id)
	logging.info(m)
	await context.bot.send_message(chat_id=config["admin_id"], text=m, parse_mode=ParseMode.HTML)

def print_photo_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	print("///////")
	print(update.message.photo[0]["file_id"] + ";")

def print_animation_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	print("///////")
	print(update.message.animation["file_id"] + ";")

def print_sticker_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	print("///////")
	print(update.message.sticker["file_id"] + ";")

#Sending usage data...
async def bot_usage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	id = update.effective_chat.id
	m = update.message.text.split(" ")
	if len(m) > 1 and m[1] == config["password"]:
		m = us.build_usage_message()
		await context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)
	else:
		logging.info(hide_id(id) + " wanted to check a game round state...")
		await context.bot.send_message(chat_id=id, text=msg.get_message("intruder"), parse_mode=ParseMode.HTML)

#Saving usage data...
async def save_usage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	id = update.effective_chat.id
	m = update.message.text.split(" ")
	if len(m) > 1 and m[1] == config["password"]:
		us.save_usage()
		await context.bot.send_message(chat_id=id, text="Datos guardados...", parse_mode=ParseMode.HTML)
	else:
		logging.info(hide_id(id) + " wanted to check a game round state...")
		await context.bot.send_message(chat_id=id, text=msg.get_message("intruder"), parse_mode=ParseMode.HTML)

#Hiding the first numbers of a chat id for the log...
def hide_id(id):
	s = str(id)
	return "****" + s[len(s)-4:]

#Building the conversation handler...
def build_conversation_handler():
	handler = ConversationHandler(
		entry_points=[CommandHandler("rebus", start_rebus), CommandHandler("acertijo", start_acertijo),
					CommandHandler("firewall", selecting_firewall), CommandHandler("levenshtein", start_leveshtein),
					CommandHandler("error", trigger_error_submit)],
		states={FIREWALL_L: [CallbackQueryHandler(conversation_button_click)],
				TRYING:[MessageHandler(filters.TEXT & ~filters.COMMAND, check_try),
					CallbackQueryHandler(conversation_button_click)],
				FIREWALL: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_firewall),
						CallbackQueryHandler(conversation_button_click)],
				LEVENSHTEIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_levenshtein),
							CallbackQueryHandler(conversation_button_click)],
				ERROR_1: [MessageHandler(filters.TEXT & ~filters.COMMAND, report_command)],
				ERROR_2: [MessageHandler(filters.TEXT & ~filters.COMMAND, report_error)]},
				fallbacks=[MessageHandler(filters.COMMAND, cancel_challenge)],
				per_chat=True, per_user=False, per_message=False)
	return handler

#Configuring logging and getting ready to work...
def main():
	if config["logging"] == "persistent":
		logging.basicConfig(filename="history.txt", filemode='a',level=logging.INFO,
						format="%(asctime)s;%(name)s;%(levelname)s;%(message)s")
	elif config["logging"] == "debugging":
		logging.basicConfig(level=logging.DEBUG, format="%(asctime)s;%(name)s;%(levelname)s;%(message)s")
	else:
		logging.basicConfig(level=logging.INFO, format="%(asctime)s;%(name)s;%(levelname)s;%(message)s")
	print("Ready to build the bot...", end="\n")
	app = Application.builder().token(config["token"]).build()
	#app.add_error_handler(error_notification)
	app.add_handler(CommandHandler("start", start), group=2)
	app.add_handler(CommandHandler("palindromo", send_palindromo), group=2)
	app.add_handler(CommandHandler("reversible", send_reverse_number), group=2)
	app.add_handler(CommandHandler("video", send_video), group=2)
	app.add_handler(CommandHandler("jugarmenor", save_minor_number), group=2)
	app.add_handler(CommandHandler("chequearmenor", minor_number_info), group=2)
	app.add_handler(CommandHandler("terminarmenor", end_minor_number), group=2)
	app.add_handler(CommandHandler("info", print_info), group=2)
	app.add_handler(CommandHandler("help", print_help), group=2)
	app.add_handler(CommandHandler("botusage", bot_usage), group=2)
	app.add_handler(CommandHandler("saveusage", save_usage), group=2)
	app.add_handler(CallbackQueryHandler(button_click), group=2)
	app.add_handler(build_conversation_handler(), group=1)
	app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, wrong_message), group=1)
	#app.add_handler(MessageHandler(filters.STICKER, print_sticker_id), group=1)
	if config["webhook"]:
		logging.info("Setting up a webhook...")
		wh_url = "https://" + config["public_ip"] + ":" + str(config["webhook_port"]) + "/" + config["webhook_path"]
		app.run_webhook(listen="0.0.0.0", port=config["webhook_port"], secret_token=config["webhook_path"], key="webhook.key",
							cert="webhook.pem", webhook_url=wh_url, drop_pending_updates=True)
	else:
		logging.info("Ready to start polling...")
		app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
	main()
