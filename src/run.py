from scraper import UniversityScraper
from flask_pymongo import pymongo
from scraper_api import ScraperAPIClient
from db import DB
import os

DBClient = pymongo.MongoClient(os.environ.get("DATABASE_URL"))


cursor = DBClient.uni


db = DB(cursor=cursor)

scraper = UniversityScraper(country = "Nicaragua")

unis = scraper.scrap()

for uni in unis:

    try:
        db.insertUniversity(uni)
    except Exception as err:
        print(err)
