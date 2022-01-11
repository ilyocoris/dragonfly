import json
import requests
import pandas as pd
import streamlit as st

st.markdown(
    "## DragonFly :dragon: :honeybee:")
st.write("#### A framework for real time entity sentiment analysis.")

#st.write("Please refer to [this](https://dev.to/ilyocoris/mongodb-submission-post-placeholder-title-1ah3?preview=13c736b16298e7b27f608916325d62dcd027523c51ad607e939723845003801e8c3a7cfb9c27d762dd92642f0ce0ee442d3654235c9ea64333727cfa) write-up for a more in depth explanation of the project.")

st.write("This allows us to scrape and trigger the NER+SA pipeline on a selection of stock-related subreddits. Although here we are using a frontend button, this api call should be made every X time, in order to build a comprehensive timeline of the comments on the stock market over a period of time.")

subreddits = st.multiselect("Subreddits to scrape:", ["stocks", "StockMarket"])


def send_reddit_scraping_request():
    print("Subreddits to scrape:", subreddits)
    request_body = {
        "url_list": []
    }
    for subreddit in subreddits:
        request_body["url_list"].append({
            "project_id": "000000000000000000000000",
            "url": "https://www.reddit.com/r/" + subreddit + "/",
            "url_metadata": {"type": "subreddit"}
        })
        response = requests.post(
            "http://api:6969/process_urls", data=json.dumps(request_body))


send_request = st.button("SCRAPE!", on_click=send_reddit_scraping_request)
