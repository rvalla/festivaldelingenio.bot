![logo](https://gitlab.com/rodrigovalla/festivaldelingeniobot/-/raw/themoststable/assets/img/icon_64.png)

# Festival del Ingenio Bot: changelog

## 2021-12-12: v0.7 beta

Several changes were done related to groups. Some to solve bugs when is a group who chats withe the bot.
Data of the *challenges* are stored now in *chat_data* dictionary. Some new secret commands were added.
New **Usage()** class is in charge of saving data of bot's usage.

## 2021-12-09: v0.6 beta

New assets were added. **Game()** class is bigger and has new name: **Play()**, a change that make sense since
the new **Play()** class will be in charge of new games. One of them is *the firewall* in which users must find
out what conditions a message has to meet to pass through a filter.

- **Commands**: the command to play a *minor number* round is */jugarmenor* now. A new */firewall* command
can be used to play a new individual game. Now you can pass arguments along */help* command to receive
instructions to play games (menor, promedio, firewall).

## 2021-11-26: v0.5 beta

Ready to play during *Celebration of mind* event in Buenos Aires. Now you can use secrets commands to
know the state or end a round of the *minor number game*.  

## 2021-11-20: v0.4 beta

Different bugs were fixed. The **bot** can be used to play a live game. A new *Game()* class saves a series
a moves for a game which is ended by an administrator message (password needed). There are new challenges and the
sticker's database is bigger. Some of the new features are:  

- **Challenges**: A user who ask for a solution receives an explanation for the difficult ones now.
- **Commands**: You can send */jugar n* to play a round of the *minor number game*.

## 2021-11-18: v0.3 beta

The structure of the **bot** is ready. Some of the changes and new features are:

- **Challenges**: Now is possible to check answers of any number of words. Images for the challenges are
called from telegram servers. The **bot** send stickers selecting them randomly from a categorized database.
- **Commands**: You can send */reversible* command to obtain a reversible number.  

## 2021-11-14: v0.1 alpha

First steps setting the bot. Testing *conversationhandling* to build different *challenges**.

Reach **Festival del Ingenio Bot** [here](https://t.me/festivaldelingeniobot_bot).
Feel free to contact me by [mail](mailto:rodrigovalla@protonmail.ch) or reach me in
[telegram](https://t.me/rvalla) or [mastodon](https://fosstodon.org/@rvalla).
