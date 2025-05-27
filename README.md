# JMDict_Extended
Adds JLPT level and furigana to the JMDict Dictonary.<br>
<br>JMDict has <a href="https://www.edrdg.org/jmwsgi/updates.py?svc=jmdict&i=1">daily updates</a> 
but this project will follow the updates from <a href="https://github.com/scriptin/jmdict-simplified">jmdict-simplified</a> at 00:30 AM every Tuesday.

## <a href="https://github.com/Bluskyo/JMDict_Extended/releases/latest"> Download the latest files⬇️</a>

This project combines data from these repositories: <br>
https://github.com/scriptin/jmdict-simplified <br>
https://github.com/Doublevil/JmdictFurigana <br>
https://github.com/Bluskyo/JLPT_Vocabulary

## Example on entry with both furigana and jlpt data added.
The json follow the same structrue as jmdict-simplified but has these added properties on some entries: 
```
 "furigana": [
    {
      "挨拶": [
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
  "jlptLevel": [
    {
      "挨拶": "N3"
    },
    {
      "あいさつ": "N4"
    }
  ]
```
