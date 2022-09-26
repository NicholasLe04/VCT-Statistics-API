from fastapi import FastAPI
from scrape import Scrapper

app = FastAPI()
matches = Scrapper()


@app.get("/{match_id}")
async def read_item(match_id):
    return matches.getMatchStats(match_id)