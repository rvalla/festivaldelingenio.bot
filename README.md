![logo](https://gitlab.com/rodrigovalla/festivaldelingeniobot/-/raw/themoststable/assets/img/icon_64.png)

# Festival del Ingenio: telegram bot

This is the code for a telegram bot. The idea is to have fun with the public of **Festival del ingenio**, an event
which take place in Buenos Aires every year. It is part of the family of **Celebration of mind**.  

## online status

**Festival del Ingenio Bot** is not currently deployed. It will be available during some moments of the week while I run
some tests. Stay tuned!

## commands

Here you can see the list of available commands. Some of them allow you to pass parameters.

- **/start**: returns simply a greeting.  
- **/rebus**: to start a *rebus challenge*.
- **/adivinanza**: to start an *adivinanza challenge*.
- **/palindromo**: sends a palíndromo.
- **/video**: share a video from the Youtube chanel.
- **/help**: obviously to help.
- **/info**: to share social networks.

## running the code

Note that you will need a *config.json* file on root which includes the bot's mandatory token to run this software.
Currently *token* (provided by [@BotFather](https://t.me/BotFather) and *logging* (info, debugging or persistent)
are needed:

```
{
	"bot_name": "Festival del Ingenio Bot",
	"date": "2021-11-14",
	"username": "festivaldelingenio_bot",
	"admin_id": "A mistery",
	"link": "https://t.me/festivaldelingenio_bot",
	"token": "I won't tell you my token",
	"logging": "info",
}

```

## standing upon the shoulders of giants

This little project is possible thanks to a lot of work done by others in the *open-source* community. Particularly in
this case I need to mention:

- [**Python**](https://www.python.org/): the programming language I used.  
- [**python-telegram-bot**](https://python-telegram-bot.org/): the library I used to contact the *Telegram API*.  

Reach **Festival del Ingenio Bot** [here](https://t.me/festivaldelingeniobot_bot).
Feel free to contact me by [mail](mailto:rodrigovalla@protonmail.ch) or reach me in
[telegram](https://t.me/rvalla) or [mastodon](https://fosstodon.org/@rvalla).
