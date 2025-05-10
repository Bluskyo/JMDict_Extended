import json

jlptData = {}
furiganaData = {}
jmdictData = {}

with open("data/JLPTWords.json", "r", encoding="utf-8-sig") as file:
    jlptData = json.load(file)

with open("data/JmdictFurigana.json", "r", encoding="utf-8-sig") as file:
    data = json.load(file)

    # reading field is redundant, add text and furigana.
    for entry in data:
        furiganaData[entry["text"]] = entry["furigana"]

with open("data/jmdict-eng-3.6.1.json", "r", encoding="utf-8-sig") as file:
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

