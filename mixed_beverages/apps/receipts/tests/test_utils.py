from django.test import TestCase

from ..utils import row_to_receipt


class RowToReceiptTests(TestCase):
    def test_row_to_receipt_works(self):
        test_row = '"MB821424","ABI-HAUS                      ","959 N 2ND ST                  ","ABILENE             ","TX","79601","221","          ","2014/11", 000000963.19'
        row = test_row.replace('"', '').split(',')  # stupid csv logic
        receipt = row_to_receipt(row)
        self.assertEqual(receipt.name, 'ABI-HAUS')
