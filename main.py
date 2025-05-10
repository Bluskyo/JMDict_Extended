import requests
import re
import json
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
import shutil

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
jlptReleaseURL = requests.get("https://api.github.com/repos/Bluskyo/JLPT_Vocabulary/releases/latest", headers=headers)
for asset in jlptReleaseURL.json()["assets"]:
    if "JLPTWords.json" in asset["browser_download_url"]:
        jlptReleaseURL = asset["browser_download_url"]
        break
jlptResponse = requests.get(jlptReleaseURL)
jlptData = jlptResponse.json()

# Furigana Data:
# get latest release url:
FuriganaReleaseURL = requests.get("https://api.github.com/repos/Doublevil/JmdictFurigana/releases/latest", headers=headers)
for asset in FuriganaReleaseURL.json()["assets"]:
    if "JmdictFurigana.json.zip" in asset["browser_download_url"]:
        FuriganaReleaseURL = asset["browser_download_url"]
        break

# file is zipped download and unzip to temp dir.
furiganaFileName = downloadAndExtract(FuriganaReleaseURL, "./temp")

# read unzipped file and store data in furiganaData object
furiganaData = {}
with open(f"temp/{furiganaFileName}", "r", encoding="utf-8-sig") as file:
    data = json.load(file)
    # reading field is redundant, add text and furigana.
    for entry in data:
        furiganaData[entry["text"]] = entry["furigana"]

# JMDict data: 
jmdictReleaseURL = requests.get("https://api.github.com/repos/scriptin/jmdict-simplified/releases/latest", headers=headers)
fileRegex = r"jmdict-eng-(?!.*common).*\.json\.zip$"
for asset in jmdictReleaseURL.json()["assets"]:
    link = asset["browser_download_url"]
    if re.search(fileRegex, link):
        jmdictReleaseURL = link
        break

# file is zipped download and unzip to temp dir.
jmdictFileName = downloadAndExtract(jmdictReleaseURL, "./temp")

jmdictData = {}
with open(f"temp/{jmdictFileName}", "r", encoding="utf-8-sig") as file:
    jmdictData = json.load(file)

    for entry in jmdictData["words"]:
        for kanjiObject in entry["kanji"]:
            kanji = kanjiObject.get("text")

            if (furiganaData.get(kanji)):
                entry["furigana"] = furiganaData[kanji]
            if (not jlptData.get(kanji)):
                continue
            if (entry.get("jlptLevel") and jlptData.get(kanji)):
                entry["jlptLevel"].append({ "kanji":jlptData[kanji] })
            else:
                entry["jlptLevel"] = [{ "kanji":jlptData[kanji] }]
        for kanaObject in entry["kana"]:
            kana = kanaObject.get("text")

            if (not jlptData.get(kana)):
                continue
            if (entry.get("jlptLevel") and jlptData.get(kana)):
                entry["jlptLevel"].append({ "kana":jlptData[kana] })
            else:
                entry["jlptLevel"] = [{ "kana":jlptData[kana] }]

jmdictToJSON = json.dumps(jmdictData, ensure_ascii=False)

with open("jmdictExtended.json", "w", encoding="utf-8-sig") as writeFile:
    writeFile.write(jmdictToJSON)

shutil.rmtree("temp/")