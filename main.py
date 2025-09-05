import requests
import re
import json
import shutil
import os 

from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from urllib.request import urlopen
from datetime import date

def getLatestReleaseURL(url, fileName):
    jlptReleaseURL = requests.get(url, headers=headers)
    for asset in jlptReleaseURL.json()["assets"]:
        if fileName in asset["browser_download_url"]:
            jlptReleaseURL = asset["browser_download_url"]
            return jlptReleaseURL

def downloadAndExtract(url, pathTo="./temp"):
    response = urlopen(url)
    zipfile = ZipFile(BytesIO(response.read()))
    zipfile.extractall(path=pathTo)
    for fileName in zipfile.namelist():
        return fileName

headers = {
    'Accept': 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
}

# JLPT level data:
jlptReleaseURL = getLatestReleaseURL("https://api.github.com/repos/Bluskyo/JLPT_Vocabulary/releases/latest", "JLPTWords.json")
print("Fetching latest release of JLPT_Vocabulary...")
jlptResponse = requests.get(jlptReleaseURL)
jlptData = jlptResponse.json()

# Furigana Data:
furiganaReleaseURL = getLatestReleaseURL("https://api.github.com/repos/Doublevil/JmdictFurigana/releases/latest", "JmdictFurigana.json.zip")
print("Fetching latest release of JmdictFurigana...")
furiganaFileName = downloadAndExtract(furiganaReleaseURL, "./temp")
furiganaData = {}

with open(f"temp/{furiganaFileName}", "r", encoding="utf-8-sig") as file:
    data = json.load(file)
    # reading field is redundant, add text and furigana.
    for entry in data:
        furiganaData[entry["text"]] = entry["furigana"]

# Pitch accent data:
print("Reading wadoku pitch accents...")
pitchData = {}
with open("data/wadoku_pitchdb.json", "r", encoding="utf-8-sig") as file:
    pitchData = json.load(file)

# JMDict data: 
jmdictReleaseURL = requests.get("https://api.github.com/repos/scriptin/jmdict-simplified/releases/latest", headers=headers)
print("Fetching latest release of jmdict-simplified...")
fileRegex = r"jmdict-eng-(?!.*common).*\.json\.zip$"

for asset in jmdictReleaseURL.json()["assets"]:
    link = asset["browser_download_url"]
    if re.search(fileRegex, link):
        jmdictReleaseURL = link
        break

jmdictFileName = downloadAndExtract(jmdictReleaseURL, "./temp")
jmdictData = {}

print("Creating JMDict_Extended file...")
with open(f"temp/{jmdictFileName}", "r", encoding="utf-8-sig") as file:
    jmdictData = json.load(file)

    print("Adding data to JMDict!")
    for entry in jmdictData["words"]:
        # for every word with kanji add furigana and jlpt level data.
        for kanjiObject in entry["kanji"]:
            kanji = kanjiObject.get("text")

            if furiganaData.get(kanji):
                if "furigana" not in entry:
                    entry["furigana"] = [{ kanji : furiganaData[kanji] }]
                else:
                    entry["furigana"].append({ kanji : furiganaData[kanji] })

            if (pitchData.get(kanji)):
                entry["pitch_accent"] = [{
                    "hatsuon" : [
                        pitchData[kanji]["hatsuon"]
                    ],
                    "acc_patts" : [
                        pitchData[kanji]["acc_patts"]
                    ],
                    "zo_patts" : [
                        pitchData[kanji]["zo_patts"]
                    ]
                }]

            if (not jlptData.get(kanji)):
                continue
            if (entry.get("jlpt_level") and jlptData.get(kanji)):
                entry["jlpt_level"].append({ kanji : jlptData[kanji] })
            else:
                entry["jlpt_level"] = [{ kanji : jlptData[kanji] }]

        # for every reading/hiragana word add jlptlevel.
        for kanaObject in entry["kana"]:
            kana = kanaObject.get("text")

            if (pitchData.get(kana)):
                entry["pitch_accent"] = [{
                    "hatsuon" : [
                        pitchData[kana]["hatsuon"]
                    ],
                    "acc_patts" : [
                        pitchData[kana]["acc_patts"]
                    ],
                    "zo_patts" : [
                        pitchData[kana]["zo_patts"]
                    ]
                }]

            if (not jlptData.get(kana)):
                continue
            if (entry.get("jlpt_level") and jlptData.get(kana)):
                entry["jlpt_level"].append({ kana:jlptData[kana] })
            else:
                entry["jlpt_level"] = [{ kana:jlptData[kana] }]

currentDirectory = os.getcwd()
os.mkdir(f"{currentDirectory}/result")

today = date.today().strftime("%Y-%m-%d")

# create file in result folder.
with open(f"result/jmdictExtended-{today}.json", "w", encoding="utf-8-sig") as writeFile:
    json.dump(jmdictData, writeFile, ensure_ascii=False)

# remove temporary directory after file is made.
tempDelete = shutil.rmtree("temp/")
print("Deleted temporary files!")
print("DONE...")