import os
from pymongo import MongoClient

# mongodb+srv://root:<password>@dragonflyclustertest.eyl37.mongodb.net/myFirstDatabase?retryWrites=true&w=majority
# mongodb://root:pass12345@mongodb:27017
client = MongoClient(
    os.environ.get("MONGO_DRIVER") + "://" +
    os.environ.get("MONGO_USERNAME") + ":" +
    os.environ.get("MONGO_PASSWORD") + "@" +
    os.environ.get("MONGO_HOST") +
    # ":" + os.environ.get("MONGO_PORT") +
    "/" + os.environ.get("MONGO_DB_NAME") +
    "?" + os.environ.get("MONGO_CX_OPTIONS")
)
db = client[os.environ.get("MONGO_DB_NAME")]

# if no events time series shiny mongo collection *_* -> create it!
if os.environ.get("COLLECTION_EVENTS") not in db.list_collection_names():
    db.create_collection(
        'events',
        timeseries={
            'timeField': 'timestamp',
            'metaField': 'metadata',
            'granularity': 'hours'
        }
    )


def get_db_connection():
    return db
