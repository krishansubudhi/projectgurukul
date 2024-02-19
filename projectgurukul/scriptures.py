from typing import Callable, Tuple, Dict, Any
from abc import ABC, abstractmethod
from llama_index.core import (
    SimpleDirectoryReader,
)
from typing import Callable, Tuple, Any
from projectgurukul.readers import CSVReader, RamayanaCSVReader, MahabharataCSVReader

SCRIPTURE_METADATA_KEY = "scripture"


def load_scripture_basics(directory):
    return SimpleDirectoryReader(input_dir=directory).load_data()


class Scripture(ABC):
    ID: str = ""
    NAME: str = ""
    DIRECTORY: str = ""
    METADATAS_TO_DISPLAY: Tuple[str] = ()
    DESCRIPTION: str = ""

    @abstractmethod
    def create_source_link(self, metadata: Dict[str, str]) -> str:
        ...

    @abstractmethod
    def get_reference_string(self, metadata: Dict[str, str]) -> str:
        ...


class Gita(Scripture):
    ID = "gita"
    NAME = "Bhagavad Gita"
    DIRECTORY = "gita"
    METADATAS_TO_DISPLAY = ('chapter', 'verse', 'source')
    DESCRIPTION = ("Datasource for Bhagavad Gita - a sacred Hindu scripture that is part"
                   " of the Indian epic Mahabharata. It consists of a conversation between"
                   " Prince Arjuna and the god Krishna, who serves as his charioteer."
                   " Explore insights, chapters, verses, and the profound teachings of the Gita."
                   )

    def load(self, directory):
        def preprocess(row):
            row['chapter'], row['verse'] = row.verse_number.split(', ')
            return row

        reader = CSVReader(text_columns=['verse_in_sanskrit', 'translation_in_english',
                                         'meaning_in_english'], metadata_columns=['chapter', 'verse'], preprocess=preprocess)
        documents = SimpleDirectoryReader(
            input_dir=directory, file_extractor={".csv": reader}).load_data()

        for document in documents:
            document.metadata[SCRIPTURE_METADATA_KEY] = self.ID
            document.excluded_embed_metadata_keys.extend(["file_path"])
            document.excluded_llm_metadata_keys.extend(["file_path"])
        return documents

    def create_source_link(self, metadata: Dict[str, str]) -> str:

        if 'chapter' in metadata and 'verse' in metadata:
            chapter = metadata['chapter'].split()[-1]
            verse = metadata['verse'].split()[-1]
            return f"https://www.holy-bhagavad-gita.org/chapter/{chapter}/verse/{verse}"
        else:
            return None

    def get_reference_string(self, metadata: Dict[str, str]) -> str:
        if 'chapter' in metadata and 'verse' in metadata:
            chapter = metadata['chapter'].split()[-1]
            verse = metadata['verse'].split()[-1]
            link = self.create_source_link(metadata)
            return f"[{self.NAME}: Chapter {chapter}, Verse {verse}]({link})"
        else:
            return str(metadata)


class Ramayana(Scripture):
    ID = "ramayana"
    NAME = "Valmiki Ramayana"
    DIRECTORY = "ramayana"
    METADATAS_TO_DISPLAY = ('kanda', 'sarga', 'source')
    DESCRIPTION = (
        "Datasource for Ramayana - one of the two major Sanskrit epics of ancient"
        " Indian literature. Ramayana narrates the life of Prince Rama, his wife Sita,"
        " and his loyal companion Hanuman. Explore the epic journey, learn about the"
        " different kandas, sargas, and delve into the rich narrative that includes"
        " the powerful and complex character of Ravana, the demon king of Lanka."
        " Discover the intricate details of Ravana's role and impact in the Ramayana story."
    )
    KANDA_MAPPINGS = {
        "bala": 1,
        "ayodhya": 2,
        "aranya": 3,
        "kishkinda": 4,
        "sundara": 5,
        "yuddha": 6
    }

    def load(self, directory):
        reader = RamayanaCSVReader()
        documents = SimpleDirectoryReader(
            input_dir=directory, file_extractor={".csv": reader}).load_data()
        for document in documents:
            document.metadata["kanda"] = document.metadata["file_name"].split('.')[
                0].replace("kanda", " kanda")
            document.metadata[SCRIPTURE_METADATA_KEY] = self.ID
            document.excluded_embed_metadata_keys.extend(["file_path"])
            document.excluded_llm_metadata_keys.extend(["file_path"])
        return documents

    def create_source_link(self, metadata: Dict[str, str]) -> str:

        if 'sarga' in metadata and 'kanda' in metadata:
            kanda = metadata['kanda'].split()[0]
            sarga = metadata['sarga']
            kanda_numeric = self.KANDA_MAPPINGS[kanda]

            return f"https://www.valmiki.iitk.ac.in/sloka?field_kanda_tid={kanda_numeric}&language=dv&field_sarga_value={sarga}"
        else:
            return None

    def get_reference_string(self, metadata: Dict[str, str]) -> str:
        if 'sarga' in metadata and 'kanda' in metadata:
            kanda = metadata['kanda'].split()[0].capitalize()
            sarga = metadata['sarga']

            link = self.create_source_link(metadata)
            return f"[{self.NAME}: {kanda} Kanda, Sarga {sarga}]({link})"
        else:
            return str(metadata)


class Mahabharata(Scripture):
    ID = "mahabharata"
    NAME = "mahabharata"
    DIRECTORY = "mahabharata"
    METADATAS_TO_DISPLAY = ('parva', 'chapter', 'source')
    DESCRIPTION = (
        ""
    )

    def load(self, directory):
        reader = MahabharataCSVReader()
        documents = SimpleDirectoryReader(
            input_dir=directory, file_extractor={".csv": reader}).load_data()
        for document in documents:
            document.metadata[SCRIPTURE_METADATA_KEY] = self.ID
            document.excluded_embed_metadata_keys.extend(["file_path"])
            document.excluded_llm_metadata_keys.extend(["file_path"])
            document.excluded_embed_metadata_keys.extend(["parva_id"])
            document.excluded_llm_metadata_keys.extend(["parva_id"])
        return documents

    def create_source_link(self, metadata: Dict[str, str]) -> str:
        if 'parva_id' in metadata and 'parva' in metadata:
            parva_id = metadata['parva_id']
            parva = metadata["parva"]
            return f"https://en.wikisource.org/wiki/The_Mahabharata/Book_{parva_id}:_{parva.replace(' ','_')}"
        else:
            return None

    def get_reference_string(self, metadata: Dict[str, str]) -> str:
        if 'parva' in metadata and 'chapter_title' in metadata:
            parva = metadata['parva'].strip().capitalize()
            chapter_title = metadata['chapter_title'].strip().capitalize()
            link = self.create_source_link(metadata)
            return f"[{self.NAME}: {parva}, Chapter: {chapter_title}]({link})"
        else:
            return str(metadata)

