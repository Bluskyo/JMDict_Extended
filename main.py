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

def fileExists(path):
    filename, extension = os.path.splitext(path)
    counter = 1

    while os.path.exists(path):
        path = filename + "(" + str(counter) + ")" + extension
        counter += 1

    return path


headers = {
    'Accept': 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
}

# JLPT level data:
jlptReleaseURL = getLatestReleaseURL("https://api.github.com/repos/Bluskyo/JLPT_Vocabulary/releases/latest", "JLPTWords.json")
print("Fetching latest release of JLPT_Vocabulary...")
jlptResponse = requests.get(jlptReleaseURL)
jlptData = jlptResponse.json()

# Pitch accent data:
print("Reading wadoku pitch accents...")
pitchData = {}
with open("data/wadoku_pitchdb.json", "r", encoding="utf-8-sig") as file:
    pitchData = json.load(file)

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
        entry["pitchAccent"] = {}

        # for every word with kanji add furigana, pitch accent and jlpt level data.
        for kanjiObject in entry["kanji"]:
            kanji = kanjiObject.get("text")
            kanjiObject["furigana"] = []

            if furiganaData.get(kanji):
                kanjiObject["furigana"] = furiganaData[kanji]
            if jlptData.get(kanji):
                kanjiObject["jlptLevel"] = jlptData[kanji]

            if (pitchData.get(kanji)): 
                entry["pitchAccent"] = { # if same entry has more than one pitchAccent only gets first one.
                    "hatsuon" : pitchData[kanji]["hatsuon"][0],
                    "acc_patts" : pitchData[kanji]["acc_patts"][0],
                    "zo_patts" : pitchData[kanji]["zo_patts"][0]
                }

        # for every reading/hiragana word add furigana, pitch accent and jlpt level data.
        for kanaObject in entry["kana"]:
            kana = kanaObject.get("text")
            kanaObject["furigana"] = []

            if furiganaData.get(kana):
                kanaObject["furigana"] = furiganaData[kana]

            if jlptData.get(kana):
                kanaObject["jlptLevel"] = jlptData[kana]

            if (pitchData.get(kana)):
                entry["pitchAccent"] = {
                    "hatsuon" : pitchData[kana]["hatsuon"][0],
                    "acc_patts" : pitchData[kana]["acc_patts"][0],
                    "zo_patts" : pitchData[kana]["zo_patts"][0]
                }

today = date.today().strftime("%Y-%m-%d")
currentDirectory = os.getcwd()
path = f"{currentDirectory}/result/jmdictExtended-{today}.json"
path = fileExists(path)

# write to file:
beforeEntries = "{" + f"""
"version": {json.dumps(jmdictData.get("version"), ensure_ascii=False)},
"languages": {json.dumps(jmdictData.get("languages"), ensure_ascii=False)},
"commonOnly": {json.dumps(jmdictData.get("commonOnly"), ensure_ascii=False)},
"dictDate": {json.dumps(jmdictData.get("dictDate"), ensure_ascii=False)},
"dictRevisions": {json.dumps(jmdictData.get("dictRevisions"), ensure_ascii=False)},
"tags": {json.dumps(jmdictData.get("tags"), ensure_ascii=False)},
"words": [
""" 
with open(f"{path}", "w", encoding="utf-8-sig") as f:
    f.write(beforeEntries)
    words = jmdictData["words"]
    for i, entry in enumerate(words):
        suffix = ",\n" if i < len(words) - 1 else "\n"
        f.write(f"{json.dumps(entry, ensure_ascii=False, separators=(',', ':'))}{suffix}")
    f.write("]" + "}")

# remove temporary directory after file is made.
print("deleting temporary files...")
tempDelete = shutil.rmtree("temp/")
print("Deleted temporary files!")
print("DONE...")