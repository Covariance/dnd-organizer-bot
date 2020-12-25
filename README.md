# dnd-organizer-bot
Telegram bot for everything related to Dungeons&amp;Dragons - from dice rolling to character creation.

It is currently hosted on [@dnd_organizer_bot](t.me/dnd_organizer_bot).

## Supported commands
- /start - prints welcoming message.
- /help - printshelp for the current command or lists all commands with hints. Implemented via usage of OOP principles and creation of `Command` class.
- /dice - rolls specified amount of dice. Mathematical expressions with dices parser implemented.
- /new_char - creates new character via dialogue with user, implemented via callbacks and event handlers. Characters are stored in a SQLite database (future migration to PostgreSQL is planned).

Simplier dice rolling can be done via `!<dice_expression>` command.
