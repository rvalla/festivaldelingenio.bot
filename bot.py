from telegram.ext import Updater, ConversationHandler, CommandHandler, CallbackQueryHandler,  MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
import traceback, logging
import json as js
from messages import Messages
from assets import Assets
from play import Play

logger = logging.getLogger(__name__)
config = js.load(open("config.json")) #The configuration .json file (token included)
msg = Messages() #The class which knows what to say...
ass = Assets() #The class to access the different persistent assets...
pl = Play() #The class to let the users play some game...
TRYING, FIREWALL = range(2) #Conversation states...
rebus_keys = ["command", "type","animated","words","solution","explanation","hint","file_id","path"] #Keys to load rebus data...
acertijo_keys = ["command", "type","words","solution_type","statement","solution","explanation","hint"] #Keys to load acertijo data...
firewall_keys = ["command", "type", ]
attempts_limit = 2 #Defining the number of attempts before ending a challenge...
firewall_limits = [2, 4] #Defining victory-loose limits for firewall game...
vowelsa, vowelsb = "áéíóúü", "aeiouu" #Mapping special characters to check sent solutions...
translation = str.maketrans(vowelsa, vowelsb)

#Starting the chat with a new user...
def start(update, context):
	id = update.effective_chat.id
	logging.info(hide_id(id) + " started the bot...")
	context.bot.send_message(chat_id=id, text=msg.get_message("hello"), parse_mode=ParseMode.HTML)
	context.bot.send_message(chat_id=id, text=msg.get_message("hello2"), parse_mode=ParseMode.HTML)

#Starting an acertijo challenge...
def start_acertijo(update, context):
	id = update.effective_chat.id
	logging.info(hide_id(id) + " started acertijo challenge...")
	load_challenge(context.user_data, ass.get_acertijo_data(), acertijo_keys)
	context.bot.send_message(chat_id=id, text=msg.get_message("start_challenge"), parse_mode=ParseMode.HTML)
	context.bot.send_message(chat_id=id, text=msg.build_acertijo_message(context.user_data["solution_type"], context.user_data["statement"]), parse_mode=ParseMode.HTML)
	return TRYING

#Starting rebus challenge...
def start_rebus(update, context):
	id = update.effective_chat.id
	logging.info(hide_id(id) + " started rebus challenge...")
	load_challenge(context.user_data, ass.get_rebus_data(), rebus_keys)
	context.bot.send_message(chat_id=id, text=msg.get_message("start_challenge"), parse_mode=ParseMode.HTML)
	context.bot.send_message(chat_id=id, text=msg.build_rebus_message(context.user_data["type"], context.user_data["words"]), parse_mode=ParseMode.HTML)
	try:
		logging.info("Sending rebus image now..")
		send_image(context, context.user_data["animated"], id, context.user_data["file_id"])
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
def load_challenge(user_data, rebus, keys):
	data = rebus.split(";")
	for r, k in zip(data, keys):
		user_data[k] = r
	user_data["attempts"] = 0 #Saving number of attempsts...
	user_data["saw_hint"] = False #A field to know if the user asded for a hint...

#TRYING state check the answers sent by the user...
def check_try(update, context):
	if is_correct_answer(update.message.text, context.user_data["solution"], int(context.user_data["words"])):
		send_congrats(update, context)
		return ConversationHandler.END #Ending challenge after user succeded...
	else:
		if context.user_data["attempts"] < attempts_limit:
			context.user_data["attempts"] += 1
			if context.user_data["saw_hint"] == False: #Deciding what buttons to send...
				keyboard = [[InlineKeyboardButton(text="Pista", callback_data="hint"),
							InlineKeyboardButton(text="Solución", callback_data="solution")]]
			else:
				keyboard = [[InlineKeyboardButton(text="Solución", callback_data="solution")]]
			reply = InlineKeyboardMarkup(keyboard)
			update.message.reply_text(msg.get_message("bad_answer"),reply_markup=reply)
		else:
			update.message.reply_sticker(ass.get_sticker_id(2))
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
	if context.user_data["saw_hint"] == False:
		update.message.reply_sticker(ass.get_sticker_id(0))
	update.message.reply_text(msg.build_congrats_message("good_answer", context.user_data["command"]))
	context.user_data.clear()

#Sending the challenge's hint...
def send_hint(update, context):
	id = update.effective_chat.id
	m = msg.build_hint_message(context.user_data["hint"])
	context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)
	context.bot.send_sticker(chat_id=id, sticker=ass.get_sticker_id(1))
	context.user_data["saw_hint"] = True

#Sending the solution from a challenge...
def send_solution(update, context):
	id = update.effective_chat.id
	m = msg.build_solution_message(context.user_data["solution"], context.user_data["command"], context.user_data["explanation"])
	context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)
	if context.user_data["saw_hint"] == False:
		context.bot.send_sticker(chat_id=id, sticker=ass.get_sticker_id(1))
	context.user_data.clear()

#Ending a challenge...
def end_challenge(update, context):
	m = msg.build_end_challenge_message("end_challenge", context.user_data["command"])
	context.bot.send_message(chat_id=update.effective_chat.id, text=m, parse_mode=ParseMode.HTML)
	context.user_data.clear()
	return ConversationHandler.END

#Canceling the challenge without offering another one...
def cancel_challenge(update, context):
	m = msg.get_message("end_challenge")
	context.bot.send_message(chat_id=update.effective_chat.id, text=m, parse_mode=ParseMode.HTML)
	context.user_data.clear()
	return ConversationHandler.END

#Starting a firewall game round...
def start_firewall(update, context):
	id = update.effective_chat.id
	logging.info(hide_id(id) + " started a firewall game...")
	load_firewall(context.user_data)
	m = msg.build_start_firewall_message(context.user_data["ex_pass"], context.user_data["ex_notpass"])
	context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)
	return FIREWALL

#Checking a firewall move...
def check_firewall(update, context):
	id = update.effective_chat.id
	input = update.message.text
	context.user_data["attempts"] += 1
	success = trough_firewall(input, context.user_data)
	if success:
		context.user_data["success"] += 1
	m = msg.answer_firewall_message(success, input)
	context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)
	if context.user_data["success"] == firewall_limits[0]:
		end_firewall_game(update, context, True)
		return ConversationHandler.END
	elif firewall_limits[1] - context.user_data["attempts"] <  firewall_limits[0] - context.user_data["success"]:
		end_firewall_game(update, context, False)
		return ConversationHandler.END

#Deciding if a message pass trough the firewall...
def trough_firewall(message, user_data):
	return pl.check_firewall(user_data["algorithm"], message, user_data["parameters"])

#Ending a firewall game...
def end_firewall_game(update, context, victory):
	id = update.effective_chat.id
	logging.info(hide_id(id) + " ended a firewall game: " + str(victory))
	m = msg.end_firewall_message(victory, context.user_data["command"])
	if victory:
		sticker = ass.get_sticker_id(0)
	else:
		sticker = ass.get_sticker_id(2)
	context.bot.send_sticker(chat_id=id, sticker=sticker)
	context.bot.send_message(chat_id=id, text=m, parse_mode=ParseMode.HTML)
	context.user_data.clear()

#Loading firewall round data...
def load_firewall(user_data):
	user_data["attempts"] = 0
	user_data["success"] = 0
	firewall = pl.get_firewall_game()
	keys = list(firewall)
	for k in keys:
		user_data[k] = firewall[k]

#Sending a palindromo for the user...
def send_palindromo(update, context):
	id = update.effective_chat.id
	logging.info(hide_id(id) + " asked for a palindromo...")
	context.bot.send_message(chat_id=id, text=msg.get_message("palindromo"), parse_mode=ParseMode.HTML)
	context.bot.send_message(chat_id=id, text=msg.italic(ass.get_palindromo()), parse_mode=ParseMode.HTML)

#Sending a reverse number...
def send_reverse_number(update, context):
	id = update.effective_chat.id
	in_m = update.message.text.split(" ")
	logging.info(hide_id(id) + " asked for a reverse number...")
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
	logging.info(hide_id(id) + " asked for a video...")
	context.bot.send_message(chat_id=id, text=msg.build_video_message(ass.get_video_data()), parse_mode=ParseMode.HTML)

#Using the bot to play a live game...
def save_minor_number(update, context):
	id = update.effective_chat.id
	m = update.message.text.split(" ")
	if len(m) == 2:
		try:
			number = int(m[1]) #First we check if the user sent us a number
			if number > 0:
				fn = update.effective_chat.first_name
				ln = update.effective_chat.last_name
				try:
					name = fn + " " + ln #Saving first_name + last_name in case last_name is not None
				except:
					name = fn
				logging.info(hide_id(id) + " playing a move in minor number game...")
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
	logging.info(hide_id(id) + " failed to play a move...")
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

#Triggering /help command...
def print_help(update, context):
	id = update.effective_chat.id
	m = update.message.text.split(" ")
	if len(m) == 2:
		logging.info(hide_id(id) + " asked for help type: " + m[1])
		type = m[1].lower().translate(translation)
		context.bot.send_message(chat_id=id, text=msg.build_custom_help_message(type), parse_mode=ParseMode.HTML)
	else:
		logging.info(hide_id(id) + " asked for help...")
		context.bot.send_message(chat_id=id, text=msg.build_help_message(), parse_mode=ParseMode.HTML)

#Triggering /info command...
def print_info(update, context):
	id = update.effective_chat.id
	logging.info(hide_id(id) + " asked for information...")
	context.bot.send_message(chat_id=id, text=msg.build_info_message(), parse_mode=ParseMode.HTML)

#Answering a text message out of any conversation...
def wrong_message(update, context):
	id = update.effective_chat.id
	logging.info(hide_id(id) + " intended to chat...")
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

#Hiding the first numbers of a chat id for the log...
def hide_id(id):
	s = str(id)
	return "****" + s[len(s)-4:]

#Building the conversation handler...
def build_conversation_handler():
	handler = ConversationHandler(
		entry_points=[CommandHandler("rebus", start_rebus), CommandHandler("acertijo", start_acertijo),
					CommandHandler("firewall", start_firewall)],
		states={TRYING:[MessageHandler(Filters.text & ~Filters.command, check_try),
					CallbackQueryHandler(conversation_button_click)],
				FIREWALL: [MessageHandler(Filters.text & ~Filters.command, check_firewall)]},
				fallbacks=[MessageHandler(Filters.command, cancel_challenge)])
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
#	dp.add_error_handler(error_notification)
	dp.add_handler(CommandHandler("start", start), group=2)
	dp.add_handler(CommandHandler("palindromo", send_palindromo), group=2)
	dp.add_handler(CommandHandler("reversible", send_reverse_number), group=2)
	dp.add_handler(CommandHandler("video", send_video), group=2)
	dp.add_handler(CommandHandler("jugarmenor", save_minor_number), group=2)
	dp.add_handler(CommandHandler("chequearmenor", minor_number_info), group=2)
	dp.add_handler(CommandHandler("terminarmenor", end_minor_number), group=2)
	dp.add_handler(CommandHandler("info", print_info), group=2)
	dp.add_handler(CommandHandler("help", print_help), group=2)
	dp.add_handler(build_conversation_handler(), group=1)
	dp.add_handler(MessageHandler(Filters.text & ~Filters.command, wrong_message), group=1)
	dp.add_handler(MessageHandler(Filters.photo & ~Filters.command, print_photo_id), group=1)
	dp.bot.send_message(chat_id=config["admin_id"], text="The bot is starting!", parse_mode=ParseMode.HTML)
	if config["webhook"]:
		wh_url = "https://" + config["public_ip"] + ":" + str(config["webhook_port"]) + "/" + config["webhook_path"]
		updater.start_webhook(listen="0.0.0.0", port=config["webhook_port"], url_path=config["webhook_path"], key="webhook.key",
							cert="webhook.pem", webhook_url=wh_url, drop_pending_updates=True)
	else:
		updater.start_polling(drop_pending_updates=True)
		updater.idle()

if __name__ == "__main__":
	main()
