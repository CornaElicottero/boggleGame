

with open("russian.dic", 'r', encoding='utf-8') as file:
    Dictionary = file.read().split('\n')


def check_word(word):
    return word in Dictionary and word != ''
