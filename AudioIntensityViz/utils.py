import json

import librosa
from joblib import Memory

get_rms_cache = Memory(".AudioIntensityViz/librosa.get_rms.cache", verbose=0)


#
#
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


rms_only, eachSec = get_rms(
    "E:\Projects\SoccerGameSummarization\sushant-gautam\AudioIntensityViz\media\\1_224p.mp3")
data = list(zip([e * eachSec for e in range(len(rms_only))], rms_only))

audioScore = GetIntensityScore("AudioIntensityViz\media\Labels-v2.json",
                               rms_only, eachSec)
pass
