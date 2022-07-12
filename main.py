import requests
import spotipy
import os
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri='http://example.com',
        scope='playlist-modify-public playlist-read-private',
        show_dialog=True,
        cache_path='token.txt'
    )
)
user_id = sp.current_user()['id']
user_year = ''

correct_date = False
while not correct_date:
    user_year = input('What year would you like to travel to (YYYY-MM-DD)? ')
    year_split = user_year.split('-')
    user_year = user_year
    if len(user_year) > 10 or len(user_year) < 10 or year_split[1] > '12' or year_split[2] > '31':
        print('Please type a correct date')
    elif len(year_split[0]) < 4 or len(year_split[1]) < 2 or len(year_split[2]) < 2:
        print('Please type a date format')
    else:
        correct_date = True

ENTRY_URL = 'https://www.billboard.com/charts/hot-100/'
response = requests.get(ENTRY_URL + user_year)

soup = BeautifulSoup(response.text, 'html.parser')

song_names_h3 = soup.find_all('h3', id='title-of-a-story', class_='a-no-trucate')
artist_names_span = soup.find_all('span', class_=['a-no-trucate', 'u-letter-spacing-0021'])

song_names = [song.getText().strip('\n') for song in song_names_h3]
artist_names = [artist.getText().strip('\n') for artist in artist_names_span]

year = user_year.split('-')[0]

playlist_name = f'{user_year} Billboard Top 100'
user_playlist = sp.user_playlists(user_id)
playlist_exists = False

for playlist in user_playlist['items']:
    if playlist['name'] == playlist_name:
        playlist_exists = True
if playlist_exists:
    print('Playlist already exists')
elif not playlist_exists:
    song_ids = []
    for song in song_names:
        results = sp.search(q=f'track:{song}', type='track')
        try:
            uri = results["tracks"]["items"][0]["uri"]
            song_ids.append(uri)
        except IndexError:
            print(f'{song} doesn\'t exist in Spotify. Skipped.')

    create_playlist = sp.user_playlist_create(
        user=user_id,
        name=playlist_name,
        public=True
    )

    sp.playlist_add_items(
        playlist_id=create_playlist['id'],
        items=song_ids,
        position=None
    )
