from telegram.ext import CallbackContext, Updater, ConversationHandler, CommandHandler, CallbackQueryHandler,  MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
import traceback, logging
import json as js
from usage import Usage
from messages import Messages
from assets import Assets
from play import Play

logger = logging.getLogger(__name__)
config = js.load(open("config.json")) #The configuration .json file (token included)
us = Usage("usage.csv") #The class to store usage data...
msg = Messages() #The class which knows what to say...
ass = Assets() #The class to access the different persistent assets...
pl = Play("games.csv") #The class to let the users play some game...
LEVEL, TRYING, FIREWALL = range(3) #Conversation states...
rebus_keys = ["command", "type","animated","words","solution","explanation","hint","file_id","path"] #Keys to load rebus data...
acertijo_keys = ["command", "type","words","solution_type","statement","solution","explanation","hint"] #Keys to load acertijo data...
firewall_keys = ["command", "type", ]
attempts_limit = 2 #Defining the number of attempts before ending a challenge...
firewall_limits = [5, 13] #Defining victory-loose limits for firewall game...
vowelsa, vowelsb = "áéíóúü", "aeiouu" #Mapping special characters to check sent solutions...
translation = str.maketrans(vowelsa, vowelsb)

#Starting the chat with a new user...
def start(update, context):
	id = update.effective_chat.id
	logging.info(hide_id(id) + " started the bot...")
	us.add_start()
	m = msg.get_message("hello") + "\n\n" + msg.get_message("hello2")
	context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)

#Starting an acertijo challenge...
def start_acertijo(update, context):
	id = update.effective_chat.id
	load_challenge(context.chat_data, ass.get_acertijo_data(), acertijo_keys)
	context.bot.send_message(chat_id=id, text=msg.get_message("start_challenge"), parse_mode=ParseMode.HTML)
	context.bot.send_message(chat_id=id, text=msg.build_acertijo_message(context.chat_data["solution_type"], context.chat_data["statement"]), parse_mode=ParseMode.HTML)
	return TRYING

#Starting rebus challenge...
def start_rebus(update, context):
	id = update.effective_chat.id
	load_challenge(context.chat_data, ass.get_rebus_data(), rebus_keys)
	context.bot.send_message(chat_id=id, text=msg.get_message("start_challenge"), parse_mode=ParseMode.HTML)
	context.bot.send_message(chat_id=id, text=msg.build_rebus_message(context.chat_data["type"], context.chat_data["words"]), parse_mode=ParseMode.HTML)
	try:
		send_image(context, context.chat_data["animated"], id, context.chat_data["file_id"])
		return TRYING #Entering TRYING state if image was sent succesfully...
	except:
		logging.info("Error: It was imposible to send the image")
		context.bot.send_message(chat_id=id, text=msg.get_message("error"), parse_mode=ParseMode.HTML)
		return ConversationHandler.END #Ending challenge if image was not sent...

#Sending images and animations...
def send_image(context, animated, id, file_id):
	if animated == "True":
		context.bot.send_animation(chat_id=id, animation=file_id)
	else:
		context.bot.send_photo(chat_id=id, photo=file_id)

#Loading challenge data to CallbackContext
def load_challenge(chat_data, rebus, keys):
	data = rebus.split(";")
	for r, k in zip(data, keys):
		chat_data[k] = r
	chat_data["attempts"] = 0 #Saving number of attempsts...
	chat_data["saw_hint"] = False #A field to know if the user asded for a hint...

#TRYING state check the answers sent by the user...
def check_try(update, context):
	id = update.effective_chat.id
	if is_correct_answer(update.message.text, context.chat_data["solution"], int(context.chat_data["words"])):
		send_congrats(update, context)
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
			context.bot.send_message(chat_id=id, text=msg.get_message("bad_answer"), reply_markup=reply, parse_mode=ParseMode.HTML)
		else:
			context.bot.send_sticker(chat_id=id, sticker=ass.get_sticker_id(2))
			end_challenge(update, context)
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
def send_congrats(update, context):
	id = update.effective_chat.id
	us.add_challenge(1, context.chat_data["command"])
	if context.chat_data["saw_hint"] == False:
		context.bot.send_sticker(chat_id=id, sticker=ass.get_sticker_id(0))
	m = msg.build_congrats_message("good_answer", context.chat_data["command"])
	context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)
	context.chat_data.clear()

#Sending the challenge's hint...
def send_hint(update, context):
	id = update.effective_chat.id
	m = msg.build_hint_message(context.chat_data["hint"])
	context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)
	context.bot.send_sticker(chat_id=id, sticker=ass.get_sticker_id(1))
	context.chat_data["saw_hint"] = True

#Sending the solution from a challenge...
def send_solution(update, context):
	id = update.effective_chat.id
	us.add_challenge(3, context.chat_data["command"])
	m = msg.build_solution_message(context.chat_data["solution"], context.chat_data["command"], context.chat_data["explanation"])
	context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)
	if context.chat_data["saw_hint"] == False:
		context.bot.send_sticker(chat_id=id, sticker=ass.get_sticker_id(1))
	context.chat_data.clear()

#Ending a challenge...
def end_challenge(update, context):
	us.add_challenge(2, context.chat_data["command"])
	m = msg.build_end_challenge_message("end_challenge", context.chat_data["command"])
	context.bot.send_message(chat_id=update.effective_chat.id, text=m, parse_mode=ParseMode.HTML)
	context.chat_data.clear()
	return ConversationHandler.END

#Canceling the challenge without offering another one...
def cancel_challenge(update, context):
	us.add_challenge(4, context.chat_data["command"])
	m = msg.get_message("end_challenge")
	context.bot.send_message(chat_id=update.effective_chat.id, text=m, parse_mode=ParseMode.HTML)
	context.chat_data.clear()
	return ConversationHandler.END

#Selecting firewall difficulty and starting challenge...
def selecting_firewall(update, context):
	id = update.effective_chat.id
	keyboard = [[InlineKeyboardButton(text="Fácil", callback_data="f_0"),
				InlineKeyboardButton(text="Difícil", callback_data="f_1"),
				InlineKeyboardButton(text="Durísimo", callback_data="f_2")]]
	reply = InlineKeyboardMarkup(keyboard)
	context.bot.send_message(chat_id=id, text=msg.get_message("present_firewall"), reply_markup=reply, parse_mode=ParseMode.HTML)
	return LEVEL

#Starting a firewall game round...
def start_firewall(update, context, difficulty):
	id = update.effective_chat.id
	load_firewall(context.chat_data, difficulty)
	m = msg.build_start_firewall_message(context.chat_data["ex_pass"], context.chat_data["ex_notpass"])
	context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)

#Checking a firewall move...
def check_firewall(update, context):
	id = update.effective_chat.id
	input = update.message.text.lower().translate(translation)
	if input not in context.chat_data["moves"]:
		context.chat_data["attempts"] += 1
		success = trough_firewall(input, context.chat_data)
		if success:
			context.chat_data["success"] += 1
			context.chat_data["moves"].add(input)
		m = msg.answer_firewall_message(success, input)
		context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)
		if context.chat_data["success"] == firewall_limits[0]:
			end_firewall_game(update, context, True)
			return ConversationHandler.END
		elif firewall_limits[1] - context.chat_data["attempts"] <  firewall_limits[0] - context.chat_data["success"]:
			end_firewall_game(update, context, False)
			return ConversationHandler.END
	else:
		firewall_cheat_detected(update, context)
		return ConversationHandler.END

#Deciding if a message pass trough the firewall...
def trough_firewall(message, chat_data):
	return pl.check_firewall(chat_data["algorithm"], message, chat_data["parameters"])

#Ending a firewall game...
def end_firewall_game(update, context, victory):
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
	context.bot.send_sticker(chat_id=id, sticker=sticker)
	context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)
	context.chat_data.clear()

#Ending a firewall game because the user cheated...
def firewall_cheat_detected(update, context):
	id = update.effective_chat.id
	us.add_challenge(3, context.chat_data["command"])
	logging.info(hide_id(id) + " ended a firewall game: CHEAT")
	context.bot.send_message(chat_id=id, text=msg.get_message("firewall_cheat"), parse_mode=ParseMode.HTML)
	context.bot.send_sticker(chat_id=id, sticker=ass.get_sticker_id(3))

#Loading firewall round data...
def load_firewall(chat_data, difficulty):
	firewall = pl.get_firewall_game(difficulty)
	keys = list(firewall)
	for k in keys:
		chat_data[k] = firewall[k]
	chat_data["attempts"] = 0
	chat_data["success"] = 0
	chat_data["moves"] = set()
	chat_data["moves"].add(chat_data["ex_pass"])

#Sending a palindromo for the user...
def send_palindromo(update, context):
	id = update.effective_chat.id
	us.add_palindromo()
	context.bot.send_message(chat_id=id, text=msg.get_message("palindromo"), parse_mode=ParseMode.HTML)
	context.bot.send_message(chat_id=id, text=msg.italic(ass.get_palindromo()), parse_mode=ParseMode.HTML)

#Sending a reverse number...
def send_reverse_number(update, context):
	id = update.effective_chat.id
	in_m = update.message.text.split(" ")
	us.add_reversible()
	if len(in_m) > 1:
		try:
			n = int(in_m[1])
			data = ass.get_reverse_number(n).split(";")
			m = msg.get_message("reverse_number") + "\n\n"
			m += msg.bold(data[1])
			context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)
			context.bot.send_photo(chat_id=id, photo=data[2])
		except:
			context.bot.send_message(chat_id=id, text=msg.get_message("reverse_error"), parse_mode=ParseMode.HTML)
	else:
		data = ass.get_random_reverse_number().split(";")
		m = msg.get_message("reverse_number") + "\n\n"
		m += msg.bold(data[1])
		context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)
		context.bot.send_photo(chat_id=id, photo=data[2])

#Sendind a video from the youtube chanel...
def send_video(update, context):
	id = update.effective_chat.id
	us.add_video()
	context.bot.send_message(chat_id=id, text=msg.build_video_message(ass.get_video_data()), parse_mode=ParseMode.HTML)

#Using the bot to play a live game...
def save_minor_number(update, context):
	id = update.effective_chat.id
	m = update.message.text.split(" ")
	if len(m) == 2:
		try:
			number = int(m[1]) #First we check if the user sent us a number
			if number > 0:
				name = build_user_name(update)
				us.add_jugarmenor()
				if pl.save_minor_number(number, name, id): #Saving a move... Returns False if the player played before in the round...
					context.bot.send_message(chat_id=id, text=msg.build_minor_move_message(number, name), parse_mode=ParseMode.HTML)
				else:
					context.bot.send_message(chat_id=id, text=msg.get_message("play_double_move"), parse_mode=ParseMode.HTML)
			else:
				failed_minor_number(context, id)
		except:
			failed_minor_number(context, id)
	else:
		failed_minor_number(context, id)

#Notifying the user of a wrong game move...
def failed_minor_number(context, id):
	logging.info(hide_id(id) + " failed to play a minor number move...")
	context.bot.send_message(chat_id=id, text=msg.get_message("play_minor_number_move_error"), parse_mode=ParseMode.HTML)

#Ending a game round...
def end_minor_number(update, context):
	id = update.effective_chat.id
	m = update.message.text.split(" ")
	if len(m) > 1 and m[1] == config["password"]:
		winner_exist, number, winner, winner_id = pl.end_minor_game()
		logging.info(hide_id(id) + " ending a minor game round...")
		end_m = pl.minor_info() + "\n\n" + \
				msg.build_minor_game_message(winner_exist, number, winner)
		context.bot.send_message(chat_id=id, text=end_m, parse_mode=ParseMode.HTML)
		try:
			if winner_exist:
				context.bot.send_message(chat_id=winner_id, text=msg.build_minor_victory_message(number), parse_mode=ParseMode.HTML)
				context.bot.send_sticker(chat_id=winner_id, sticker=ass.get_sticker_id(0))
				logging.info("Game round victory notification sent")
			loosers = pl.get_minor_loosers(winner_id)
			looser_message = msg.build_minor_loose_message(winner_exist, winner, number)
			logging.info("Notifying loosers of a minor game round")
			for l in loosers:
				context.bot.send_message(chat_id=l, text=looser_message, parse_mode=ParseMode.HTML)
				context.bot.send_sticker(chat_id=l, sticker=ass.get_sticker_id(2))
		except:
			logging.info("Problems during game round notifications.")
		pl.save_minor(winner, number)
		pl.minor_reset()
	else:
		logging.info(hide_id(id) + " wanted to end a game round without the password...")
		context.bot.send_message(chat_id=id, text=msg.get_message("intruder"), parse_mode=ParseMode.HTML)

#Sending game current state...
def minor_number_info(update, context):
	id = update.effective_chat.id
	m = update.message.text.split(" ")
	if len(m) > 1 and m[1] == config["password"]:
		m = pl.minor_info()
		context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)
	else:
		logging.info(hide_id(id) + " wanted to check a game round state...")
		context.bot.send_message(chat_id=id, text=msg.get_message("intruder"), parse_mode=ParseMode.HTML)

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
def print_help(update, context):
	id = update.effective_chat.id
	m = update.message.text.split(" ")
	if len(m) == 2:
		type = m[1].lower().translate(translation)
		us.add_help(type)
		context.bot.send_message(chat_id=id, text=msg.build_custom_help_message(type), parse_mode=ParseMode.HTML)
	else:
		us.add_help(None)
		context.bot.send_message(chat_id=id, text=msg.build_help_message(), parse_mode=ParseMode.HTML)

#Triggering /info command...
def print_info(update, context):
	id = update.effective_chat.id
	us.add_info()
	context.bot.send_message(chat_id=id, text=msg.build_info_message(), parse_mode=ParseMode.HTML)

#Answering a text message out of any conversation...
def wrong_message(update, context):
	if update.message.reply_to_message == None:
		id = update.effective_chat.id
		us.add_wrong_message()
		context.bot.send_message(chat_id=id, text=msg.get_message("wrong"), parse_mode=ParseMode.HTML)

#Deciding what function to trigger after a button click...
def conversation_button_click(update, context):
	query = update.callback_query
	query.answer()
	if query.data == "hint":
		send_hint(update, context)
	elif query.data == "solution":
		send_solution(update, context)
		return ConversationHandler.END
	elif query.data.startswith("f"):
		d = int(query.data.split("_")[1])
		start_firewall(update, context, d)
		return FIREWALL

#Sending a message to bot admin when an error occur...
def error_notification(update, context):
	id = update.effective_chat.id
	m = "An error ocurred! While comunicating with chat " + hide_id(id)
	logging.info(m)
	context.bot.send_message(chat_id=config["admin_id"], text=m, parse_mode=ParseMode.HTML)

def print_photo_id(update, context):
	print("///////")
	print(update.message.photo[0]["file_id"] + ";")

def print_animation_id(update, context):
	print("///////")
	print(update.message.animation["file_id"] + ";")

def print_sticker_id(update, context):
	print("///////")
	print(update.message.sticker["file_id"] + ";")

#Sending usage data...
def bot_usage(update, context):
	id = update.effective_chat.id
	m = update.message.text.split(" ")
	if len(m) > 1 and m[1] == config["password"]:
		m = us.build_usage_message()
		context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)
	else:
		logging.info(hide_id(id) + " wanted to check a game round state...")
		context.bot.send_message(chat_id=id, text=msg.get_message("intruder"), parse_mode=ParseMode.HTML)

#Saving usage data...
def save_usage(update, context):
	id = update.effective_chat.id
	m = update.message.text.split(" ")
	if len(m) > 1 and m[1] == config["password"]:
		us.save_usage()
		context.bot.send_message(chat_id=id, text="Datos guardados...", parse_mode=ParseMode.HTML)
	else:
		logging.info(hide_id(id) + " wanted to check a game round state...")
		context.bot.send_message(chat_id=id, text=msg.get_message("intruder"), parse_mode=ParseMode.HTML)

#Hiding the first numbers of a chat id for the log...
def hide_id(id):
	s = str(id)
	return "****" + s[len(s)-4:]

#Building the conversation handler...
def build_conversation_handler():
	handler = ConversationHandler(
		entry_points=[CommandHandler("rebus", start_rebus), CommandHandler("acertijo", start_acertijo),
					CommandHandler("firewall", selecting_firewall)],
		states={LEVEL: [CallbackQueryHandler(conversation_button_click)],
				TRYING:[MessageHandler(Filters.text & ~Filters.command, check_try),
					CallbackQueryHandler(conversation_button_click)],
				FIREWALL: [MessageHandler(Filters.text & ~Filters.command, check_firewall)]},
				fallbacks=[MessageHandler(Filters.command, cancel_challenge)],
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
	updater = Updater(config["token"], request_kwargs={'read_timeout': 5, 'connect_timeout': 5})
	dp = updater.dispatcher
	dp.add_error_handler(error_notification)
	dp.add_handler(CommandHandler("start", start), group=2)
	dp.add_handler(CommandHandler("palindromo", send_palindromo), group=2)
	dp.add_handler(CommandHandler("reversible", send_reverse_number), group=2)
	dp.add_handler(CommandHandler("video", send_video), group=2)
	dp.add_handler(CommandHandler("jugarmenor", save_minor_number), group=2)
	dp.add_handler(CommandHandler("chequearmenor", minor_number_info), group=2)
	dp.add_handler(CommandHandler("terminarmenor", end_minor_number), group=2)
	dp.add_handler(CommandHandler("info", print_info), group=2)
	dp.add_handler(CommandHandler("help", print_help), group=2)
	dp.add_handler(CommandHandler("botusage", bot_usage), group=2)
	dp.add_handler(CommandHandler("saveusage", save_usage), group=2)
	dp.add_handler(build_conversation_handler(), group=1)
	dp.add_handler(MessageHandler(Filters.text & ~Filters.command, wrong_message), group=1)
	#dp.add_handler(MessageHandler(Filters.sticker, print_sticker_id), group=1)
	dp.bot.send_message(chat_id=config["admin_id"], text="The bot is starting!", parse_mode=ParseMode.HTML)
	if config["webhook"]:
		logging.info("Setting up a webhook...")
		wh_url = "https://" + config["public_ip"] + ":" + str(config["webhook_port"]) + "/" + config["webhook_path"]
		updater.start_webhook(listen="0.0.0.0", port=config["webhook_port"], url_path=config["webhook_path"], key="webhook.key",
							cert="webhook.pem", webhook_url=wh_url, drop_pending_updates=True)
	else:
		logging.info("Ready to start polling...")
		updater.start_polling(drop_pending_updates=True)
		updater.idle()

if __name__ == "__main__":
	main()
