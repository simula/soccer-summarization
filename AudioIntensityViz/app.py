import json

import librosa
from flask import Flask, render_template
from joblib import Memory

get_rms_cache = Memory(".AudioIntensityViz/librosa.get_rms.cache", verbose=0)


@get_rms_cache.cache
def get_rms(full_path):
    y, sr = librosa.load(full_path)
    S, phase = librosa.magphase(librosa.stft(y))
    rms = librosa.feature.rms(S=S)
    times = librosa.times_like(rms)
    eachSec = list(times)[-1] / len(list(times))
    # merge two list as list of tuple
    rms = list(rms[0])
    max_rms = max(rms)
    rms = [e * 100 / max_rms for e in rms]
    return rms, eachSec


def GetIntensityScore(jsonPath, rms_only, eachSec, pre_pad=2, post_pad=5, ):
    WithIntensity = []
    with open(jsonPath, 'r', encoding="utf-8") as f:  # open in readonly mode
        data = json.loads(f.read())
        for e in data['annotations']:
            time_second = int(e['position']) / 1000
            half_split = int(e['gameTime'].split(" - ")[0])
            if half_split == 1:
                vec = rms_only[max(int(time_second / eachSec) - int(pre_pad / eachSec), 0): \
                               int(time_second / eachSec + int(post_pad / eachSec))]
                WithIntensity.append(
                    [time_second, sum(vec) / len(vec), e['label']])
    return WithIntensity


app = Flask(__name__)
app.debug = True


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


# return HTMl video player
@app.route("/video/<path:path>")
def video(path):
    rms_only, eachSec = get_rms(
        "E:\Projects\SoccerGameSummarization\sushant-gautam\AudioIntensityViz\media\\1_224p.mp3")
    data = list(zip([e * eachSec for e in range(len(rms_only))], rms_only))

    audioScore = GetIntensityScore("AudioIntensityViz\media\Labels-v2.json",
                                   rms_only, eachSec)
    # get sum  of audioScore
    average_audio_inten = sum([e[1] for e in audioScore]) / len(audioScore)
    # change float to string  2 floating decimal places
    average_audio_inten = str(round(average_audio_inten, 2))

    audioScore.sort(key=lambda x: x[1], reverse=True)
    data.sort(key=lambda x: x[1], reverse=True)
    data = data[:int(len(data) * 0.1)]
    data.sort(key=lambda x: x[0])
    # read

    return render_template('index.html', path=path, x=[x[0] for x in data], y=[x[1] for x in data],
                           audioScore=audioScore, eachSec=eachSec, average_audio_inten=average_audio_inten)
    # return '<video controls><source src="' + path + '" type="video/mp4"></video>'

# ffmpeg -i 1_224p.mkv -codec copy 1_224p.mp4
# ffmpeg -i 1_224p.mkv -vn  1_224p.mp3

# set FLASK_APP=AudioIntensityViz/app.py
# set FLASK_ENV=development
# flask run
