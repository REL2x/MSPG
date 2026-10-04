import discord
from discord import app_commands
from discord.ext import commands
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import os
import random
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv("SP_CLIENT_ID")
CLIENT_SECRET = os.getenv("SP_CLIENT_SECRET")
print("CLIENT_ID:", os.getenv("SP_CLIENT_ID"))
print("CLIENT_SECRET:", os.getenv("SP_CLIENT_SECRET"))

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=os.getenv("SP_CLIENT_ID"),
        client_secret=os.getenv("SP_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope="playlist-read-private playlist-read-collaborative",
        cache_path=".cache"
    )
)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"슬래시 명령어 동기화 완료: 총 {len(synced)}개")
    except Exception as e:
        print(f"동기화 중 오류 발생: {e}")
        
    print(f"로그인 완료: {bot.user.name}")

@bot.tree.command(name="곡추천", description="ENV파일에 저장되어있는 플레이리스트 아이디를 토대로 곡을 하나 추천해드립니다.")
async def recommend_song(interaction: discord.Interaction):
    await interaction.response.defer()
    
    try:
        playlist_id = os.getenv("PLAYLIST_ID")
        results = sp.playlist_tracks(playlist_id)
        items = results.get('items', [])

        if not items:
            await interaction.followup.send("플레이리스트에 곡이 없습니다.")
            return

        valid_tracks = []
        for item in items:
            if not item:
                continue

            track = item.get('item')
            if track and track.get('name') and track.get('artists'):
                valid_tracks.append(track)

        if not valid_tracks:
            await interaction.followup.send("플레이리스트에서 유효한 곡 정보를 찾지 못했습니다.")
            return

        track = random.choice(valid_tracks)

        track_name = track.get('name', '제목 없음')
        artist_name = track.get('artists')[0].get('name', '알 수 없는 아티스트')
        track_url = track.get('external_urls', {}).get('spotify', '')
        
        album_images = track.get('album', {}).get('images', [])
        album_image = album_images[0].get('url') if album_images else None

        embed = discord.Embed(
            title="**추천 곡^~^**",
            description="",
            color=discord.Color.pink()
        )
        embed.add_field(name="곡 제목", value=track_name, inline=False)
        embed.add_field(name="아티스트", value=artist_name, inline=False)
        
        if track_url:
            embed.add_field(name="스포티파이 링크", value=f"[듣기 링크]({track_url})", inline=False)
        
        if album_image:
            embed.set_image(url=album_image)

        await interaction.followup.send(embed=embed)

    except Exception as e:
        print(f"에러 발생 상세: {e}")
        await interaction.followup.send("곡을 추천하는 중 오류가 발생했습니다.")

@bot.tree.command(name="음악검색",description = "음악을 검색합니다.")
@app_commands.describe(music_name="검색할 음악 이름")
async def search_song(interaction : discord.Interaction,music_name: str):
    await interaction.response.defer()

    results = sp.search(q=music_name, type='track', limit=5)

    track_name = results['tracks']['items'][0]['name']
    artist_name = results['tracks']['items'][0]['artists'][0]['name']
    image_url = results['tracks']['items'][0]['album']['images'][0]['url']
    release_date = results['tracks']['items'][0]['album']['release_date']

    embed = discord.Embed(title= f'{music_name}검색 결과',description = f'검색한 곡 : {track_name}\n아티스트 이름 : {artist_name}\n발매일 ; {release_date}')
    embed.set_image(url=image_url)

    await interaction.followup.send(embed=embed)

#플레이리스트 분석
@bot.tree.command(name="플레이리스트분석", description = "사용자에게 입력받은 플레이리스트를 토대로 플레이리스트를 분석합니다.")
@app_commands.describe(playlist_id = "플레이리스트 아이디")
async def analyze_playlist(interaction : discord.Interaction, playlist_id : str):
    interaction.response.defer()
    result = sp.playlist_items(playlist_id)

    playlist_info = sp.playlist(playlist_id)
    tracks = result['items']

    while results["next"]:
        results = sp.next(results)
        tracks.extend(results["items"])

    playlist_name = playlist_info["name"]  
    playlist_owner = playlist_info["owner"]["display_name"]  #
    total_tracks = playlist_info["tracks"]["total"]

    for i, item in enumerate(tracks, 1):
            track = item["track"]

            if track is not None:
                track_name = track["name"]
                artist_name = track["artists"][0]["name"]

    embed = discord.Embed(title=f"{playlist_name} 에 대한 분석",
                          description = f"플레이리스트 제작자 : {playlist_owner}\n 총 곡의 수 : {total_tracks}\n\n {i}. 곡명 : {track_name}, 아티스트 : {artist_name}")
    await interaction.followup.send(embed=embed)


bot.run(os.getenv("BOT_TOKEN"))
