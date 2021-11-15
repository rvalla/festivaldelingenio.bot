from telegram.ext import Updater, ConversationHandler, CommandHandler, CallbackQueryHandler,  MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
import traceback, logging
import json as js
from messages import Messages
from assets import Assets

config = js.load(open("config.json")) #The configuration .json file (token included)
msg = Messages() #The class which knows what to say...
ass = Assets() #The class to access the different persistent assets...
TRY1 = range(1) #Conversation states...
rebus_keys = ["type", "words","path","solution","hint"]
adivinanza_keys = ["type", "solution_type","type_category","statement","solution","hint"]
attempts_limit = 4

#Starting the chat with a new user...
def start(update, context):
	id = update.effective_chat.id
	logging.info(hide_id(id) + " started the bot...")
	context.bot.send_message(chat_id=id, text=msg.get_message("hello"), parse_mode=ParseMode.HTML)
	context.bot.send_message(chat_id=id, text=msg.get_message("hello2"), parse_mode=ParseMode.HTML)

#Starting an adivinanza challenge...
def start_adivinanza(update, context):
	id = update.effective_chat.id
	logging.info(hide_id(id) + " started adivinanza challenge...")
	load_challenge(context.user_data, ass.get_adivinanza_data(), adivinanza_keys)
	context.bot.send_message(chat_id=id, text=msg.get_message("start_challenge"), parse_mode=ParseMode.HTML)
	context.bot.send_message(chat_id=id, text=msg.build_adivinanza_message(context.user_data["solution_type"], context.user_data["statement"]), parse_mode=ParseMode.HTML)
	return TRY1

#Starting rebus challenge...
def start_rebus(update, context):
	id = update.effective_chat.id
	logging.info(hide_id(id) + " started rebus challenge...")
	load_challenge(context.user_data, ass.get_rebus_data(), rebus_keys)
	context.bot.send_message(chat_id=id, text=msg.get_message("start_challenge"), parse_mode=ParseMode.HTML)
	context.bot.send_message(chat_id=id, text=msg.build_rebus_message(context.user_data["words"]), parse_mode=ParseMode.HTML)
	try:
		logging.info("Sending rebus image now..")
		context.bot.send_photo(chat_id=id, photo=ass.get_rebus_image(context.user_data["path"]))
		return TRY1
	except:
		logging.info("Error: It was imposible to send the image")
		context.bot.send_message(chat_id=id, text=msg.get_message("error"), parse_mode=ParseMode.HTML)
		return ConversationHandler.END

#Loading rebus data to CallbackContext
def load_challenge(user_data, rebus, keys):
	data = rebus.split(";")
	for r, k in zip(data, keys):
		user_data[k] = r
	user_data["attempts"] = 0
	user_data["saw_hint"] = False

def check_try(update, context):
	if is_correct_answer(update.message.text, context.user_data["solution"]):
		send_congrats(update, context)
		return ConversationHandler.END
	else:
		if context.user_data["attempts"] < attempts_limit:
			context.user_data["attempts"] += 1
			if context.user_data["saw_hint"] == False:
				keyboard = [[InlineKeyboardButton(text="Pista", callback_data="hint"),
							InlineKeyboardButton(text="Solución", callback_data="solution")]]
			else:
				keyboard = [[InlineKeyboardButton(text="Solución", callback_data="solution")]]
			reply = InlineKeyboardMarkup(keyboard)
			update.message.reply_text(msg.get_message("bad_answer"),reply_markup=reply)
		else:
			end_challenge(update, context)
			return ConversationHandler.END

def is_correct_answer(text, solution):
	if text.lower() == solution:
		return True
	else:
		return False

def send_congrats(update, context):
	update.message.reply_text(msg.build_congrats_message("good_answer", context.user_data["type"]))
	context.user_data.clear()

def send_hint(update, context):
	m = msg.build_hint_message(context.user_data["hint"])
	context.bot.send_message(chat_id=update.effective_chat.id, text=m, parse_mode=ParseMode.HTML)
	context.user_data["saw_hint"] = True

def send_solution(update, context):
	m = msg.build_solution_message(context.user_data["solution"], context.user_data["type"])
	context.bot.send_message(chat_id=update.effective_chat.id, text=m, parse_mode=ParseMode.HTML)
	context.user_data.clear()

def end_challenge(update, context):
	m = msg.build_end_challenge_message("end_challenge", context.user_data["type"])
	context.bot.send_message(chat_id=update.effective_chat.id, text=m, parse_mode=ParseMode.HTML)
	context.user_data.clear()
	return ConversationHandler.END

#Sendind a palindromo for the user...
def send_palindromo(update, context):
	id = update.effective_chat.id
	logging.info(hide_id(id) + " asked for a palindromo...")
	context.bot.send_message(chat_id=id, text=msg.get_message("palindromo"), parse_mode=ParseMode.HTML)
	context.bot.send_message(chat_id=id, text=msg.italic(ass.get_palindromo()), parse_mode=ParseMode.HTML)

#Sendind a video from the youtube chanel...
def send_video(update, context):
	id = update.effective_chat.id
	logging.info(hide_id(id) + " asked for a video...")
	context.bot.send_message(chat_id=id, text=msg.build_video_message(ass.get_video_data()), parse_mode=ParseMode.HTML)

#Triggering /help command...
def print_help(update, context):
	id = update.effective_chat.id
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

def button_click(update, context):
	query = update.callback_query
	query.answer()
	if query.data == "hint":
		send_hint(update, context)
	elif query.data == "solution":
		send_solution(update, context)
		return ConversationHandler.END
	elif query.data == "end_challenge":
		end_challenge(update, context)

#Sending a message to bot admin when an error occur...
def error_notification(update, context):
	id = update.effective_chat.id
	m = "An error ocurred! While comunicating with chat " + hide_id(id)
	logging.info(m)
	context.bot.send_message(chat_id=config["admin_id"], text=m, parse_mode=ParseMode.HTML)

#Hiding the first numbers of a chat id for the log...
def hide_id(id):
	s = str(id)
	return "****" + s[len(s)-4:]

def build_conversation_handler():
	handler = ConversationHandler(
		entry_points=[CommandHandler("rebus", start_rebus), CommandHandler("adivinanza", start_adivinanza)],
		states={TRY1:[CommandHandler("cancel", end_challenge),
					MessageHandler(Filters.text, check_try),
					CallbackQueryHandler(button_click)]},
				fallbacks=[])
	return handler

#Configuring logging and getting ready to work...
def main():
	if config["logging"] == "persistent":
		logging.basicConfig(filename="history.txt", filemode='a',level=logging.INFO,
						format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	elif config["logging"] == "debugging":
		logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	else:
		logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	updater = Updater(config["token"], request_kwargs={'read_timeout': 5, 'connect_timeout': 5})
	dp = updater.dispatcher
	#dp.add_error_handler(error_notification)
	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CommandHandler("palindromo", send_palindromo))
	dp.add_handler(CommandHandler("video", send_video))
	dp.add_handler(CommandHandler("info", print_info))
	dp.add_handler(CommandHandler("help", print_help))
	dp.add_handler(build_conversation_handler())
	dp.add_handler(MessageHandler(Filters.text, wrong_message))
	dp.bot.send_message(chat_id=config["admin_id"], text="The bot is online!", parse_mode=ParseMode.HTML)
	updater.start_polling(drop_pending_updates=True)
	updater.idle()

if __name__ == "__main__":
	main()
