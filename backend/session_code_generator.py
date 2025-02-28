import random
import math


def generate_session_code():
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    code = ''
    for i in range(6):
        random_index = math.floor(random.random() * len(characters))
        code += characters[random_index]
    return code
