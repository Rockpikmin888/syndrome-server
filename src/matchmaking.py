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

    r.setex(pid + "-sd", 120, sd)
    r.setex(pid + "-seed", 120, str(getrandbits(60)))

    
    matched = r.get(pid + "-matched")
    if matched:
        opponent = matched.decode()
        r.delete(pid + "-matched")
        opp_sd = r.get(opponent + "-sd")
        if opp_sd:
            return {
                "ty": "MatchReady",
                "sd": opp_sd.decode(),
                "gi": opponent,
                "or": 50
            }

   
    claimed = r.setnx("waiting-player", pid)
    if claimed:
        r.expire("waiting-player", 60)
        return {
            "ty": "WaitingForMatch",
            "eta": 30,
            "gi": None
        }
    else:
        
        opponent = r.getdel("waiting-player")
        if opponent and opponent.decode() != pid:
            opponent = opponent.decode()
            r.setex(opponent + "-matched", 120, pid)
            return {
                "ty": "MatchReady",
                "sd": r.get(opponent + "-sd").decode(),
                "gi": opponent,
                "or": 50
            }
        else:
          
            r.setnx("waiting-player", pid)
            r.expire("waiting-player", 60)
            return {
                "ty": "WaitingForMatch",
                "eta": 30,
                "gi": None
            }

@matchmaking.route('/matchPoll', methods=['GET', 'POST'])
def match_poll():
    return {}
