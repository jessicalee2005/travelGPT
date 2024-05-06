import requests
import json
from pydantic import BaseModel, Field
from langchain.agents import tool
from dotenv import load_dotenv, find_dotenv
import os

class GetCastDetailsInput(BaseModel):
    id: str = Field(..., title="ID", description="ID of the movie or the TV show")


class GetRatingInput(BaseModel):
    id: str = Field(..., title="ID", description="ID of the movie or the TV show")


class GetAwardsInput(BaseModel):
    id: str = Field(..., title="ID", description="ID of the movie or the TV show")


class GetPlotInput(BaseModel):
    id: str = Field(..., title="ID", description="ID of the movie or the TV show")

class GetInfo(BaseModel):
    name: str = Field(..., title="Name", description="Name of the movie or the TV show")

class GetPosterImages(BaseModel):
    name: str = Field(..., title="Name", description="Name of the movie or the TV show")

def get_headers():
    _ = load_dotenv(find_dotenv())  # read local .env file
    #return {
    #    "Authorization": f"Bearer {os.getenv('TMDB_BEARER_TOKEN')}",
    #}
    #print('tmdb token:' + os.getenv('TMDB_API_TOKEN'))
    return {
    'accept': 'application/json',
    'Authorization': 'Bearer '+ os.getenv('TMDB_API_TOKEN')
    }

from utils.logger import logger

foundMovie = {}

def get_id(name: str) -> str:
    """Get the ID of the movie or the TV show from the name"""

    url = "https://api.themoviedb.org/3/search/multi?"
    #'https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=1&sort_by=popularity.desc';

    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer ' + os.getenv('TMDB_API_TOKEN')
    }

    querystring = {"query":name}
    try:
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
        # Find the first item with an 'id' key and break the loop
        for item in data['results']:
            if 'id' in item:
                movie_id = item['id']
                foundMovie = item
                print(foundMovie)
                break
        logger.debug(f"Movie ID was succesfully retrieved. Movie ID: {movie_id}")
        return movie_id
    except Exception as e:
        logger.debug(f"Not able to find the movie ID for the movie: {name}")
        logger.debug(f"Error: {e}")
        return f"Movie ID not found for the movie: {name}"

@tool(args_schema=GetCastDetailsInput)
def get_cast_details(id: str) -> str:
    """Get the cast details of the movie or the TV show from the ID"""

    url = "https://api.themoviedb.org/3/movie/"+id+"/credits"
    querystring = {"id": id}
    headers = get_headers()
    response = requests.get(url, headers=headers)
    print(response.json()['cast'])
    logger.debug(f"Inside the get_cast_details function")
    if response.status_code != 200:
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response headers: {response.headers}")
        logger.debug(f"Response body: {response.text}")
        return f"Not able to retrieve the cast for the movie with ID: {id}. Response text: {response.text}"
    else:
        logger.debug(f"Cast retrieved successfully")
    cast = response.json()['cast']
    crew = response.json()['crew']
    logger.debug(response.json())
    ret = ""
    if(len(cast) >0 ):
        logger.debug(cast['edges'])
        for edge in cast['edges']:
            ret += f"""Actor Name: {edge['node']['name']['nameText']['text']}\n"""
            ret += "------------------------------------------------------\n"
        logger.debug(f"Returning the cast details succesfully")
        return ret
    elif(len(response.json()['crew']) > 0):
        ret += "Directed by:" + crew[0]['name'] + "\n"
        #ret += response.json()['overview']
        return ret
    else:
        return "Not found. Please try another question."


## Rating is not supported by themoviedb.org's API
# @tool(args_schema=GetRatingInput)
# def get_rating(id: str) -> str:
#     """Get the rating of the movie or the TV show from the ID"""

#     url = "https://imdb-com.p.rapidapi.com/title/ratings"

#     querystring = {"tconst": id}
#     headers = get_headers()
#     response = requests.get(url, headers=headers, params=querystring)
#     if response.status_code != 200:
#         logger.debug(f"Response status code: {response.status_code}")
#         logger.debug(f"Response headers: {response.headers}")
#         logger.debug(f"Response body: {response.text}")
#         return f"Not able to retrieve the rating for the movie with ID: {id}. Response text: {response.text}"
#     else:
#         logger.debug(f"Rating retrieved successfully")
#     data = response.json()
#     aggregate_rating = data['data']['entityMetadata']['ratingsSummary']['aggregateRating']
    
#     # Initialize the summary string
#     summary = f"Aggregate Rating: {aggregate_rating}\n\n"
    
#     # Check if histogramData exists
#     if 'histogramData' in data['data']['entityMetadata']:
#         # Extract the histogram data
#         histogram_data = data['data']['entityMetadata']['histogramData']
        
#         # Extract the country-specific ratings
#         country_ratings = histogram_data['countryData']
        
#         # Add country-specific ratings to the summary
#         summary += "Country-specific Ratings:\n"
#         for country_rating in country_ratings:
#             summary += f"{country_rating['displayText']}: {country_rating['aggregateRating']} (Votes: {country_rating['totalVoteCount']})\n"
        
#         # Extract the histogram values
#         histogram_values = histogram_data['histogramValues']
        
#         # Add histogram values to the summary
#         summary += "\nHistogram Values:\n"
#         for histogram_value in histogram_values:
#             summary += f"Rating: {histogram_value['rating']} (Votes: {histogram_value['formattedVoteCount']})\n"
#     # Print the entire output string
#     logger.debug(f"Returning the rating details succesfully")
#     return summary


@tool(args_schema=GetAwardsInput)
def get_awards(id: str) -> str:
    """Get the awards of the movie or the TV show from the ID"""

    #url = "https://imdb146.p.rapidapi.com/v1/title/"
    url = "https://api.themoviedb.org/3/find/"+id

    querystring = {"id": id}
    headers = get_headers()
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response headers: {response.headers}")
        logger.debug(f"Response body: {response.text}")
        return f"Not able to retrieve the awards for the movie with ID: {id}. Response text: {response.text}"
    data = response.json()
    print(data['wins'])
    print(data['nominations'])
    print(data['prestigiousAwardSummary'])
    # Create a summary string
    summary = f"Total Nominations: {data['wins']['total']}\n" \
          f"Total Awards: {data['wins']['total']}\n" \
          f"Number of Wins: {data['prestigiousAwardSummary']['wins']}\n" \
          f"Last Prestigious Award: {data['prestigiousAwardSummary']['award']['text']} (ID: {data['prestigiousAwardSummary']['award']['id']})"
    logger.debug(f"Returning the awards details succesfully")
    return summary
    # # Extract the title, year, and highlighted award information
    # title = data["title"]
    # year = data["year"]
    # highlighted_award = data["awardsSummary"]["highlighted"]["awardName"]
    # highlighted_award_count = data["awardsSummary"]["highlighted"]["count"]
    # highlighted_award_is_winner = (
    #     "Winner" if data["awardsSummary"]["highlighted"]["isWinner"] else "Nominated"
    # )

    # # Append the title, year, and highlighted award information to the summary string
    # summary += f"Title: {title}\n"
    # summary += f"Year: {year}\n"
    # summary += (
    #     f"Highlighted Award: {highlighted_award} ({highlighted_award_count} times)\n"
    # )
    # summary += f"Status: {highlighted_award_is_winner}\n"

    # # Append the other nominations and wins count to the summary string
    # summary += (
    #     f"Other Nominations Count: {data['awardsSummary']['otherNominationsCount']}\n"
    # )
    # summary += f"Other Wins Count: {data['awardsSummary']['otherWinsCount']}\n"

    # # Append the highlighted ranking information to the summary string
    # summary += f"Highlighted Ranking: {data['highlightedRanking']['label']} (Rank: {data['highlightedRanking']['rank']})\n"
    


@tool(args_schema=GetPlotInput)
def get_plot(id: str) -> str:
    """Get the plot of the movie or the TV show from the ID"""

    if foundMovie:
        print(foundMovie)
        return foundMovie['overview']
    #url = "https://imdb146.p.rapidapi.com/v1/title/"
    url = "https://api.themoviedb.org/3/movie/"+id  #+"?language=en-US"
    headers = get_headers()
    print("plot")
    print(url)
    response = requests.get(url, headers=headers)
    print(response.json())
    if response.status_code != 200:
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response headers: {response.headers}")
        logger.debug(f"Response body: {response.text}")
        return f"Not able to retrieve the plot for the movie with ID: {id}. Response text: {response.text}"
    data = response.json()['overview']
    # Initialize an empty string to hold the formatted output
    plots_summary = response.json()['overview'] #['plotText']['plainText']

    # # Iterate over the plots and append each plot's text to the summary string
    # for plot in data["plots"][:5]:
    #     plots_summary += plot["text"] + "\n\n"
    logger.debug(f"Returning the plot details succesfully")
    return plots_summary  # Return the formatted output

@tool(args_schema=GetInfo)
def get_info(name: str) -> str:
    """Return overview of the movie or TV program"""
    url = "https://api.themoviedb.org/3/search/movie?"
    #'https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=1&sort_by=popularity.desc';

    #headers = get_headers()
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer ' +  os.getenv('TMDB_API_TOKEN')
    }

    querystring = {"query":name}
    try:
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
        # Find the first item with an 'id' key and break the loop
        for item in data['results']:
            if 'id' in item:
                movie_id = item['id']
                foundMovie = item
                print(foundMovie)
                break
        logger.debug(f"Movie ID was succesfully retrieved. Movie ID: {movie_id}")
        return foundMovie
    except Exception as e:
        logger.debug(f"Not able to find the movie ID for the movie: {name}")
        logger.debug(f"Error: {e}")
        return f"Movie info not found for the movie: {name}"
    
@tool(args_schema=GetPosterImages)
def get_images(name: str) -> str:
    """Get the poster and images of the movie or the TV show from the name"""

    #url = "https://imdb146.p.rapidapi.com/v1/title/"
    url = "https://api.themoviedb.org/3/search/movie?"

    querystring = {"query": name}
    headers = get_headers()
    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code != 200:
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response headers: {response.headers}")
        logger.debug(f"Response body: {response.text}")
        return f"Not able to retrieve the awards for the movie with ID: {id}. Response text: {response.text}"
    data = response.json()
    foundMovie = None
    for item in data['results']:
        if name in item['title']:
            movie_id = item['id']
            foundMovie = item
            print(foundMovie)
            break

    # Create a summary string
    prefix = "https://images.tmdb.org/t/p/original"
    if not foundMovie:
        imageUrl = "not found"
    else:    
        imageUrl = foundMovie['poster_path']
        if not imageUrl:
            imageUrl = foundMovie['backdrop_path']
        if not imageUrl:
            imageUrl = "Not found"    
        else:
            imageUrl = prefix + imageUrl
    logger.debug(f"Returning the image succesfully")
    print(imageUrl)
    return imageUrl