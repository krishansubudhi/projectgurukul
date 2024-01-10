import pandas as pd
from llama_index.readers.base import BaseReader
from llama_index.schema import Document
import pandas as pd


class CSVReader(BaseReader):
    def __init__(self, text_columns, metadata_columns = (), text_template="{value}", text_separator="\n\n", preprocess=None, column_name_mappings=None, header=None):
        self.text_columns = text_columns
        self.metadata_columns = metadata_columns
        self.preprocess = preprocess
        self.text_template = text_template
        self.text_separator = text_separator
        self.column_name_mappings = column_name_mappings
        self.header = header if header else 'infer' # pandas default.

    def load_data(self, file, extra_info=None):
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

            documents.append(Document(text=text + "\n\n", extra_info=metadata))

        return documents

    def format_text(self, row):
        # Default implementation, can be overridden in subclasses
        text_values = [self.text_template.format(
            key=col, value=row[col]) for col in self.text_columns]
        return self.text_separator.join(text_values)

    def extract_metadata(self, row):
        return {col: row[col] for col in self.metadata_columns}
