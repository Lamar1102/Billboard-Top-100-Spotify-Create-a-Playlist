import requests
from bs4 import BeautifulSoup
import lxml
from config import CLIENT_ID,CLIENT_SECRET


need_response = True
while need_response:
    user_chosen_date = input("What year would you like to travel to in this format YYYY-MM-DD:?")

    response = requests.get(f"https://www.billboard.com/charts/hot-100/{user_chosen_date}")
    need_response = False

    if response.status_code == 404:
        need_response = True

top_100 = response.text
soup = BeautifulSoup(top_100, "lxml")

artists = soup.find_all(class_="chart-element__information__artist text--truncate color--secondary")
artists_list = []

for artist in artists:
    artist = artist.string
    if "Featuring" in artist:
        artist = artist.replace("Featuring", "")
    artists_list.append(artist)

songs = soup.find_all(class_="chart-element__information__song text--truncate color--primary")
songs = [song.string for song in songs]

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import pprint

SPOTIPY_CLIENT_SECRET = CLIENT_SECRET


spotify = SpotifyOAuth(client_id=CLIENT_ID,client_secret=CLIENT_SECRET,
                       redirect_uri="http://example.com",scope="playlist-modify-public",cache_path="token.txt")

response = spotify.get_auth_response()

code = spotify.get_authorization_code(response=response)
token_data = spotify.get_access_token(code)

with open("token.txt","r") as token_data:
    token1= token_data.read()
token1= token1.strip('{,}')
token1= token1.split(" ")

TOKEN = token1[1].strip('",,')

auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID,client_secret=CLIENT_SECRET)
client = spotipy.Spotify(auth=TOKEN, client_credentials_manager=auth_manager,oauth_manager=spotify)

user_id = client.current_user()["id"]


spotify_results = spotipy.Spotify(auth_manager=auth_manager,auth=TOKEN,client_credentials_manager=auth_manager,
                                  oauth_manager=spotify)

songs_uri_list = []
for i in range(100):
    results = spotify_results.search(q=f"track:{songs[i]} artist:{artists_list[i]}",type = "track")
    try:
        uri=results["tracks"]["items"][2]["uri"]
        songs_uri_list.append(uri)
    except IndexError:
        try:
            uri = results["tracks"]["items"][1]["uri"]
            songs_uri_list.append(uri)
        except IndexError:
            try:
                uri = results["tracks"]["items"][0]["uri"]
                songs_uri_list.append(uri)
            except IndexError:
                pass

create_playlist_id = spotify_results.user_playlist_create(user=user_id,name=f"{user_chosen_date} Jams",collaborative=False,
                                                       description="Jams")
playlist_id = create_playlist_id["id"]

spotify_results.playlist_add_items(playlist_id=playlist_id,items=songs_uri_list)



