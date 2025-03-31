import pandas as pd
from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import Document
import pandas as pd
import re

class CSVReader(BaseReader):
    """
    CSVReader class for loading data from CSV files into a list of Document objects.

    Parameters:
    - text_columns (list): List of column names containing text data.
    - metadata_columns (tuple, optional): Tuple of column names containing metadata (default is an empty tuple).
    - text_template (str, optional): Template for formatting text values (default is "{value}").
    - text_separator (str, optional): Separator for joining text values (default is "\n\n").
    - preprocess (callable, optional): Function for preprocessing rows before formatting (default is None).
    - column_name_mappings (dict, optional): Dictionary for mapping column names (default is None).
    - header (str or None, optional): Header parameter for pandas read_csv method (default is 'infer').

    Methods:
    - load_data(file, extra_info=None): Load data from a CSV file into a list of Document objects.
    - format_text(row): Format text values from a row using the specified template and separator.
    - extract_metadata(row): Extract metadata values from a row.

    """

    def __init__(self, text_columns, metadata_columns=(), text_template="{value}", text_separator="\n\n", preprocess=None, column_name_mappings=None, header=None):
        self.text_columns = text_columns
        self.metadata_columns = metadata_columns
        self.preprocess = preprocess
        self.text_template = text_template
        self.text_separator = text_separator
        self.column_name_mappings = column_name_mappings
        self.header = header if header else 'infer'  # pandas default.

    def load_data(self, file, extra_info=None):
        """
        Load data from a CSV file into a list of Document objects.

        Parameters:
        - file (str): Path to the CSV file.
        - extra_info (dict, optional): Extra information to be added to the metadata (default is None).

        Returns:
        - list: List of Document objects.

        """
        df = pd.read_csv(file, header=self.header)
        if self.column_name_mappings:
            df.rename(mapper=self.column_name_mappings, axis=1, inplace=True)
        documents = []

        for _, row in df.iterrows():
            if self.preprocess:
                row = self.preprocess(row)
            text = self.format_text(row)
            metadata = self.extract_metadata(row)

            if extra_info:
                metadata.update(extra_info)

            documents.append(Document(text=text, extra_info=metadata))

        return documents

    def format_text(self, row):
        """
        Format text values from a row using the specified template and separator.

        Parameters:
        - row (pd.Series): Row from the CSV file.

        Returns:
        - str: Formatted text.

        """
        text_values = [self.text_template.format(
            key=col, value=row[col]) for col in self.text_columns]
        return self.text_separator.join(text_values)

    def extract_metadata(self, row):
        """
        Extract metadata values from a row.

        Parameters:
        - row (pd.Series): Row from the CSV file.

        Returns:
        - dict: Metadata values.

        """
        return {col: row[col] for col in self.metadata_columns}


class RamayanaCSVReader(CSVReader):
    def __init__(self):
        pass
    def load_data(self, file, extra_info=None):
        df = pd.read_csv(file).dropna(how="all").fillna("")
        ids = df.content.map(lambda shloka: re.findall(r'.*(\d+\.\d+\.\d+).*',shloka))
        df["shloka_ids"] = ids.map(lambda ids: ", ".join(ids))
        df["sarga"] = ids.map(lambda ids: int(ids[0].split(".")[1]))

        df["shloka_with_explanation"] = df.apply(
            lambda row: f"{row.content}\n {row.explanation}",
            axis = 1
        )

        df["explanation_with_id"] = df.apply(
            lambda row: f"{row.explanation} ।।{row.shloka_ids}।।",
            axis = 1
        )
        df_grouped = df.groupby('sarga').agg(lambda lst: "\n\n".join(lst)).reset_index()
        documents = []

        for _, row in df_grouped.iterrows():
            sarga = row['sarga']
            shlokas = row['content']
            english_expl = row['explanation']
            shloka_with_explanation = row['shloka_with_explanation']
            explanation_with_id = row['explanation_with_id']

            metadata = {
                'sarga': sarga
            }


            if shlokas[0] == "[":
                metadata['summary'] = shlokas.split("]")[0][1:][:200]

            if extra_info:
                metadata.update(extra_info)

            documents.append(Document(text=shloka_with_explanation, extra_info=metadata))
            # documents.append(Document(text=explanation_with_id, extra_info=metadata))

        return documents

class MahabharataCSVReader(CSVReader):
    def __init__(self):
        pass
    def load_data(self, file, extra_info=None):
        df = pd.read_csv(file)
        documents = []

        df_grouped = df.groupby(['parva', 'chapter', 'chapter title']).agg(lambda lst: "\n\n".join(lst)).reset_index()
        parva_id_map = dict(zip(*[iter(df_grouped['parva'].unique()), iter(range(1, df_grouped.size + 1))]))

        for _, row in df_grouped.iterrows():
            parva = row['parva']
            parva_id = parva_id_map[parva]
            chapter_id = row['chapter']
            chapter_title = row['chapter title']
            content = row['content']

            metadata = {
                'parva_id' : parva_id,
                'parva': parva,
                'chapter_id':chapter_id,
                'chapter_title':chapter_title
            }

            documents.append(Document(text=content, extra_info=metadata))

        return documents