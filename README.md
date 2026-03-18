# 财务会计文书技能

## 概述
这是一个轻量级财务会计技能包，当前提供以下能力：

- 记录收入、支出、转账
- 导入标准 CSV 银行流水
- 计算增值税和企业所得税
- 生成基础资产负债表和利润表
- 按期间过滤数据，支持 `YYYY-MM`、`YYYY-QN`、`YYYY`、`YYYY-MM-DD`

## 安装依赖
```bash
pip install pandas openpyxl reportlab pyyaml
```

如果你使用 conda，也可以直接用对应环境中的 Python 运行，例如：

```bash
/opt/homebrew/Caskroom/miniconda/base/envs/python3.12/bin/python script/finance.py --help
```

## 快速开始
```bash
# 记录一笔收入
python script/finance.py record --type income --amount 50000 --account 4001 --description "产品销售" --category "销售收入" --date 2026-02-01

# 记录一笔支出
python script/finance.py record --type expense --amount 15000 --account 5001 --description "采购原材料" --category "主营业务成本" --date 2026-02-05

# 查看余额
python script/finance.py balance

# 计算税款
python script/finance.py tax --type vat --period 2026-02
python script/finance.py tax --type income_tax --period 2026-Q1

# 生成报表
python script/finance.py report --type balance_sheet --period 2026-02 --output balance_sheet.json
python script/finance.py report --type income_statement --period 2026-Q1 --output income_statement.json

# 导入银行流水
python script/finance.py import --file examples/bank_statement.csv
```

## 命令说明

### 1. `record`
记录单笔交易。

```bash
python script/finance.py record \
  --type income \
  --amount 1000 \
  --account 4001 \
  --description "销售产品" \
  --category "销售收入" \
  --date 2026-02-28
```

参数：

- `--type`: `income`、`expense`、`transfer`
- `--amount`: 金额
- `--account`: 会计科目编号
- `--description`: 交易描述
- `--category`: 分类
- `--date`: 日期，默认当天

### 2. `balance`
查看当前交易汇总。

```bash
python script/finance.py balance
```

### 3. `tax`
计算税款。

```bash
python script/finance.py tax --type vat --period 2026-02
python script/finance.py tax --type income_tax --period 2026-Q1
python script/finance.py tax --type vat --period 2026-02 --income 50000
```

参数：

- `--type`: `vat` 或 `income_tax`
- `--period`: 统计期间
- `--income`: 可选，手动指定收入；不传时会按期间从交易记录汇总

### 4. `report`
生成基础报表，输出为 JSON。

```bash
python script/finance.py report --type balance_sheet --period 2026-02 --output balance_sheet.json
python script/finance.py report --type income_statement --period 2026-Q1 --output income_statement.json
```

参数：

- `--type`: `balance_sheet` 或 `income_statement`
- `--period`: 统计期间
- `--output`: 可选，输出文件路径

### 5. `import`
导入标准银行流水 CSV。

```bash
python script/finance.py import --file examples/bank_statement.csv
```

CSV 需要包含以下列：

```csv
date,description,amount,balance
2026-02-01,工资收入,10000.00,15000.00
2026-02-05,采购付款,-5000.00,10000.00
```

## 配置说明

### 环境变量

- `FINANCE_DATA_DIR`: 财务数据目录，默认是当前工作目录下的 `data`

示例：

```bash
export FINANCE_DATA_DIR=/path/to/finance-data
```

### 会计科目配置
会计科目文件默认使用 `FINANCE_DATA_DIR/accounts.yaml`。

仓库中提供了一份示例配置：

```yaml
accounts:
  assets:
    - code: "1001"
      name: "现金"
      type: "current_asset"
```

### 税务配置
税务配置文件默认使用 `FINANCE_DATA_DIR/tax_config.yaml`。

推荐结构如下：

```yaml
tax:
  vat:
    rate: 0.13
    declaration_period: "monthly"
  income_tax:
    standard_rate: 0.25
    threshold: 300000
    declaration_period: "quarterly"
```

脚本也兼容旧版扁平结构：

```yaml
vat_rate: 0.13
income_tax_rate: 0.25
tax_threshold: 300000
```

## 数据格式

### 交易记录
```csv
date,type,account,amount,description,category
2026-02-01,income,4001,50000.00,产品销售,销售收入
2026-02-05,expense,5001,15000.00,采购原材料,主营业务成本
```

### 银行流水
```csv
date,description,amount,balance
2026-02-01,工资收入,10000.00,15000.00
2026-02-05,采购付款,-5000.00,10000.00
```

## 测试
运行测试脚本：

```bash
python script/test_finance.py
```

如果你使用 conda：

```bash
/opt/homebrew/Caskroom/miniconda/base/envs/python3.12/bin/python script/test_finance.py
```

当前测试覆盖：

- 基础记账和余额计算
- 银行流水导入
- 嵌套税务配置兼容
- 按月份、季度、年份的期间过滤

## 注意事项

- 当前实现适合轻量记账、技能演示和自动化场景，不应直接替代正式财务系统或报税系统。
- 报表输出目前为 JSON，不生成 PDF/Excel。
- 修改税务配置后，建议重新运行测试确认结果正确。
