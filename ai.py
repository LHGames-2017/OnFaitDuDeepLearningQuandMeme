from flask import Flask, request
from structs import *
import json
import numba
import math
from A2C import Environment, Brain

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
    return ENV_TEST.runStep(state, R)

def make_state_space(map, x, y):
    state = []
    R = 15
    tmp_x, tmp_y = -1, -1
    for rows in map:
        for tile in rows:
            if tile.Content != None:
                if tile.Content == 4:
                    if math.sqrt(math.pow(x - tile.X,2) + math.pow(y - tile.Y, 2)) < R:
                        tmp_x, tmp_y = tile.X, tile.Y
                        R = math.sqrt(math.pow(x - tile.X,2) + math.pow(y - tile.Y, 2))

                state.append(tile.Content)

    return state, R, tmp_x, tmp_y

def bot():
    """
    Main de votre bot.
    """
    map_json = request.form["map"]
    # print(map_json)
    # Player info

    #encoded_map = map_json.encode()
    map_json = json.loads(map_json)
    p = map_json["Player"]
    pos = p["Position"]
    x = pos["X"]
    y = pos["Y"]

    serialized_map = map_json["CustomSerializedMap"]
    deserialized_map = deserialize_map(serialized_map)
    state, R, tmp_x, tmp_y = make_state_space(deserialized_map, x, y)

    actions = take_action(state, R)
    ACTIONS_DICT = {0: create_move_action(Point(x, y + 1)),
                    1: create_move_action(Point(x + 1, y)),
                    2: create_move_action(Point(x, y - 1)),
                    3: create_move_action(Point(x - 1, y))}
    if(R == 1):
        print('collecting', p["TotalResources"])
        return create_collect_action(Point(tmp_x, tmp_y))
    return ACTIONS_DICT[actions]

@app.route("/", methods=["POST"])
def reponse():
    """
    Point d'entree appelle par le GameServer
    """
    return bot()

if __name__ == "__main__":
    ENV_TEST = Environment()
    brain = Brain()
    ENV_TEST.make_agent(brain)

    app.run(host="0.0.0.0", port=8080)