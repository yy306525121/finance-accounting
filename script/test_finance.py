#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""财务会计技能测试脚本"""

import json
import os
import shutil
import sys
import unittest

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from finance import FinanceAccounting


class FinanceAccountingTestCase(unittest.TestCase):
    def setUp(self):
        self.test_dirs = [
            "tmp_test_data",
            "tmp_test_data_advanced",
            "tmp_period_data",
            "tmp_config_data",
        ]
        for dir_name in self.test_dirs:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)

    def tearDown(self):
        for dir_name in self.test_dirs:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)

        for output_file in ["test_balance_sheet.json", "test_income_statement.json"]:
            if os.path.exists(output_file):
                os.remove(output_file)

    def test_basic_functions(self):
        finance = FinanceAccounting(data_dir="tmp_test_data")

        finance.record_transaction(
            date="2026-02-28",
            trans_type="income",
            account="4001",
            amount=50000.00,
            description="产品销售",
            category="销售收入",
        )
        finance.record_transaction(
            date="2026-02-28",
            trans_type="expense",
            account="5001",
            amount=15000.00,
            description="采购原材料",
            category="主营业务成本",
        )
        finance.record_transaction(
            date="2026-02-28",
            trans_type="expense",
            account="5101",
            amount=5000.00,
            description="广告宣传",
            category="销售费用",
        )

        balance = finance.get_balance()
        self.assertEqual(balance["total_income"], 50000.00)
        self.assertEqual(balance["total_expense"], 20000.00)
        self.assertEqual(balance["balance"], 30000.00)
        self.assertEqual(balance["transaction_count"], 3)

        vat_result = finance.calculate_tax("vat", "2026-02", income=50000)
        self.assertEqual(vat_result["tax_amount"], 6500.00)

        income_tax_result = finance.calculate_tax("income_tax", "2026-02", income=30000)
        self.assertEqual(income_tax_result["tax_amount"], 0)

        balance_sheet = finance.generate_report("balance_sheet", "2026-02", "test_balance_sheet.json")
        income_statement = finance.generate_report("income_statement", "2026-02", "test_income_statement.json")

        self.assertEqual(balance_sheet["assets"], 50000.00)
        self.assertEqual(balance_sheet["liabilities"], 20000.00)
        self.assertEqual(balance_sheet["equity"], 30000.00)
        self.assertEqual(income_statement["net_income"], 30000.00)

        with open("test_income_statement.json", "r", encoding="utf-8") as f:
            saved_report = json.load(f)
        self.assertEqual(saved_report["net_income"], 30000.00)

    def test_import_bank_statement(self):
        finance = FinanceAccounting(data_dir="tmp_test_data_advanced")
        bank_file = os.path.join("examples", "bank_statement.csv")

        success = finance.import_bank_statement(bank_file)

        self.assertTrue(success)
        balance = finance.get_balance()
        self.assertEqual(balance["total_income"], 45500.00)
        self.assertEqual(balance["total_expense"], 9000.00)
        self.assertEqual(balance["balance"], 36500.00)
        self.assertEqual(balance["transaction_count"], 7)

    def test_nested_tax_config_is_supported(self):
        os.makedirs("tmp_config_data", exist_ok=True)
        shutil.copy("config/tax_config.yaml", "tmp_config_data/tax_config.yaml")

        finance = FinanceAccounting(data_dir="tmp_config_data")
        vat_result = finance.calculate_tax("vat", "2026-02", income=1000)
        income_tax_result = finance.calculate_tax("income_tax", "2026-02", income=500000)

        self.assertEqual(vat_result["tax_rate"], 0.13)
        self.assertEqual(vat_result["tax_amount"], 130.0)
        self.assertEqual(income_tax_result["tax_threshold"], 300000)
        self.assertEqual(income_tax_result["tax_amount"], 50000.0)

    def test_period_filtering(self):
        finance = FinanceAccounting(data_dir="tmp_period_data")
        finance.record_transaction(
            date="2026-01-15",
            trans_type="income",
            account="4001",
            amount=100.00,
            description="1月收入",
            category="销售收入",
        )
        finance.record_transaction(
            date="2026-02-15",
            trans_type="income",
            account="4001",
            amount=200.00,
            description="2月收入",
            category="销售收入",
        )
        finance.record_transaction(
            date="2026-03-20",
            trans_type="expense",
            account="5001",
            amount=50.00,
            description="3月支出",
            category="主营业务成本",
        )

        feb_report = finance.generate_report("income_statement", "2026-02")
        q1_report = finance.generate_report("income_statement", "2026-Q1")
        year_report = finance.generate_report("income_statement", "2026")
        feb_tax = finance.calculate_tax("vat", "2026-02")

        self.assertEqual(feb_report["total_income"], 200.0)
        self.assertEqual(feb_report["total_expense"], 0.0)
        self.assertEqual(q1_report["net_income"], 250.0)
        self.assertEqual(year_report["net_income"], 250.0)
        self.assertEqual(feb_tax["tax_amount"], 26.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
