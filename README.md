# Project Gurukul
Unveiling the Knowledge of Hindu Scriptures

Project Description Slides: https://1drv.ms/p/s!ApUg6qGY-u_cifwwQzGW0KLRbch_CA?e=08GoD4

This project builds a QnA bot where one can ask questions and fetch answers from the hindu scriptures.
Currently only Bhagavad Gita is added. In future, more data sources will be added.

# Contribute

Join the discord community https://discord.gg/dsHRPwQH to discuss, suggest ideas, volunteer or just to say hi.

You can contribute by testing this library, adding more scriptures, creating PRs, suggesting features, fixing bugs etc. 

# Setup instructions


## Conda Environment
```
conda create -n gurukul python=3.11
conda activate gurukul
conda install pip
pip install -r requirements.txt
```

## Create OpenAI API Key [Optional]
https://docs.llamaindex.ai/en/stable/getting_started/installation.html#important-openai-environment-setup

This might require credit card and open AI API subscription. If you do not want to subscribe to OpenAI yet, you can avoid this.

## .env
- Create a file called `.env` in the project root.
- Write these in that file and save.
  ```
  OPENAI_API_KEY=<Your OpenAI Key>
  PYTHONPATH=<Path to the root folder of this project>
  ```

`OPENAI_API_KEY` is optional. However, rember to pass `--offline` option to the `starter.py` script. More on that below

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
python starter.py --question "<Your question>" [--offline] [--debug]
```

## Online OpenAI models
```
python starter.py --question "If god can't be seen, how can we trust him?"
```
**Q: If god can't be seen, how can we trust him?**

A: God cannot be directly seen with our physical senses. However, this does not mean that we cannot trust in God's existence. Trusting in God requires faith, which is an inherent aspect of human nature. In the Bhagavad Gita, it is explained that faith is necessary to embark on the spiritual path and to perceive God. Just as we believe in many things in the world without direct perception, such as historical events or reports from different sources, we can also have faith in the existence of God.

The Sanskrit shloka from Chapter 9, Verse 3 of the Bhagavad Gita states: "अश्रद्दधाना: पुरुषा धर्मस्यास्य परन्तप |अप्राप्य मां निवर्तन्ते मृत्युसंसारवर्त्मनि || 3||" (English Meaning: In the last two verses, Shree Krishna promised knowledge and then qualified it with eight merits. It is mentioned here as “this dharma,” or the path of loving devotion to God. No matter how wonderful the knowledge and how effective the path, it remains useless to one who refuses to walk on it.)

The logic behind trusting in God without direct perception is also explained in the context. Just as a judge delivers judgment based on events that took place in the past, or a president administers a country based on reports from various sources, faith is required in every step of our material activities. Similarly, faith is required in the spiritual realm as well. The context provides the example of a story where a king is asked to believe in the presence of butter in milk, even though it cannot be directly seen. The story illustrates that just because something cannot be immediately perceived, it does not mean it does not exist. There is a process for perceiving God, and if we are willing to have faith and follow the process, we can attain direct perception of God and become God-realized.

Source: Bhagavad Gita, Chapter 9, Verse 3


Sources:

Source [1]: 'verse': ' Verse 3', 'chapter': 'Chapter 9'

Source [2]: 'verse': ' Verse 2', 'chapter': 'Chapter 17'

Source [3]: 'verse': ' Verse 11', 'chapter': 'Chapter 15'



## Offline Local models

If you do not have OpenAI subscription, use this. This will have lower accuracy and slow response. Good thing is it does not require any subscription and internet connection - ideal candidate for testing and development.
If you have GPU, results will be faster.

```
python starter.py --question "If god can't be seen, how can we trust him?" --offline
```

**Q: If god can't be seen, how can we trust him?**

A: The question is a common one, and it is often asked by people who are skeptical about the existence of God. The answer to this question is not as simple as it may seem. The fact is that we believe in many things in the world too, without direct perception of them. A judge delivers judgment upon a case concerning an event that took place many years in the past. If the judge adopted the philosophy of believing only what he or she had directly experienced, then the entire legal system would fail. A President administers a country on the basis of reports from all over the country. It is impossible for him to visit and see all the villages and cities within his domain. Now, if he was not willing to believe these reports, on the grounds that he had no direct perception of what was happening, how would he be able to administer the whole country? So, even in material activities, faith is required at every step. The Bible states this very nicely: “We walk by faith, and not by sight.” (2 Corinthians 5:7)

The story of the king and the sadhu is a beautiful example of how faith works. The king believed in the existence of butter in the milk because he had faith that


Sources:

Source [1]: 'chapter': 'Chapter 9', 'verse': 'Verse 3'


Note: Answers may change on subsequent calls even for same query.

## Debug
Use the `--debug` flag. This logs the actual prompt and context passed to the llms.

Example:
```
python starter.py --question "Who was arjuna?" --offline --debug
```

# Website

## Run locally
```
Start streamlit run website/app.py
```

