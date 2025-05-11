import os
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from dotenv import load_dotenv
load_dotenv()



class MongoDB:
    _initiated = None
    def __init__(self):
        username = os.getenv("MONGODB_USERNAME")
        if username is None:
            raise Exception("MONGODB_NAME not set")
        
        password = os.getenv("MONGODB_PASSWORD")
        if password is None:
            raise Exception("MONGODB_PASSWORD not set")
        
        host = os.getenv("MONGODB_HOST")
        if host is None:
            raise Exception("MONGODB_HOST not set")
        
        
        uri = f"mongodb://{username}:{password}@mongodb-service:27017" #mongodb-service
        print("Mongodb_uri: ",uri)


        self.client : MongoClient = MongoClient(uri)
        self.database : Database  = self.client.facedetection

    def get_collection(self,collection : str) -> Collection:
        return self.database[collection]
    
    def health_check(self):
        try:
            return self.client.admin.command("ping")
            
        except Exception as e:
            return {"error": str(e)}


def MongoInit():
    if MongoDB._initiated is None:
        MongoDB._initiated = MongoDB()
    return MongoDB._initiated