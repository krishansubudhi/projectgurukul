import unittest
import tempfile
import csv
from projectgurukul.readers import CSVReader 

class TestCSVReader(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', newline='', encoding='utf-8')
        csv_writer = csv.writer(self.temp_file)
        csv_writer.writerow(["verse_number", "verse_in_sanskrit", "meaning_in_english"])
        csv_writer.writerow(["1", "Sanskrit Shloka 1", "English Meaning 1"])
        csv_writer.writerow(["2", "Sanskrit Shloka 2", "English Meaning 2"])
        self.temp_file.close()

    def tearDown(self):
        # Remove the temporary CSV file after the test
        import os
        os.remove(self.temp_file.name)

    def test_load_data_with_default_format(self):
        # Test with default text template and separator
        reader = CSVReader(
            text_columns=["verse_in_sanskrit", "meaning_in_english"],
            metadata_columns=["verse_number"],
        )
        expected_text = "Sanskrit Shloka 1\n\nEnglish Meaning 1"

        documents = reader.load_data(self.temp_file.name, extra_info={"source": "test_source"})

        self.assertIsInstance(documents, list)
        self.assertEqual(len(documents), 2)
        self.assertIn(expected_text, documents[0].text)
        self.assertIn("source", documents[0].metadata)
        self.assertIn("verse_number", documents[0].metadata)
    
    def test_load_data_with_custom_format(self):
        # Test with custom text template and separator
        reader = CSVReader(
            text_columns=["verse_in_sanskrit", "meaning_in_english"],
            metadata_columns=["verse_number"],
            text_template="{key}: {value}",
            text_separator=", ",
        )
        expected_text = "verse_in_sanskrit: Sanskrit Shloka 1, meaning_in_english: English Meaning 1"

        documents = reader.load_data(self.temp_file.name, extra_info={"source": "test_source"})

        self.assertIn(expected_text, documents[0].text)

    def test_load_data_with_custom_preprocess(self):
        # Test with a custom preprocessing function
        def custom_preprocess(row):
            row["verse_in_sanskrit"] = row["verse_in_sanskrit"].upper()
            return row

        reader = CSVReader(
            text_columns=["verse_in_sanskrit", "meaning_in_english"],
            preprocess=custom_preprocess,
        )
        expected_text = "SANSKRIT SHLOKA 1\n\nEnglish Meaning 1"

        documents = reader.load_data(self.temp_file.name, extra_info={"source": "test_source"})

        self.assertIn(expected_text, documents[0].text)

    def test_load_data_with_column_name_mappings(self):
        # Test with custom column name mappings
        column_mappings = {"verse_in_sanskrit": "Sanskrit", "meaning_in_english": "English"}
        reader = CSVReader(
            text_columns=["Sanskrit", "English"],
            column_name_mappings=column_mappings,
            text_template = "{key}: {value}"
        )
        expected_text = "Sanskrit: Sanskrit Shloka 1\n\nEnglish: English Meaning 1"

        documents = reader.load_data(self.temp_file.name)

        self.assertIn(expected_text, documents[0].text)

if __name__ == '__main__':
    unittest.main()
