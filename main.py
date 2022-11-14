from pydantic import env_settings
import requests
import json 
import gtts
import random
import os
from tqdm.auto import tqdm
from moviepy.editor import *
import os
from dotenv import load_dotenv
from moviepy.video.io.VideoFileClip import VideoFileClip
from mutagen.mp3 import MP3

load_dotenv() #load .env

PEXELS_API_KEY = os.getenv('PEXELS_API_KEY') #add your api key in .ENV



# download background video from pexels - https://www.pexels.com/api/documentation/#videos-search__parameters
def downloadVideo(id):
    """Downloads video from Pexels with the according video ID """
    url = "https://www.pexels.com/video/" + str(id) + "/download.mp4"
    # Streaming, so we can iterate over the response.
    response = requests.get(url, stream=True)
    total_size_in_bytes= int(response.headers.get('content-length', 0))
    block_size = 1024 #1 Kibibyte
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    save_as = "vid.mp4" # the name you want to save file as
    with open(save_as, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()
    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        print("ERROR, something went wrong")
    return save_as

        

def scrapeVideos():
    """Scrapes video's from PEXELS about nature in portrait mode with API key"""
    print("scrapeVideos()")
    parameters = {
        'query' : 'nature',
        'orientation' : 'portrait',
        #'page' : '1',
    }
    try:
        pexels_auth_header = {
            'Authorization' : PEXELS_API_KEY
        }
        print("trying to request page..")
        resp = requests.get("https://api.pexels.com/videos/search",headers=pexels_auth_header, params=parameters)
    except:
        print("Error in request.get....!??")
    data = json.loads(resp.text)
    results = data['total_results']
    if results == 0:
        print("No video results for your query: ", parameters['query'],"\nExiting..." )
        exit()
    return data

def deleteFirstLineInTxt():
    """Removes the quote text we used in the video, so we don't have duplicates"""
    with open('quotes/motivational.txt', 'r+') as file:
        lines = file.readlines()
        file.seek(0)
        file.truncate()
        file.writelines(lines[1:])

def getQuote():
    """Get 1 quote from the text file"""
    with open('quotes/motivational.txt', 'r+') as file:
        lines = file.readlines()
        x = lines[0].replace("\n","").replace("-", "\n -")
        print ("Quote: ", x)
        return x

def makeMp3(data):
    """Make mp3 from the quote text, so we know the duration it takes to read"""
    save_as = "speech.mp3"
    tts = gtts.gTTS(data, lang='en', tld='ca')
    tts.save(save_as)
    return save_as


def createVideo(quoteText: str, bgMusic, bgVideo, video_number: int):
    """Creates the entire video with everything together - this should be split up in different methods"""
    introText = ['A quote about never giving up on your dreams','A quote about being yourself','A quote about believing in yourself','A quote about making your dreams come true','A quote about happiness','A quote to remind you to stay positive','A quote about never giving up', 'A quote about being grateful', 'A quote about taking risks', 'A quote about living your best life']
    print("Introtext we will use: ", introText[video_number])
    # Create intro start
    intro_text_clip = TextClip(
        txt=introText[video_number],
        fontsize=70,
        size=(800, 0),
        font="Roboto-Regular",
        color="white",
        method="caption",
        #bg_color='black',
        ).set_position('center')
    
    intro_width, intro_height = intro_text_clip.size
    intro_color_clip = ColorClip(
        size=(intro_width+100, intro_height+50),
        color=(0,0,0)
        ).set_opacity(.6)
    intro_clip = VideoFileClip("intro_clip/2_hands_up.mp4").resize((1080,1920))
    intro_clip_duration = 6
    text_with_bg= CompositeVideoClip([intro_color_clip, intro_text_clip]).set_position(lambda t: ('center', 200+t)).set_duration(intro_clip_duration)
    intro_final = CompositeVideoClip([intro_clip, text_with_bg]).set_duration(intro_clip_duration)
    # Create intro end

    #quoteArray = ['Happiness is not a brilliant climax to years of grim struggle and anxiety.', 'It is a long succession of little decisions simply to be happy in the moment.']
    quoteArray = []
    quoteArray.append(quoteText)
    totalTTSTime = 0
    completedVideoParts = []
    ttsAudio = False
    for idx, sentence in enumerate(quoteArray):
        #create the audio
        save_as = "temp_audio_" + str(idx) + ".mp3"
        tts = gtts.gTTS(sentence, lang='en', tld='ca')
        #save audio
        tts.save(save_as)
        audio = MP3(save_as)
        time = audio.info.length
        totalTTSTime += time
        #print audio length
        print("Mp3 ", str(idx), " has audio length: ",time)
        #createTheClip with the according text
        text_clip = TextClip(
            txt=sentence,
            fontsize=70,
            size=(800, 0),
            font="Roboto-Regular",
            color="white",
            method="caption",
            ).set_position('center')
        #make background for the text
        tc_width, tc_height = text_clip.size
        color_clip = ColorClip(
            size=(tc_width+100, tc_height+50),
            color=(0,0,0)
            ).set_opacity(.6)

        text_together = CompositeVideoClip([color_clip, text_clip]).set_duration(time).set_position('center')
        audio_clip = AudioFileClip(save_as)
        new_audioclip = CompositeAudioClip([audio_clip])
        text_together.audio = new_audioclip
        text_together.fps = 24 #delete this line ??
        completedVideoParts.append(text_together)
        if os.path.exists(save_as):
            os.remove(save_as)
        else:
            print("Can't find the MP3 file so we did NOT delete it!!")
    combined_quote_text_with_audio = concatenate_videoclips(completedVideoParts).set_position('center') # delete compose (was needed for resolution issue)
    combined_quote_text_with_audio.set_position('center')

    #calculate total time
    total_video_time = intro_clip_duration + totalTTSTime
    background_clip = VideoFileClip(bgVideo).resize((1080,1920))
    
    final_export_video = CompositeVideoClip([background_clip, combined_quote_text_with_audio]).subclip(0, totalTTSTime)

    #Set audio
    audio_clip = AudioFileClip(bgMusic)
    #change the audio under here...
    new_audioclip = CompositeAudioClip([
        audio_clip, 
        #final_export_video.audio.set_start(intro_clip_duration) #uncomment to get TTS audio
        ]).subclip(0,total_video_time)

    final = concatenate_videoclips([intro_final, final_export_video])
    final.audio = new_audioclip

    final.write_videofile("VID_" + str(video_number) + ".mp4", threads=12)

def randomBgMusic():
    """Get a random 'sad' song from the sad_music folder"""
    dir = "sad_music"
    x = random.choice(os.listdir(dir)) #change dir name to whatever
    print("Random music chosen: ", x)
    return dir + "/" + x

if __name__ == "__main__":
    """Make X amount of videos."""
    for i in range(1): #amount of videos to generate
        scrapedVideosJson = scrapeVideos()
        videoArray = scrapedVideosJson['videos']
        randomVideoToScrape = random.randint(0, len(videoArray)-1)
        videoId = videoArray[randomVideoToScrape]['id']
        print("Going to scrape video with id: ", videoId)
        bgVideo = downloadVideo(videoId)
        quoteText = getQuote()
        print(quoteText)
        deleteFirstLineInTxt() # remove the quote from quotes.txt
        mp3 = makeMp3(quoteText) # make mp3 and save as: speech.mp3
        bgMusic = randomBgMusic()
        # createVideo(mp3, quoteText,bgMusic, bgVideo, i) # createVideo(quoteMp3,bgMusic,bgVideo)
        createVideo(quoteText,bgMusic, bgVideo, i) # createVideo(quoteMp3,bgMusic,bgVideo)
        print("finished! video: ", i)
    


