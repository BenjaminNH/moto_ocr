# 🏍️ moto_ocr

摩托车保单 OCR 识别与佣金结算工具。通过百度 OCR 自动识别保单图片，提取客户信息，生成台账 Excel 和结算文件。

## 功能

- 批量识别保单图片，自动提取姓名和实付金额
- 智能匹配保费组合（交强险 + 意外险 + 车船税）
- 自动计算佣金（按配置文件维护意外险档位和佣金）
- 按群组生成明细 Excel
- 同步更新月度台账
- 自动生成结算文本
- 图片自动归档
- 多 OCR 接口自动降级（配额不足自动切换）

## 快速开始

### 1. 安装依赖

```bash
pip install requests python-dotenv openpyxl
```

### 2. 配置 OCR 凭证

复制 `.env.example` 为 `.env`，填入你的百度 OCR 凭证：

```bash
BAIDU_API_KEY=your_api_key_here
BAIDU_SECRET_KEY=your_secret_key_here
```

凭证获取：[百度智能云控制台](https://console.bce.baidu.com/) → 文字识别 → 应用管理

### 3. 放置图片

将待识别的保单图片放入 `图片/` 目录，按以下结构组织：

```
图片/
├── 张三/
│   ├── 群组A/
│   │   ├── policy1.png
│   │   └── policy2.jpg
│   └── 群组B/
│       └── policy3.png
└── 李四/
    └── 群组C/
        └── policy4.png
```

### 4. 运行

双击 `点击运行.bat`，或执行：

```bash
python -m moto_ocr.main
```

## 输出

运行后会在同级目录生成：

```
结果/
├── 03月31日/
│   ├── 张三/
│   │   ├── 群组A.xlsx        # 群组明细
│   │   ├── 群组B.xlsx
│   │   └── 结算.txt           # 佣金结算
│   └── 李四/
│       └── 群组C.xlsx
└── 2026年3月摩托车台账.xlsx    # 月度台账

图片归档/
└── 03月31日/                  # 已处理图片自动归档
    └── ...
```

## 结算规则配置

保费与佣金规则已改为外部配置文件 `settlement_rules.json`，后续常见调整只需要改这个文件，不需要改 Python 代码。

当前默认规则：

- 交强险档位：`104`、`156`
- 156 交强险可按月份叠加税额
- 月税额：1 月 `36`，2 月 `33`，3 月 `30`，依次每月递减 `3`
- 意外险 `200`，佣金 `0`
- 意外险 `302`，佣金 `30`
- 意外险 `400`，佣金 `50`

系统会自动按 `交强险 + 意外险 + 税额` 枚举匹配总金额。

### 配置字段说明

`settlement_rules.json` 当前字段如下：

- `accident_plans`：意外险方案列表，也是最常改的配置，已放在第一项。
- `accident_plans[].amount`：意外险金额。
- `accident_plans[].commission`：该意外险金额对应的佣金。
- `compulsory_amounts`：允许参与匹配的交强险金额列表。
- `taxable_compulsory_amounts`：哪些交强险金额允许叠加车船税。
- `monthly_tax`：每个月对应的税额表，键是月份 `1-12`，值是该月税额。

示例：

```json
{
  "accident_plans": [
    { "amount": 200, "commission": 0 },
    { "amount": 302, "commission": 30 },
    { "amount": 400, "commission": 50 }
  ],
  "compulsory_amounts": [104, 156],
  "taxable_compulsory_amounts": [156],
  "monthly_tax": {
    "1": 36,
    "2": 33,
    "3": 30,
    "4": 27,
    "5": 24,
    "6": 21,
    "7": 18,
    "8": 15,
    "9": 12,
    "10": 9,
    "11": 6,
    "12": 3
  }
}
```

常见修改方式：

- 新增一个意外险档位：在 `accident_plans` 里追加一条 `{ "amount": 金额, "commission": 佣金 }`
- 修改某档佣金：直接改对应 `commission`
- 调整哪类交强险带税：修改 `taxable_compulsory_amounts`
- 调整月税额：修改 `monthly_tax`

## 项目结构

```
moto_ocr/
├── config.py          # API 凭证、OCR 接口、Excel 配置
├── ocr_service.py     # 百度 OCR 调用与信息提取
├── commission.py      # 保费匹配与佣金计算
├── output_manager.py  # 文件归档、Excel 生成、台账同步
├── settlement.py      # 结算文本生成
├── file_utils.py      # 文件工具（唯一文件名）
└── main.py            # 入口
```

## 维护说明

项目内维护约定、结算规则变更要求、测试要求和提交规范见 `AGENTS.md`。

## 注意事项

- 首次运行需在 `结果/` 目录放置台账模板文件（文件名在 `config.py` 中配置）
- OCR 识别失败的图片不会被移动，可重新运行
- 所有 `requests` 请求均设置了 30 秒超时
