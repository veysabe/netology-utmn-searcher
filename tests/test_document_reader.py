import unittest
from pathlib import Path

from document_reader import load_documents
from structures import documents
from tempfile import TemporaryDirectory

class TestLoadDocuments(unittest.TestCase):
    def test_finds_one_pdf_files(self):
        with TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            pdf_file = folder / 'test.pdf'
            pdf_file.touch()
            result = load_documents([str(folder)])
            test_dict = {1 : str(pdf_file)}
            self.assertEqual(result, test_dict)
    def test_skips_non_pdf_files(self):
        with TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            txt_file = folder / 'test.txt'
            txt_file.touch()
            result = load_documents([str(folder)])
            test_dict = {}
            self.assertEqual(result, test_dict)
    def test_finds_pdf_with_uppercase_letters(self):
        with TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            pdf_file = folder / 'TEST.PDF'
            pdf_file.touch()
            result = load_documents([str(folder)])
            test_dict = {1 : str(pdf_file)}
            self.assertEqual(result, test_dict)
    def test_skips_missing_directory(self):
        with TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            missing_folder = folder / 'missing'
            result = load_documents([str(missing_folder)])
            test_dict = {}
            self.assertEqual(result, test_dict)
    def test_clears_documents(self):
        with TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            documents.clear()
            documents[42] = 'tumgu.pdf'
            result = load_documents([str(folder)])
            test_dict = {}
            self.assertEqual(result, test_dict)
    def test_skips_pdf_in_nested_directory(self):
        with TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            nested_folder = folder / 'nested'
            nested_folder.mkdir()
            nested_file = nested_folder / 'test.pdf'
            nested_file.touch()
            result = load_documents([str(folder)])
            test_dict = {}
            self.assertEqual(result, test_dict)
    def test_load_all_pdf_with_each_paths(self):
        with TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            first_folder = folder / 'first'
            first_folder.mkdir()
            first_file = first_folder / 'first.pdf'
            first_file.touch()
            second_folder = folder / 'second'
            second_folder.mkdir()
            second_file = second_folder / 'second.pdf'
            second_file.touch()
            all_folders = [str(first_folder), str(second_folder)]
            result = load_documents(all_folders)
            test_dict = {1: str(first_file), 2:str(second_file)}
            self.assertEqual(result, test_dict)
