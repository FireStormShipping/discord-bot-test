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
    def test_sample_entry_full_singleflag(self):
        sample = """{
    "text": "test",
    "weight": 2,
    "sensitivity": "E",
    "flags": [
        "flag"
    ]
}"""
        enc = JsonEncoder()
        entry = DatasetEntry(1, "test", "test", 2, "E", "flag")
        output = json.dumps(enc.encode(entry), indent=4)
        self.assertEqual(sample, output)

    def test_sample_entry_multiflags1(self):
        sample = """{
    "text": "test",
    "weight": 2,
    "sensitivity": "E",
    "flags": [
        "flag1",
        "flag2"
    ]
}"""
        enc = JsonEncoder()
        entry = DatasetEntry(1, "test", "test", 2, "E", "flag1,flag2")
        output = json.dumps(enc.encode(entry), indent=4)
        self.assertEqual(sample, output)

    def test_sample_entry_multiflags2(self):
        sample = """{
    "text": "test",
    "weight": 2,
    "sensitivity": "E",
    "flags": [
        "flag1",
        "flag2"
    ]
}"""
        enc = JsonEncoder()
        entry = DatasetEntry(1, "test", "test", 2, "E", "flag1, flag2")
        output = json.dumps(enc.encode(entry), indent=4)
        self.assertEqual(sample, output)

    def test_sample_entry_basic(self):
        sample = """{
    "text": "test2"
}"""
        enc = JsonEncoder()
        entry = DatasetEntry(1, "test", "test2", 1, "S", "")
        output = json.dumps(enc.encode(entry), indent=4)
        self.assertEqual(sample, output)

    def test_entry_with_escaping(self):
        sample = """{
    "text": "test2",
    "flags": [
        "A",
        "\\"extras\\" / poly"
    ]
}"""
        enc = JsonEncoder()
        entry = DatasetEntry(1, "test", "test2", 1, "S", "A,\"extras\" / poly")
        output = json.dumps(enc.encode(entry), indent=4)
        self.assertEqual(sample, output)
