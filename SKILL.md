---
name: finance-accounting
version: 1.0.0
description: "财务会计处理技能包，提供记账、银行流水导入、税务计算和基础报表生成"
author: 天元 (⚡)
category: finance
tags: [accounting, finance, tax, document, invoice]
dependencies:
  - python>=3.11
  - pandas
  - openpyxl
  - reportlab
---

# 财务会计文书技能

## 概述
本技能包提供轻量级财务会计处理能力，包括记账、银行流水导入、税务计算和基础报表生成。

## 当前支持的功能

### 1. 基础记账
- **流水账记录**: 收入、支出、转账记录
- **科目字段**: 记录会计科目编号
- **余额计算**: 实时计算账户余额

### 2. 数据导入
- **银行流水导入**: 将标准 CSV 银行流水转换为收入/支出记录
- **批量入账**: 自动写入交易台账

### 3. 税务模块
- **增值税计算**: 支持按期间统计收入后计算
- **企业所得税计算**: 根据阈值和税率计算

### 4. 报表模块
- **资产负债表**: 输出 JSON 格式基础资产负债表
- **利润表**: 输出 JSON 格式利润表
- **期间过滤**: 支持 `YYYY-MM`、`YYYY-QN`、`YYYY`、`YYYY-MM-DD`

## 使用方法

### 基本记账
```bash
# 记录收入
python script/finance.py record --type income --amount 1000 --account 4001 --description "销售产品" --category "销售收入" --date "2026-02-28"

# 记录支出
python script/finance.py record --type expense --amount 500 --account 5001 --description "购买办公用品" --category "办公费用" --date "2026-02-28"

# 查看余额
python script/finance.py balance
```

### 数据导入
```bash
# 导入银行流水 CSV
python script/finance.py import --file examples/bank_statement.csv
```

### 税务计算
```bash
# 计算增值税
python script/finance.py tax --type vat --period 2026-02

# 计算企业所得税
python script/finance.py tax --type income_tax --period 2026-Q1
```

### 报表生成
```bash
# 生成资产负债表
python script/finance.py report --type balance_sheet --period 2026-02 --output balance_sheet.json

# 生成利润表
python script/finance.py report --type income_statement --period 2026-Q1 --output income_statement.json
```

## 环境变量

在使用本技能之前，需要预先设置以下环境变量：

| 环境变量 | 必填 | 默认值 | 说明 |
|----------|------|--------|------|
| `FINANCE_DATA_DIR` | 否 | `data` | 财务数据存储目录，用于存放交易记录（`transactions.csv`）以及运行时使用的账户和税务配置（`accounts.yaml`、`tax_config.yaml`）。若未设置，将在当前工作目录下自动创建 `data` 子目录。 |

### 设置示例

```bash
# Linux / macOS
export FINANCE_DATA_DIR=/path/to/your/finance/data

# Windows (命令提示符)
set FINANCE_DATA_DIR=C:\path\to\your\finance\data

# Windows (PowerShell)
$env:FINANCE_DATA_DIR = "C:\path\to\your\finance\data"
```

> **注意**：如果指定目录不存在，脚本会自动创建该目录。建议将此变量写入系统的环境变量配置文件（如 `~/.bashrc`、`~/.zshrc`）以便长期生效。

## 配置文件

### 会计科目设置
```yaml
# config/accounts.yaml
accounts:
  assets:
    - code: 1001
      name: 现金
      type: current_asset
    - code: 1002
      name: 银行存款
      type: current_asset
  
  liabilities:
    - code: 2001
      name: 短期借款
      type: current_liability
  
  equity:
    - code: 3001
      name: 实收资本
      type: equity
  
  income:
    - code: 4001
      name: 主营业务收入
      type: revenue
  
  expenses:
    - code: 5001
      name: 办公费用
      type: expense
```

### 税务设置
```yaml
# config/tax_config.yaml
tax:
  vat:
    rate: 0.13
    declaration_period: monthly
  income_tax:
    standard_rate: 0.25
    threshold: 300000
    declaration_period: quarterly
```

## 数据格式

### 交易记录格式
```csv
date,type,account,amount,description,category
2026-02-28,income,4001,1000.00,销售产品,销售收入
2026-02-28,expense,5001,500.00,购买办公用品,办公费用
```

### 银行流水格式
```csv
date,description,amount,balance
2026-02-28,工资收入,10000.00,15000.00
2026-02-28,水电费支出,-500.00,14500.00
```

## 安全注意事项

### 数据安全
- 仓库当前未内置加密和权限控制
- 建议将数据目录放在受限路径并自行备份

### 合规性
- 符合会计准则
- 遵守税务法规
- 审计追踪

## 故障排除

### 常见问题
1. **数据导入失败**: 检查 CSV 列是否包含 `date,description,amount,balance`
2. **计算错误**: 检查 `FINANCE_DATA_DIR` 下的 `tax_config.yaml` 是否符合示例结构
3. **报表生成失败**: 确认目标期间存在交易记录

### 日志查看
```bash
# 查看运行日志
tail -f logs/finance.log

# 查看错误日志
tail -f logs/error.log
```

## 更新计划

### 近期更新
- [ ] 添加更多报表模板
- [ ] 支持更多银行格式
- [ ] 优化税务计算算法

### 长期规划
- [ ] AI智能分析功能
- [ ] 预测和预算功能
- [ ] 多语言支持

---

**技能状态**: ✅ 就绪  
**最后更新**: 2026-02-28  
**维护者**: 天元 (⚡)
