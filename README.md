# Project Gurukul
Unveiling the Knowledge of Hindu Scriptures

Project Description Slides: https://1drv.ms/p/s!ApUg6qGY-u_cifwwQzGW0KLRbch_CA?e=08GoD4
# Setup instructions


## Conda Environment
```
conda create -n gurukul python=3.11
conda activate gurukul
conda install pip
pip install -r requirements.txt
```

## Create OpenAI API Key
https://docs.llamaindex.ai/en/stable/getting_started/installation.html#important-openai-environment-setup


## .env
- Create a file called `.env` in the project root.
- Write these in that file and save.
  ```
  OPENAI_API_KEY=<Your OpenAI Key>
  ```

# Data
Data is downloaded from a kaggle repository.
Gita: 
https://www.holy-bhagavad-gita.org/chapter/1/verse/1

https://www.kaggle.com/datasets/yashnarnaware/bhagavad-gita-versewise


# Test

```
pip install pytest
python -m pytest
```
# Run

```
python starter.py "Why should Arjuna fight with his relatives?"
```

You should see answers like:
```
Q: Why should Arjuna fight with his relatives?
A: Arjuna should fight with his relatives because it is his duty as a warrior to fight in the war. In the Bhagavad Gita, Arjuna realizes that all the warriors on the battlefield, ready to shed blood, are his own relatives, friends, and family. He is filled with remorse and fearful of performing his duty of fighting this war due to his attachment towards his bodily relatives. However, he becomes forgetful of his spiritual existence and the fact that he is not just the body. His affection for his bodily relatives blinds his consciousness. The materialistic concept considers oneself to be only the body, emotionally attached to all its bodily relatives. This attachment is based on ignorance and carries with it the burdens of life like pain, sorrow, grief, and death. Only the death of the physical body can end these materialistic attachments. However, we are more than just the physical body; our eternal souls are beyond life and death. Tangled in the various attachments of the material world, we keep forgetting that the Supreme Lord is our only permanent relative. He is the Father, Mother, Friend, Master, and Beloved of our soul.

The chapters, verses, and shlokas mentioned in the context are as follows:
- Chapter 1
- Verse 28
- Shloka: अर्जुन उवाच |दृष्ट्वेमं स्वजनं कृष्ण युयुत्सुं समुपस्थितम् || 28||सीदन्ति मम गात्राणि मुखं च परिशुष्यति |

- Chapter 1
- Verses 36-37
- Shlokas: निहत्य धार्तराष्ट्रान्न: का प्रीति: स्याज्जनार्दन |पापमेवाश्रयेदस्मान्हत्वैतानाततायिन: || 36 || तस्मान्नार्हा वयं हन्तुं धार्तराष्ट्रान्स्वबान्धवान् |स्वजनं हि कथं हत्वा सुखिन: स्याम माधव || 37||
```

Note: Answers may change on subsequent calls even for same query.


