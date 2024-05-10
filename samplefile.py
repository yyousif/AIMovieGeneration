import logging
import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()
from azure.cosmos import CosmosClient, PartitionKey
import azure.functions as func
import openai

# database information
ENDPOINT = os.getenv('endUrl')
KEY = os.getenv('cosmodbkey')
client = CosmosClient(url=ENDPOINT, credential=KEY)
database = client.get_database_client(os.getenv('DATABASE_NAME'))
container = database.get_container_client(os.getenv('CONTAINER_NAME'))

#openAI API
api_key = os.getenv('openaiapikey')
openai.api_key = api_key


def generate_summary(movie_name):
    response = openai.chat.completions.create(
        model = "gpt-3.5-turbo",
        messages=[
            {"role":"user", "content": f"Summarize the movie: {movie_name} in 2 sentences"}
            ],
        temperature=1,
        max_tokens = 200,
    )
    return response.choices[0].message.content

def getMoviesBySummary(title):
    movie_list = []
    for item in container.query_items(query = f'SELECT c.title, c.releaseYear, c.genre, c.coverUrl From c WHERE LOWER(c.title) = @title', parameters = [dict(name='@title', value = title.lower())], enable_cross_partition_query=True):
        movie_summary = generate_summary(item['title'])
        item['generatedSummary'] = movie_summary
        movie_list.append(item)
    return json.dumps(movie_list, indent = True)

title_input = input('Enter movie name: ')
print(getMoviesBySummary(title_input))
