import requests
import json 
import gtts
import random
import os
import subprocess
from tqdm.auto import tqdm
from moviepy.editor import *
import os
import glob
from moviepy.video.io.VideoFileClip import VideoFileClip
from mutagen.mp3 import MP3

# download background video from pexels - https://www.pexels.com/api/documentation/#videos-search__parameters
def downloadVideo(id) -> str:
    """Downloads video from Pexels with the according video ID """
    url = "https://www.pexels.com/video/" + str(id) + "/download.mp4"
    # Streaming, so we can iterate over the response.
    response = requests.get(url, stream=True)
    total_size_in_bytes= int(response.headers.get('content-length', 0))
    block_size = 1024 #1 Kibibyte
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    save_as = "tempFiles/vid.mp4" # the name you want to save file as
    with open(save_as, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()
    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        print("ERROR, something went wrong")
    return save_as

        

def scrapeVideos(pexelsApiKey: str):
    """Scrapes video's from PEXELS about nature in portrait mode with API key"""
    print("scrapeVideos()")
    parameters = {
        'query' : 'nature',
        'orientation' : 'portrait',
        #'page' : '1',
    }
    try:
        pexels_auth_header = {
            'Authorization' : pexelsApiKey
        }
        print("Trying to request Pexels page with your api key")
        resp = requests.get("https://api.pexels.com/videos/search", headers=pexels_auth_header, params=parameters)
        statusCode = resp.status_code
        if statusCode != 200:
            if statusCode == 429:
                print(f"""You sent too many requests(you have exceeded your rate limit)!\n 
                The Pexels API is rate-limited to 200 requests per hour and 20,000 requests per month (https://www.pexels.com/api/documentation/#introduction).\n
                Returned status code: {statusCode}""")
            else:
                print(f"Error requesting Pexels, is your api key correct? Returned status code: {statusCode}")
            print("Exiting...!")
            return None
    except:
        print("Error in request.get....!??")
        return None
    try:
        data = json.loads(resp.text)
        results = data['total_results']
    except:
        print("Error in pexels json data ?")
        return None
    if results == 0:
        print("No video results for your query: ", parameters['query'],"\nExiting..." )
        return None
    return data

def usedQuoteToDifferentFile():
    """Removes the used quote from the .txt and places the quote in usedQuotes.txt"""
    quote = None
    with open('quotes/motivational.txt', 'r+', encoding='utf8') as file:
        lines = file.readlines()
        quote = lines[0]
        file.seek(0)
        file.truncate()
        file.writelines(lines[1:])
    
    with open('quotes/usedQuotes.txt', 'a') as file:
        file.write(quote)


def getQuote():
    data = requests.get('https://api.quotable.io/random').json()
    quote = data['content']
    print(f"Quote: {quote}")
    return quote

# def makeMp3(data):
#     """Make mp3 from the quote text, so we know the duration it takes to read"""
#     save_as = "tempFiles/speech.mp3"
#     tts = gtts.gTTS(data, lang='en', tld='ca')
#     tts.save(save_as)
#     return save_as

def videoIntro(introText, videoNumber) -> CompositeVideoClip:
    intro_text_clip = TextClip(
        txt=introText[videoNumber],
        fontsize=70,
        size=(800, 0),
        font="Roboto-Regular",
        color="white",
        method="caption",
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
    return intro_final

def createVideo(quoteText: str, bgMusic: str, bgVideo: str, videoNumber: int, ttsAudio: bool):
    """Creates the entire video with everything together - this should be split up in different methods"""
    introText = ['A quote about never giving up on your dreams','A quote about being yourself','A quote about believing in yourself','A quote about making your dreams come true','A quote about happiness','A quote to remind you to stay positive','A quote about never giving up', 'A quote about being grateful', 'A quote about taking risks', 'A quote about living your best life']
    print(f"Introtext we will use: {introText[videoNumber]}")
    intro_final = videoIntro(introText, videoNumber)

    quoteArray = []
    quoteArray.append(quoteText)
    totalTTSTime = 0
    completedVideoParts = []

    print(f"Going to create a total of {len(quoteArray)} 'main' clips")
    for idx, sentence in enumerate(quoteArray):
        #create the audio
        save_as = f"tempFiles/temp_audio_{str(idx)}.mp3"
        tts = gtts.gTTS(sentence, lang='en', tld='ca')
        #save audio
        tts.save(save_as)
        audio = MP3(save_as)
        time = audio.info.length
        totalTTSTime += time
        print(f"Mp3 {str(idx)} has audio length: {time} ")

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
        completedVideoParts.append(text_together)

    combined_quote_text_with_audio = concatenate_videoclips(completedVideoParts).set_position('center') 
    combined_quote_text_with_audio.set_position('center')

    #calculate total time
    total_video_time = intro_final.duration + totalTTSTime
    background_clip = VideoFileClip(bgVideo).resize((1080,1920))
    final_export_video = CompositeVideoClip([background_clip, combined_quote_text_with_audio]).subclip(0, totalTTSTime)

    #Set audio
    backgroundMusic = AudioFileClip(bgMusic)
    totalAudio = audioClip(ttsAudio, backgroundMusic, final_export_video, total_video_time, intro_final.duration)

    final = concatenate_videoclips([intro_final, final_export_video])
    final.audio = totalAudio
    final.write_videofile("VID_" + str(videoNumber) + ".mp4", threads=12)

def audioClip(ttsAudio: bool, backgroundMusic, final_export_video, total_video_time, introDuration: int) -> CompositeAudioClip:
    """Makes the audioclip for the entire video, ttsAudio is the boolean that the user sets (yes/no TTS in the quotetext)"""
    new_audioclip = None
    if ttsAudio:
        new_audioclip = CompositeAudioClip([
            backgroundMusic, 
            final_export_video.audio.set_start(introDuration) #uncomment to get TTS audio -> goes to else
            ]).subclip(0,total_video_time)
    else:
        new_audioclip = CompositeAudioClip([
        backgroundMusic, 
        ]).subclip(0,total_video_time)
    return new_audioclip



def randomBgMusic():
    """Get a random 'sad' song from the sad_music folder"""
    dir = "sad_music"
    x = random.choice(os.listdir(dir)) 
    print("Random music chosen: ", x)
    return dir + "/" + x


def deleteTempFiles():
    """Deletes the downloaded/generated vid.mp4 and speech.mp3"""
    print("Deleting temporary downloaded files / generated mp3 file")
    files = glob.glob('tempFiles/*')
    for x in files:
        os.remove(x)

def cleanUpAfterVideoFinished():
    usedQuoteToDifferentFile()
    # deleteTempFiles()

def getBackgroundVideo(pexelsApiKey) -> str:
    
    scrapedVideosJson = scrapeVideos(pexelsApiKey)
    if scrapedVideosJson is None:
        return None
    videoArray = scrapedVideosJson['videos']
    randomVideoToScrape = random.randint(0, len(videoArray)-1)
    videoId = videoArray[randomVideoToScrape]['id']
    print("Going to scrape video with id: ", videoId)
    bgVideo = downloadVideo(videoId)
    return bgVideo

def mainVideoLoop(data):
    """Make X amount of videos."""
    for i in range(int(data['amountOfVideosToMake'])): #amount of videos to generate
        bgVideo = getBackgroundVideo(data['pexelsAPIKey'])
        if bgVideo is None:
            return None
        quoteText = getQuote()
        # mp3 = makeMp3(quoteText) # make mp3 and save as: speech.mp3
        bgMusic = randomBgMusic()
        ttsAudio = True
        createVideo(quoteText, bgMusic, bgVideo, i, ttsAudio)
        cleanUpAfterVideoFinished()
        print("finished! video: ", i)
    return True


def changeJsonValue(question, data, dataString):
    user_input = input(question)
    data[dataString] = user_input
    with open('config.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent = 4, sort_keys=True)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'



def verifyData(data):
    """Verify amount of videos to make and pexelsAPI (does 1 request via scrapeVideo's method)"""
    print("Checking data....")
    if int(data['amountOfVideosToMake']) < 1:
        print("Amount of videos to create is smaller then 1.\nExiting...")
        quit()
    scrapeVideos(data['pexelsAPIKey'])
    print("Everything went well! Starting to create videos now!")


def launchImageMagicksInstaller():
    print("Launching installer...")
    print("In the installer, make sure to select this option(3rd screen):{bcolors.WARNING}legacy utilities(e.g. Convert){bcolors.ENDC}")
    subprocess.run(['imageMagicksInstaller/ImageMagick-7.1.0-52-Q16-HDRI-x64-dll.exe'], stdout=subprocess.PIPE)

def checkIfImageMagicksIsInstalled():
    terminalOutput = ""
    try:
        result = subprocess.run(['magick', 'identify', '--version'], stdout=subprocess.PIPE)
        terminalOutput = str(result.stdout)
    except FileNotFoundError:
        print("ImageMagick installation is not found!")
    if "ImageMagick" in terminalOutput:
        print("ImageMagicks installation is found")
        print("Checking if you selected 'Install legacy utilities(e.g. Convert)' ")
        try:
            TextClip(txt="text") #trying to make a textclip
            print(f"{bcolors.OKGREEN}ImageMagicks is installed correctly{changes}{bcolors.ENDC}")
            return
        except:
            print(f"You did not install ImageMagicks with {bcolors.WARNING}legacy utilities(e.g. Convert){bcolors.ENDC}!\nRerun the installation with this option enabled.")
            x = input("Do you want to reinstall ImageMagicks? (yes/no)")
            if "yes" in x:
                launchImageMagicksInstaller()
                checkIfImageMagicksIsInstalled()
            return
    else:
        print("Do you want to install ImageMagicks? (yes/no)")
        x = input("yes or no: ")
        if "yes" in x:
            launchImageMagicksInstaller()
            checkIfImageMagicksIsInstalled()
        return        

if __name__ == "__main__":
    changes = ""
    while True:
        with open('config.json', 'r') as file:
            data = json.load(file)
        os.system('cls' if os.name=='nt' else 'clear')
        loopPrint = (f"""{bcolors.HEADER}
        
    /__/|__                                                            __//|
    |__|/_/|__                 Video generator v1.1.0                _/_|_||
    |_|___|/_/|__                     fabbree                     __/_|___||
    |___|____|/_/|__                                           __/_|____|_||
    |_|___|_____|/_/|_________________________________________/_|_____|___||
    |___|___|__|___|/__/___/___/___/___/___/___/___/___/___/_|_____|____|_||
    |_|___|___|___|___|___|___|___|___|___|___|___|___|___|___|___|___|___||
    |___|___|___|___|___|___|___|___|___|___|___|___|___|___|___|___|___|_||
    |_|___|___|___|___|___|___|___|___|___|___|___|___|___|___|___|___|___|/{bcolors.ENDC}

                {bcolors.OKGREEN}   {changes}{bcolors.ENDC}

Current configurations:
    Your Pexels API key: {bcolors.WARNING}{data['pexelsAPIKey']}{bcolors.ENDC}
    Amount of videos to create: {bcolors.WARNING}{data['amountOfVideosToMake']}{bcolors.ENDC}
    
Options menu:
    1) Change amount of videos to create
    2) Change Pexels API key
    3) Start generating videos
    4) Check if ImageMagicks is installed (needed to run)
    5) Exit

    Enter your choice: """)
        choice = input(loopPrint)
        changes = ""
        match int(choice):
            case 1:
                changeJsonValue("Amount of videos to create: ", data, 'amountOfVideosToMake')
                changes = "updated video's to create successfully"
            case 2:    
                changeJsonValue("Your Pexels API key: ", data, 'pexelsAPIKey')
                changes = f"updated your API key successfully to - {data['pexelsAPIKey']}"
            case 3:
                verifyData(data)
                videoloop = mainVideoLoop(data)
                if videoloop:
                    changes = f"Succesfully completed making {data['amountOfVideosToMake']} video(s)"
                else:
                    changes = f"An error occurred somewhere above ^ (copy -> sent to developer)"
                    input("Press enter to return to the main screen")
            case 4:
                checkIfImageMagicksIsInstalled()
                input("Press enter to return to the main screen")
            case 5:
                print("Exiting...")
                quit()
            case _:
                print("Invalid option! Example input: 1")
    


