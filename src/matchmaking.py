import json

from flask import Blueprint, request
from utils import r, it_should_be_there_soon
from random import getrandbits
from utils import r, it_should_be_there_soon, get_id

matchmaking = Blueprint('matchmaking', __name__, url_prefix='/matchmaking/v1')


@matchmaking.route('/createChallenge', methods=['POST'])
def create_challenge():
    data = request.get_json()
    player_data = json.loads(data['sd'])
    challenger = player_data['PlayerId']
    challenged = data['o']
    seed_contribution = getrandbits(60)
    r.setex(challenger + "-sd", 20, data['sd'])
    r.setex(challenger + "-seed", 20, seed_contribution)
    return {
        "ty": "JoinMatch",
        "eta": 0,
        "gi": challenged
    }


@matchmaking.route('/joinMatch', methods=['POST'])
def join_match():
    data = request.get_json()
    gi = data['gi']
    return {
        "ty": "MatchReady",
        "sd": it_should_be_there_soon(gi + "-sd").decode(),
        "gi": gi,
        "or": 50
    }
@matchmaking.route('/queryStats', methods=['GET', 'POST'])
def query_stats():
    return {
        "wins": 0,
        "losses": 0,
        "mmr": 1600
    }

@matchmaking.route('/cancelMatch', methods=['GET', 'POST'])
def cancel_match():
    return {}

@matchmaking.route('/makeMatch', methods=['GET', 'POST'])
def make_match():
    data = request.get_json()
    pid = get_id()
    sd = json.dumps(data)

    r.setex(pid + "-sd", 60, sd)
    r.setex(pid + "-seed", 60, str(getrandbits(60)))

    
    matched = r.get(pid + "-matched")
    if matched:
        opponent = matched.decode()
        r.delete(pid + "-matched")
        return {
            "ty": "MatchReady",
            "sd": r.get(opponent + "-sd").decode(),
            "gi": opponent,
            "or": 50
        }

    
    waiting = r.get("waiting-player")
    if waiting and waiting.decode() != pid:
        opponent = waiting.decode()
        r.delete("waiting-player")
        # Notify opponent they got matched
        r.setex(opponent + "-matched", 60, pid)
        return {
            "ty": "MatchReady",
            "sd": r.get(opponent + "-sd").decode(),
            "gi": opponent,
            "or": 50
        }

   
    r.setex("waiting-player", 60, pid)
    return {
        "ty": "WaitingForMatch",
        "eta": 30,
        "gi": None
    }

@matchmaking.route('/matchPoll', methods=['GET', 'POST'])
def match_poll():
    return {}
