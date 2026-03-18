#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财务会计核心脚本
功能：记账、对账、税务计算、报表生成
"""

import argparse
import pandas as pd
import json
import yaml
import os
from datetime import datetime
from pathlib import Path
import re

class FinanceAccounting:
    """财务会计核心类"""
    
    def __init__(self, data_dir=None):
        """初始化财务系统"""
        if data_dir is None:
            env_data_dir = os.getenv("FINANCE_DATA_DIR")
            if env_data_dir:
                data_dir = env_data_dir
            else:
                data_dir = "data"
                print("提示: 未设置 FINANCE_DATA_DIR，当前使用默认数据目录: data")
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # 初始化数据文件
        self.transactions_file = self.data_dir / "transactions.csv"
        self.accounts_file = self.data_dir / "accounts.yaml"
        self.tax_config_file = self.data_dir / "tax_config.yaml"
        
        # 加载配置
        self.load_config()
    
    def load_config(self):
        """加载配置"""
        # 默认账户设置
        self.accounts = {
            "assets": [
                {"code": "1001", "name": "现金", "type": "current_asset"},
                {"code": "1002", "name": "银行存款", "type": "current_asset"}
            ],
            "liabilities": [
                {"code": "2001", "name": "短期借款", "type": "current_liability"}
            ],
            "equity": [
                {"code": "3001", "name": "实收资本", "type": "equity"}
            ],
            "income": [
                {"code": "4001", "name": "主营业务收入", "type": "revenue"}
            ],
            "expenses": [
                {"code": "5001", "name": "办公费用", "type": "expense"}
            ]
        }
        
        # 默认税务配置
        self.tax_config = {
            "vat_rate": 0.13,  # 增值税率
            "income_tax_rate": 0.25,  # 企业所得税率
            "tax_threshold": 300000,  # 起征点
            "declarations": {
                "vat": "monthly",
                "income_tax": "quarterly"
            }
        }
        
        # 尝试加载现有配置
        if self.accounts_file.exists():
            with open(self.accounts_file, 'r', encoding='utf-8') as f:
                self.accounts = yaml.safe_load(f)
        
        if self.tax_config_file.exists():
            with open(self.tax_config_file, 'r', encoding='utf-8') as f:
                loaded_tax_config = yaml.safe_load(f)
                if loaded_tax_config:
                    self.tax_config = self._normalize_tax_config(loaded_tax_config)

    def _normalize_tax_config(self, config):
        """兼容扁平和嵌套两种税务配置结构"""
        if "vat_rate" in config:
            return config

        tax_config = config.get("tax", config)
        vat_config = tax_config.get("vat", {})
        income_tax_config = tax_config.get("income_tax", {})
        declarations = tax_config.get("declarations", {})

        return {
            "vat_rate": vat_config.get("rate", 0.13),
            "income_tax_rate": income_tax_config.get("standard_rate", 0.25),
            "tax_threshold": income_tax_config.get("threshold", 300000),
            "declarations": {
                "vat": vat_config.get("declaration_period", declarations.get("vat", "monthly")),
                "income_tax": income_tax_config.get(
                    "declaration_period",
                    declarations.get("income_tax", "quarterly"),
                ),
            },
            "raw": tax_config,
        }

    def _load_transactions(self):
        """加载交易数据"""
        if not self.transactions_file.exists():
            return None

        df = pd.read_csv(self.transactions_file, encoding='utf-8')
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        return df.dropna(subset=["date"])

    def _filter_transactions_by_period(self, df, period):
        """按期间过滤交易，支持 YYYY-MM / YYYY-QN / YYYY / YYYY-MM-DD"""
        if not period:
            return df

        month_match = re.fullmatch(r"(\d{4})-(\d{2})", period)
        quarter_match = re.fullmatch(r"(\d{4})-Q([1-4])", period, re.IGNORECASE)
        year_match = re.fullmatch(r"\d{4}", period)
        day_match = re.fullmatch(r"\d{4}-\d{2}-\d{2}", period)

        if day_match:
            target_date = pd.Timestamp(period)
            return df[df["date"].dt.normalize() == target_date]

        if month_match:
            year, month = map(int, month_match.groups())
            return df[(df["date"].dt.year == year) & (df["date"].dt.month == month)]

        if quarter_match:
            year = int(quarter_match.group(1))
            quarter = int(quarter_match.group(2))
            start_month = (quarter - 1) * 3 + 1
            end_month = start_month + 2
            return df[
                (df["date"].dt.year == year)
                & (df["date"].dt.month >= start_month)
                & (df["date"].dt.month <= end_month)
            ]

        if year_match:
            year = int(period)
            return df[df["date"].dt.year == year]

        return df
    
    def record_transaction(self, date, trans_type, account, amount, description, category):
        """记录交易"""
        # 创建交易记录
        transaction = {
            "date": date,
            "type": trans_type,  # income/expense/transfer
            "account": account,
            "amount": float(amount),
            "description": description,
            "category": category,
            "timestamp": datetime.now().isoformat()
        }
        
        # 保存到CSV
        df = pd.DataFrame([transaction])
        
        if self.transactions_file.exists():
            df.to_csv(self.transactions_file, mode='a', header=False, index=False, encoding='utf-8')
        else:
            df.to_csv(self.transactions_file, index=False, encoding='utf-8')
        
        print(f"Transaction recorded: {description} - ¥{amount}")
        return transaction
    
    def get_balance(self):
        """计算余额"""
        df = self._load_transactions()
        if df is None:
            print("暂无交易记录")
            return {"total_income": 0, "total_expense": 0, "balance": 0}

        total_income = df[df['type'] == 'income']['amount'].sum()
        total_expense = df[df['type'] == 'expense']['amount'].sum()
        balance = total_income - total_expense
        
        result = {
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": balance,
            "transaction_count": len(df)
        }
        
        print(f"Financial Overview:")
        print(f"  Total Income: ¥{total_income:,.2f}")
        print(f"  Total Expense: ¥{total_expense:,.2f}")
        print(f"  Current Balance: ¥{balance:,.2f}")
        print(f"  Transaction Count: {len(df)}")
        
        return result
    
    def calculate_tax(self, tax_type, period, income=None):
        """计算税款"""
        if tax_type == "vat":
            # 增值税计算
            if income is None:
                df = self._load_transactions()
                if df is None:
                    print("❌ 无交易记录，无法计算税款")
                    return None
                df = self._filter_transactions_by_period(df, period)
                income = df[df['type'] == 'income']['amount'].sum()
            
            vat_amount = income * self.tax_config["vat_rate"]
            
            result = {
                "tax_type": "增值税",
                "period": period,
                "income": income,
                "tax_rate": self.tax_config["vat_rate"],
                "tax_amount": vat_amount,
                "net_income": income - vat_amount
            }
            
            print(f"VAT Calculation ({period}):")
            print(f"  Taxable Income: ¥{income:,.2f}")
            print(f"  Tax Rate: {self.tax_config['vat_rate']*100}%")
            print(f"  Tax Amount: ¥{vat_amount:,.2f}")
            print(f"  After-tax Income: ¥{income - vat_amount:,.2f}")
            
            return result
        
        elif tax_type == "income_tax":
            # 所得税计算
            if income is None:
                df = self._load_transactions()
                if df is None:
                    print("❌ 无交易记录，无法计算税款")
                    return None
                df = self._filter_transactions_by_period(df, period)
                net_income = df[df['type'] == 'income']['amount'].sum() - df[df['type'] == 'expense']['amount'].sum()
                income = max(0, net_income)
            
            # 简单计算（实际需要更复杂的累进税率）
            taxable_income = max(0, income - self.tax_config["tax_threshold"])
            tax_amount = taxable_income * self.tax_config["income_tax_rate"]
            
            result = {
                "tax_type": "企业所得税",
                "period": period,
                "income": income,
                "tax_threshold": self.tax_config["tax_threshold"],
                "taxable_income": taxable_income,
                "tax_rate": self.tax_config["income_tax_rate"],
                "tax_amount": tax_amount,
                "net_income": income - tax_amount
            }
            
            print(f"Income Tax Calculation ({period}):")
            print(f"  Total Income: ¥{income:,.2f}")
            print(f"  Tax Threshold: ¥{self.tax_config['tax_threshold']:,.2f}")
            print(f"  Taxable Income: ¥{taxable_income:,.2f}")
            print(f"  Tax Rate: {self.tax_config['income_tax_rate']*100}%")
            print(f"  Tax Amount: ¥{tax_amount:,.2f}")
            print(f"  After-tax Income: ¥{income - tax_amount:,.2f}")
            
            return result
        
        else:
            print(f"❌ 不支持的税种: {tax_type}")
            return None
    
    def generate_report(self, report_type, period, output_file=None):
        """生成报表"""
        df = self._load_transactions()
        if df is None:
            print("❌ 无交易记录，无法生成报表")
            return None

        df = self._filter_transactions_by_period(df, period)

        if report_type == "balance_sheet":
            # 简化资产负债表
            total_assets = df[df['type'] == 'income']['amount'].sum()
            total_liabilities = df[df['type'] == 'expense']['amount'].sum()
            equity = total_assets - total_liabilities
            
            report = {
                "report_type": "资产负债表",
                "period": period,
                "assets": total_assets,
                "liabilities": total_liabilities,
                "equity": equity,
                "formula": "资产 = 负债 + 所有者权益"
            }
            
            print(f"Balance Sheet ({period}):")
            print(f"  Total Assets: ¥{total_assets:,.2f}")
            print(f"  Total Liabilities: ¥{total_liabilities:,.2f}")
            print(f"  Equity: ¥{equity:,.2f}")
            
        elif report_type == "income_statement":
            # 利润表
            total_income = df[df['type'] == 'income']['amount'].sum()
            total_expense = df[df['type'] == 'expense']['amount'].sum()
            net_income = total_income - total_expense
            
            report = {
                "report_type": "利润表",
                "period": period,
                "total_income": total_income,
                "total_expense": total_expense,
                "net_income": net_income
            }
            
            print(f"Income Statement ({period}):")
            print(f"  Total Income: ¥{total_income:,.2f}")
            print(f"  Total Expense: ¥{total_expense:,.2f}")
            print(f"  Net Income: ¥{net_income:,.2f}")
            
        else:
            print(f"❌ 不支持的报表类型: {report_type}")
            return None
        
        # 保存报表
        if output_file:
            output_path = Path(output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"Report saved: {output_file}")
        
        return report
    
    def import_bank_statement(self, file_path):
        """导入银行流水"""
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            print(f"Bank statement imported: {len(df)} records")
            
            # 简单处理：转换为交易记录
            for _, row in df.iterrows():
                trans_type = "income" if row['amount'] > 0 else "expense"
                self.record_transaction(
                    date=row['date'],
                    trans_type=trans_type,
                    account="1002",  # 银行存款
                    amount=abs(row['amount']),
                    description=row['description'],
                    category="银行交易"
                )
            
            return True
        except Exception as e:
            print(f"❌ 导入失败: {e}")
            return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="财务会计处理系统")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # record命令
    record_parser = subparsers.add_parser("record", help="记录交易")
    record_parser.add_argument("--type", required=True, choices=["income", "expense", "transfer"], help="交易类型")
    record_parser.add_argument("--amount", required=True, type=float, help="金额")
    record_parser.add_argument("--account", required=True, help="会计科目")
    record_parser.add_argument("--description", required=True, help="描述")
    record_parser.add_argument("--category", required=True, help="分类")
    record_parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"), help="日期")
    
    # balance命令
    balance_parser = subparsers.add_parser("balance", help="查看余额")
    
    # tax命令
    tax_parser = subparsers.add_parser("tax", help="税务计算")
    tax_parser.add_argument("--type", required=True, choices=["vat", "income_tax"], help="税种")
    tax_parser.add_argument("--period", required=True, help="期间")
    tax_parser.add_argument("--income", type=float, help="收入金额")
    
    # report命令
    report_parser = subparsers.add_parser("report", help="生成报表")
    report_parser.add_argument("--type", required=True, choices=["balance_sheet", "income_statement"], help="报表类型")
    report_parser.add_argument("--period", required=True, help="期间")
    report_parser.add_argument("--output", help="输出文件")
    
    # import命令
    import_parser = subparsers.add_parser("import", help="导入数据")
    import_parser.add_argument("--file", required=True, help="数据文件路径")
    
    args = parser.parse_args()
    
    # 初始化财务系统
    finance = FinanceAccounting()
    
    if args.command == "record":
        finance.record_transaction(
            date=args.date,
            trans_type=args.type,
            account=args.account,
            amount=args.amount,
            description=args.description,
            category=args.category
        )
    
    elif args.command == "balance":
        finance.get_balance()
    
    elif args.command == "tax":
        finance.calculate_tax(
            tax_type=args.type,
            period=args.period,
            income=args.income
        )
    
    elif args.command == "report":
        finance.generate_report(
            report_type=args.type,
            period=args.period,
            output_file=args.output
        )
    
    elif args.command == "import":
        finance.import_bank_statement(args.file)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
