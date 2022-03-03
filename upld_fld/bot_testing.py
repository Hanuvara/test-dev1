import html2text

bot_answers = {
    "name": "name is name",
    "harshil": "I am also Harshil"
}


def get_bot_output(bot_message=''):
    word = str(html2text.html2text(bot_message)).lower()

    for key, value in bot_answers.items():
        if key in word:
            return value
    return False
