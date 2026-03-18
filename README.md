# JMDict_Extended
Adds JLPT level, furigana and pitch accent to the JMDict Dictonary.<br>
JMDict has <a href="https://www.edrdg.org/jmwsgi/updates.py?svc=jmdict&i=1">daily updates</a> 
but this project will follow the updates from <a href="https://github.com/scriptin/jmdict-simplified">jmdict-simplified</a> at 00:30 AM every Tuesday.

## <a href="https://github.com/Bluskyo/JMDict_Extended/releases/latest"> Download the latest files⬇️</a>

This project combines data from these repositories: <br>
JMDict files in JSON format: https://github.com/scriptin/jmdict-simplified <br>
JMDict Furigana files: https://github.com/Doublevil/JmdictFurigana <br>
JLPT vocabulary in JSON format: https://github.com/Bluskyo/JLPT_Vocabulary <br>
Parsing of Wadoku XML files: https://github.com/IllDepence/anki_add_pitch/blob/master/wadoku_parse.py

## Example on an entry with furigana, JLPT-level and pitch accent data added.
The json follows the same structrue as jmdict-simplified but has these added properties:

```
    "kanji": [
        {
            "common": true,
            "text": "挨拶",
            "tags": [],
            "furigana": [  <-----------
                {
                    "ruby": "挨",
                    "rt": "あい"
                },
                {
                    "ruby": "拶",
                    "rt": "さつ"
                }
            ]
        }
    ],
    {...},
    "pitchAccent": {  <-----------
        "hatsuon": "あい'さつ",
        "acc_patts": "1",
        "zo_patts": "HLLLL"
    },
    "jlptLevel": {  <-----------
        "挨拶": {
            "挨拶": "N3"
        },
        "あいさつ": {
            "あいさつ": "N4"
        }
    }
```

## Attributions / Data collected from
<li>
JMdict Japanese-Multilingual Dictionary File by the Electronic Dictionary Research and Development Group: https://www.edrdg.org/
</li>
<li>
Japanese Language Proficiency Test Resources by Jonathan Waller: https://www.tanos.co.uk/jlpt/
</li>
<li>
The Wadoku project by Ulrich Apel: http://www.wadoku.de/
</li>