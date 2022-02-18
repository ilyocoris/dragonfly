import os
from pymongo import MongoClient

# mongodb+srv://root:<password>@dragonflyclustertest.eyl37.mongodb.net/myFirstDatabase?retryWrites=true&w=majority
# mongodb://root:pass12345@mongodb:27017
client = MongoClient(
    # os.environ.get("MONGO_DRIVER") + "://" +
    # os.environ.get("MONGO_USERNAME") + ":" +
    # os.environ.get("MONGO_PASSWORD") + "@" +
    # os.environ.get("MONGO_HOST") +
    # # ":" + os.environ.get("MONGO_PORT") +
    # "/" + os.environ.get("MONGO_DB_NAME") +
    # "?" + os.environ.get("MONGO_CX_OPTIONS")
    os.getenv("MONGO_CONNECTION_STRING")
)
db = client[os.environ.get("MONGO_DB_NAME")]

# if no events time series, create it!
if os.environ.get("COLLECTION_EVENTS") not in db.list_collection_names():
    db.create_collection(
        os.environ.get("COLLECTION_EVENTS"),
        # timeseries={
        #     'timeField': 'timestamp',
        #     'metaField': 'metadata',
        #     'granularity': 'hours'
        # }
    )

# if os.environ.get("COLLECTION_SCRAPING_REDDIT") not in db.list_collection_names():
#     db.create_collection(
#         os.environ.get("COLLECTION_SCRAPING_REDDIT")
#     )


def get_db_connection():
    return db
