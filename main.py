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
jlptResponse = requests.get(jlptReleaseURL)
jlptData = jlptResponse.json()

# Furigana Data:
# get latest release url:
FuriganaReleaseURL = getLatestReleaseURL("https://api.github.com/repos/Doublevil/JmdictFurigana/releases/latest", "JmdictFurigana.json.zip")
# file is zipped downloaded and unziped to temp dir.
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

    print("Adding data to JMDict!")

    # looks through all words in jmdict. 
    for entry in jmdictData["words"]:
        # for every word with kanji add furigana and jlpt level data.
        for kanjiObject in entry["kanji"]:
            kanji = kanjiObject.get("text")

            if furiganaData.get(kanji):
                if "furigana" not in entry:
                    entry["furigana"] = [{ kanji : furiganaData[kanji] }]
                else:
                    entry["furigana"].append({ kanji : furiganaData[kanji] })
            if (not jlptData.get(kanji)):
                continue
            if (entry.get("jlptLevel") and jlptData.get(kanji)):
                entry["jlptLevel"].append({ kanji:jlptData[kanji] })
            else:
                entry["jlptLevel"] = [{ kanji:jlptData[kanji] }]
        # for every reading/hiragana word add jlptlevel.
        for kanaObject in entry["kana"]:
            kana = kanaObject.get("text")

            if (not jlptData.get(kana)):
                continue
            if (entry.get("jlptLevel") and jlptData.get(kana)):
                entry["jlptLevel"].append({ kana:jlptData[kana] })
            else:
                entry["jlptLevel"] = [{ kana:jlptData[kana] }]

# update the whole dict file with added jlpt and furigana data.
jmdictToJSON = json.dumps(jmdictData, ensure_ascii=False)

currentDirectory = os.getcwd()
os.mkdir(f"{currentDirectory}/result")

today = date.today().strftime("%Y-%d-%m")

# create file in result folder.
with open(f"result/jmdictExtended-{today}.json", "w", encoding="utf-8-sig") as writeFile:
    writeFile.write(jmdictToJSON)
    print("File done!")

# remove temporary directory after file is made.
tempDelete = shutil.rmtree("temp/")
print("Deleted deleted temporary files!")
print("DONE...")