import pymongo

client = pymongo.MongoClient('mongodb+srv://RG:HackEat12@cluster0.apkmv.mongodb.net/')
db = client['apiKey'] #DB Name For API Keys
collection = db['users'] #Collection Name

