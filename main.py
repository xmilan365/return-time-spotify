# imports
import requests
import config
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Ids
SPOTIFY_CLIENT_ID = config.sp_client_id
SPOTIFY_CLIENT_SECRET = config.sp_client_secret

# main input
year_in_time = input("What year you would like to travel to? Type the date in this format YYYY-MM-DD: ")

# get songs popular in that year
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="http://example.com",
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt"
    )
)
user_id = sp.current_user()["id"]

request = requests.get(f"https://www.billboard.com/charts/hot-100/{year_in_time}")
request.raise_for_status()
content = request.text

soup = BeautifulSoup(content, "html.parser")
song_soup = soup.find_all(name="h3", id="title-of-a-story", class_="c-title a-no-trucate a-font-primary-bold-s u-letter"
                                                                   "-spacing-0021 lrv-u-font-size-18@tablet lrv-u-font"
                                                                   "-size-16 u-line-height-125 u-line-height-"
                                                                   "normal@mobile-max a-truncate-ellipsis u-max-width-"
                                                                   "330 u-max-width-230@tablet-only")
song_list = [song.getText()[1:-1] for song in song_soup]

song_uris = []

year = year_in_time.split("-")[0]

for song in song_list:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        # print(f"{song} doesn't exist in Spotify. Skipped.")
        pass

playlist_id = sp.user_playlist_create(user=user_id,
                        name=f"{year_in_time} Billboard 100",
                        public=False)["id"]

sp.user_playlist_add_tracks(user=user_id,
                            playlist_id=playlist_id,
                            tracks=song_uris,
                            position=None)
