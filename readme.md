Short 'quote' video generator for whatever platform you use. (reels, shorts, tiktok)

- Generate unlimited video's
- All songs are from youtube's free music library for commercial use.
- 4500+ Quotes included


Todo: ✅ = done ❌ = not done yet
- ❌ Add openAI custom support (title/description generation)
- ❌ Selenium uploading to youtube
- ❌ Quote scraping from API
- ✅ CLI with options (api key, easy file configurations)
- ❌ GUI

Example output video with automatic into:
https://www.youtube.com/shorts/JCElumu8KZ8

Example output video without intro:
https://youtube.com/shorts/j-xkH3DrD9k


## Setup
Install requirements.txt
Normal pip

```pip install -r requirements.txt```
Pip3:

```pip3 install -r requirements.txt```

Required arguments:
- `-a` amount of videos to create
- `-k` your Pexels API key

Optional arguments:
- `-tts` enable TTS for quote text (default is OFF)


### example 0:
```python3 main.py -h```

Displays the help menu

### example 1:
```python3 main.py -a 5 -k 3534323a6f9324345100205454ba4cdac2e35c2d8e43434323230a```

Generates 5 videos

### example 2:
```python3 main.py -tts -a 5 -k 3534323a6f9324345100205454ba4cdac2e35c2d8e43434323230a```

Generates 5 videos with text to speech enabled for the 'quote' part (no text to speech for intro)





