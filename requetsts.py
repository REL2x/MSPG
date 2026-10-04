import discord
from discord import app_commands
from discord.ext import commands
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import os
import random
from dotenv import load_dotenv


sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=os.getenv("SP_CLIENT_ID"),
        client_secret=os.getenv("SP_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope="playlist-read-private playlist-read-collaborative",
        cache_path=".cache"
    )
)

result = sp.search(q='shape of you',limit=1,type='track')
print(result)