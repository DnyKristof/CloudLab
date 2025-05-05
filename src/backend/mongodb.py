import os
from pymongo import MongoClient



class MongoDB:
    _initiated = None
    def __init__(self):
        username = os.getenv("MONGODB_USERNAME")
        if username is None:
            raise Exception("MONGODB_NAME not set")
        
        password = os.getenv("MONGODB_PASSWORD")
        if password is None:
            raise Exception("MONGODB_PASSWORD not set")
        
        uri = f"mongodb://{username}:{password}@mongodb-service:27017" #mongodb-service

        self.client = MongoClient(uri)
        self.database = self.client.facedetection

    def get_collection(self,collection):
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