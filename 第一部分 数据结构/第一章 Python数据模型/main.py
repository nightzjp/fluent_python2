# -*- coding: utf-8 -*-

"""
@author: Mr_zhang
@software: PyCharm
@file: main.py
@time: 2023/5/5 21:25
"""


# 1.2 一摞Python风格的纸牌
import collections


Card = collections.namedtuple("Card", ["rank", "suit"])


class FrenchDesk:
    ranks = [str(n) for n in range(2, 11)] + list("JQKA")
    suits = "spades diamonds clubs hearts".split()

    def __init__(self):
        self._card = [Card(rank, suit) for suit in self.suits for rank in self.ranks]

    def __len__(self):
        return len(self._card)

    def __getitem__(self, item):
        return self._card[item]


beer_card = Card("7", "diamonds")
print(beer_card)

deck = FrenchDesk()
print(len(deck))

print(deck[0])
print(deck[-1])

from random import choice
print(choice(deck))
print(choice(deck))
print(choice(deck))


print(deck[:3])
print(deck[12::13])


for card in deck:
    print(card)

for card in reversed(deck):
    print(card)

print(Card("7", "hearts") in deck)
print(Card("11", "hearts") in deck)

suit_values = dict(spades=3, hearts=2, diamonds=1, clubs=0)


def spades_high(card):
    rank_value = FrenchDesk.ranks.index(card.rank)
    return rank_value * len(suit_values) + suit_values[card.suit]


for card in sorted(deck, key=spades_high):
    print(card)


# 1.3.1 模拟数值类型
from math import hypot
class Vector:
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "Vector(%r,%r)" % (self.x,self.y)

    def __abs__(self):
        return hypot(self.x,self.y)

    def __bool__(self):
        return bool(abs(self))

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Vector(x,y)

    def __mul__(self, other):
        return Vector(self.x * other, self.y * other)


v1 = Vector(2, 4)
v2 = Vector(2, 1)
print(v1 + v2)

v = Vector(3, 4)
print(abs(v))

print(v * 3)

print(abs(v * 3))


v1 = Vector(3, 4)
v2 = Vector(2, 1)
print(v1 + v2)

v = Vector(3, 4)
print(abs(v))

print(v * 3)
print(abs(v * 3))