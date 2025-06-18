
import re

def cleanMarkdown(text):
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

# You can keep log_transaction and archive_and_reset_file here if you want.
