from flask_pymongo import pymongo


class DB:

    def __init__(self, cursor):
        self.cursor = cursor

    def insertUniversity(self,data):

        collection = self.cursor.Universities

        if collection.find_one({"name":data["name"], "country":data["country"], "city":data["city"]}):
            raise Exception(f"University of name {data['name']} already exists")
        
        
        collection.insert_one(data)
        print(f"{data['name']} stored in database")
        return True