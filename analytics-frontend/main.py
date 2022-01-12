import json
import requests
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from mongodb import get_db_connection

st.markdown(
    "## DragonFly :dragon: :honeybee:")
st.write("#### A framework for real time entity sentiment analysis.")

#st.write("Please refer to [this](https://dev.to/ilyocoris/mongodb-submission-post-placeholder-title-1ah3?preview=13c736b16298e7b27f608916325d62dcd027523c51ad607e939723845003801e8c3a7cfb9c27d762dd92642f0ce0ee442d3654235c9ea64333727cfa) write-up for a more in depth explanation of the project.")

st.write("This allows us to scrape and trigger the NER+SA pipeline on a selection of stock-related subreddits. Although here we are using a frontend button, this api call should be made every X time, in order to build a comprehensive timeline of the comments on the stock market over a period of time.")

subreddits = st.multiselect(
    "Subreddits to scrape:",
    ["stocks",
     "StockMarket",
     "wallstreetbets",
     "pennystocks",
     "investing",
     "Wallstreetbetsnew",
     "options"]
)


def send_reddit_scraping_request():
    print("Subreddits to scrape:", subreddits)
    request_body = {
        "url_list": []
    }
    for subreddit in subreddits:
        request_body["url_list"].append({
            "project_id": "000000000000000000000000",
            "url": "https://www.reddit.com/r/" + subreddit + "/",
            "url_metadata": {"type": "subreddit", "post_limit": 50}
        })
        response = requests.post(
            "http://api:6969/process_urls", data=json.dumps(request_body))


send_request = st.button("SCRAPE!")
if send_request:
    send_reddit_scraping_request()


st.write("### Plot data for some stocks")

db = get_db_connection()


def get_top_entities():
    entities = db.events.aggregate([
        {"$match": {"event.type": "opinion"}},
        {
            "$group": {
                "_id": "$event.entity", "count": {"$sum": 1}
            }
        }])
    df = pd.DataFrame(entities)
    df = df.rename(columns={"_id": "entity"})
    return list(df.sort_values(by=["count"], ascending=False, ignore_index=True).head(10)["entity"])


def altair_opinion_barplot(entity):
    # get data from db
    data = {}
    to_idx = {"negative": 0, "neutral": 1, "positive": 2}
    for event in db.events.find({"event.entity": entity, "event.type": "opinion"}):
        str_date = str(event["timestamp"])[:10]
        if str_date not in data:
            data[str_date] = [0, 0, 0]
        data[str_date][to_idx[event["event"]["value"]]] += 1
    # to barchart format
    df = []
    for date in data.keys():
        for i in range(3):
            df.append({
                "date": date,
                "opinion": ["negative", "neutral", "positive"][i],
                "count": data[date][i]
            })
    df = pd.DataFrame(df)
    # return plot
    return alt.Chart(df).mark_bar().encode(
        x='date',
        y='sum(count)',
        color='opinion'
    ).properties(
        title='Opinion data for ' + entity
    )


col1, col2 = st.columns(2)
entity = col1.radio("Some entities", get_top_entities())
col2.altair_chart(altair_opinion_barplot(entity), use_container_width=True)
