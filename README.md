# Summary
This is a personal finance tracker that is intended to help you keep track
of the money spend.
This is intended to be used along with the Money Manager app https://realbyteapps.com/
Since the Money Manager app does not allow multi users, there is a pain point to solve when
spending has to be tracked across different members of the family.
This project is a solution to such workflows.
The expectation is that the money manager app will be installed on one person's phone.
This user will be refered to as the admin and the others will send updates of their spendings/incomes to a telegram bot.
The telegram bot fills in the import.xls
The admin has to periodically import the import.xls to the money manager app.
https://help.realbyteapps.com/hc/en-us/articles/360043223253-How-to-import-bulk-data-by-Excel-file

## How to use

 1. First create a telegram bot follow the instructions on https://core.telegram.org/bots/tutorial
 2. Store the bot token in a `.env` file which is in the same location as the telegram-interpreter-bot.py
 3. YOu might have to make changes in the parser_module to match the account names and categories.
 4. To train your data add a text file with lines of the following form
 `__label__<category>__<sub category> <VENDOR/Account name> `
 5. Once you have this training data run the file `train_fasttext.py`. This should generate the trained model in `models/`. This is trained based on https://fasttext.cc/
 6. Once training is done run the `telegram-bot-interpreter.py`. Provide the messages to the bot and you should see responses with categorisation and the data/import.xlsx