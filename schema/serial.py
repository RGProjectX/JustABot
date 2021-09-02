
# Used to convert pymongo object to dict or proper json to handle _id = ObjectID('')

def serializeDict(item) -> dict:
    return{**{i:str(item[i]) for i in item if i=='_id'},**{i:item[i] for i in item if i!='_id'}}

def serializeList(items) -> list:
    return [serializeDict(item) for item in items]
