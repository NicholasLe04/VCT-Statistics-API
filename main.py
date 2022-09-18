from fastapi import FastAPI
from scrape import Scrapper

app = FastAPI()
matches = Scrapper()


@app.get("/{number}/{match}")
async def read_item(number, match):
    return matches.gameStats(number, match)