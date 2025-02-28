import random

with open('dices.txt', 'r', encoding='utf-8') as file:
    Dices = (file.read().split('\n'))


def generate_board():
    n = 4
    random.shuffle(Dices)
    board = [[Dices[j * n + i][random.randint(0, 5)] for i in range(n)] for j in range(n)]
    return board
