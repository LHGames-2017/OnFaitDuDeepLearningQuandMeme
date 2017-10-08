from flask import Flask, request
from structs import *
import json
import math
from A2C import Environment, Brain
import random

app = Flask(__name__)


def create_action(action_type, target):
    actionContent = ActionContent(action_type, target.__dict__)
    return json.dumps(actionContent.__dict__)

def create_move_action(target):
    return create_action("MoveAction", target)

def create_attack_action(target):
    return create_action("AttackAction", target)

def create_collect_action(target):
    return create_action("CollectAction", target)

def create_steal_action(target):
    return create_action("StealAction", target)

def create_heal_action():
    return create_action("HealAction", "")

def create_purchase_action(item):
    return create_action("PurchaseAction", item)

def deserialize_map(serialized_map):
    """
    Fonction utilitaire pour comprendre la map
    """
    serialized_map = serialized_map[1:]
    rows = serialized_map.split('[')
    column = rows[0].split('{')
    deserialized_map = [[Tile() for x in range(20)] for y in range(20)]
    for i in range(len(rows) - 1):
        column = rows[i + 1].split('{')

        for j in range(len(column) - 1):
            infos = column[j + 1].split(',')
            end_index = infos[2].find('}')
            content = int(infos[0])
            x = int(infos[1])
            y = int(infos[2][:end_index])
            deserialized_map[i][j] = Tile(content, x, y)

    return deserialized_map


def take_action(state, R):
    return ENV_RES.runStep(state, R)


def make_state_space(map, x, y):
    state = []
    R = [25, 25]
    tmp_x, tmp_y = [-1, -1], [-1, -1]

    for rows in map:
        for tile in rows:
            if tile.Content != None:
                if tile.Content == 6:
                    if (math.sqrt(math.pow(x - tile.X,2) + math.pow(y - tile.Y, 2)) < R[0]) & (math.sqrt(math.pow(x - tile.X,2) + math.pow(y - tile.Y, 2)) > 0):
                        tmp_x[0], tmp_y[0] = tile.X, tile.Y
                        R[0] = math.sqrt(math.pow(x - tile.X,2) + math.pow(y - tile.Y, 2))
                if tile.Content == 1:
                    if math.sqrt(math.pow(x - tile.X, 2) + math.pow(y - tile.Y, 2)) < R[1]:
                        tmp_x[1], tmp_y[1] = tile.X, tile.Y
                        R[1] = math.sqrt(math.pow(x - tile.X, 2) + math.pow(y - tile.Y, 2))

                state.append(tile.Content)

    return state, R, tmp_x, tmp_y

# L'algorithme de Deep Reinforcement Learning de style A2C https://blog.openai.com/baselines-acktr-a2c/
# Apprend a ce rapprocher de joueur sur la carte, recevant des recompenses lorsqu'il s'en rapproche et
# attaquant tout mur ou joueur etant suffisament proche.

# Il s'agit de mon implementation de l'algorithme a partir de la base d'un autre algorithme de deep reinforcement learning

def ai_logic(x, y, deserialized_map):

    ACTIONS_DICT = {0: create_move_action(Point(x, y + 1)),
                    1: create_move_action(Point(x + 1, y)),
                    2: create_move_action(Point(x, y - 1)),
                    3: create_move_action(Point(x - 1, y))}
    state, R, tmp_x, tmp_y = make_state_space(deserialized_map, x, y)
    if (R[0] == 1):
        print('killing player')
        return create_attack_action(Point(tmp_x[0], tmp_y[0]))
    elif (R[1] == 1):
        print('killing wood')
        return create_attack_action(Point(tmp_x[1], tmp_y[1]))
    else:
        actions = take_action(state, R[0])
        print('stalking player')
        print(ACTIONS_DICT[actions])
        return ACTIONS_DICT[actions]

def bot():
    """
    Main de votre bot.
    """
    map_json = request.form["map"]
    # Player info

    map_json = json.loads(map_json)
    p = map_json["Player"]
    pos = p["Position"]
    x = pos["X"]
    y = pos["Y"]

    serialized_map = map_json["CustomSerializedMap"]
    deserialized_map = deserialize_map(serialized_map)
    return ai_logic(x, y, deserialized_map)

@app.route("/", methods=["POST"])
def reponse():
    """
    Point d'entree appelle par le GameServer
    """
    return bot()

if __name__ == "__main__":
    ENV_RES = Environment()
    BRAIN_RES = Brain('killer')
    ENV_RES.make_agent(BRAIN_RES)

    app.run(host="0.0.0.0", port=3000)
