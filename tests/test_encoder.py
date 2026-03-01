import json
import unittest

from app.app_types import DatasetEntry
from app.dataset_encoder import JsonEncoder, TableEncoder


class UnknownType:
    def __init__(self):
        self.value = 'a'

class TestTableEncoder(unittest.TestCase):
    def test_unknown_type(self):
        obj = UnknownType()
        enc = TableEncoder()

        with self.assertRaises(TypeError):
            enc.encode(obj)
        with self.assertRaises(NotImplementedError):
            enc.decode("random", "random_type")

    def test_sample_table(self):
        sample = """
| UID | Pool | Prompt | Weight | Sensitivity | Flags |
| 1 | test | test | 1 | S | test |
"""
        enc = TableEncoder()
        header = enc.get_header_pretty()
        self.assertTrue(header in sample)

        entry = DatasetEntry(1, "test", "test", 1, "S", "test")
        row = enc.encode(entry)
        self.assertTrue(row in sample)

class TestJsonEncoder(unittest.TestCase):
    def test_sample_entry(self):
        sample = """{
    "text": "test",
    "weight": 1,
    "sensitivity": "S",
    "flags": [
        "test"
    ]
}"""
        enc = JsonEncoder()
        entry = DatasetEntry(1, "test", "test", 1, "S", "test")
        output = json.dumps(enc.encode(entry), indent=4)
        self.assertEqual(sample, output)
