import numpy as np

players = 3

cards = {
    "deck": [color for color in range(9) for _ in range(12)], # 9 colors, 12 of each
    "faceup": [[] for _ in range(5)],
    "discards": [],
    "hands": [[] for _ in range(players)],
    "goals": [] #importgoals; % read goal cards in from the .txt
}
cards["deck"].extend([0, 0]) # extra two rainbows

def shuffle_deck():
     cards["deck"] = list(np.random.permutation(cards["deck"]))

def init_faceup():
    cards["faceup"] = cards["deck"][0:5]
    cards["deck"] = cards["deck"][5:]
    cards_check()

def deal_out():
    [pick_deck(turn) for _ in range(4) for turn in range(players)]

def cards_check():
    if np.shape(np.nonzero(np.equal(cards["faceup"], 0)))[1] >= 3:
        print("discarding faceups", cards["faceup"])
        cards["discards"].extend(cards["faceup"])
        init_faceup()
    if len(cards["deck"]) < 5:
        cards["deck"].extend(cards["discards"])
        cards["discards"].clear()
        shuffle_deck()

def spend_card(card):
    cards["discards"].extend(card)
    cards["deck"].pop(cards["deck"].index(card))

def pick_faceup(turn, card):
    cards["hands"][turn].append(card)
    cards["faceup"].pop(cards["faceup"].index(card))
    cards["faceup"].append(cards["deck"][0])
    cards["deck"].pop(0)
    cards_check()

def pick_deck(turn):
    cards["hands"][turn].append(cards["deck"][0])
    cards["deck"].pop(0)
    cards_check()
