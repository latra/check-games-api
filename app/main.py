import requests
import fastapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from typing import List

import os 
HEADERS = {
    "X-Riot-Token": os.getenv("API_KEY")
}

def get_puuid(nick, tag):
    url = "https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{}/{}".format(nick, tag)
    result = requests.get(url=url, headers=HEADERS)
    if result.status_code == 200:
        return result.json()["puuid"]
    else:
        return None
def get_total_games(puuid):
    start = 0
    url = "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{}/ids".format(puuid)
    parameters = {
        "type": "ranked",
        "queue": 420,
        "startTime": 1640995200,
        "start": start,
        "count": 100
    }
    result = requests.get(url= url, params=parameters, headers=HEADERS)
    print(result)

    while len(result.json()) == 100:
        start += 100
        parameters = {
            "type": "ranked",
            "start": start,
            "count": 100
        }
        result = requests.get(url= url, params=parameters, headers=HEADERS)
    return start + len(result.json())


app = fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Reemplaza "https://tudominio.com" con el dominio de tu página web
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/games/")
def get_games(summoner: str, tag: str):
    puuid = get_puuid(summoner, tag)
    if not puuid or puuid == None:
        raise HTTPException(status_code=404, detail="Item not found")
    return get_total_games(puuid=puuid)

@app.post("/main/")
def get_games(summoners: List[str]):
    main_acc = ""
    max_games = -1

    for summoner_full in summoners:
        summoner, tag = summoner_full.split("#")
        puuid = get_puuid(summoner, tag)
        summoner_games = get_total_games(puuid=puuid)
        if summoner_games > max_games:
            max_games = summoner_games
            main_acc = summoner_full 
    return main_acc


