import os
from dotenv import load_dotenv

load_dotenv()

# 百度OCR配置
API_KEY = os.getenv("BAIDU_API_KEY")
SECRET_KEY = os.getenv("BAIDU_SECRET_KEY")

if not API_KEY or not SECRET_KEY:
    raise ValueError("请在 .env 文件中配置 BAIDU_API_KEY 和 BAIDU_SECRET_KEY")

# OCR接口URL列表，按优先级排序
OCR_URLS = [
    "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic",  # 高精度版
    "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic",   # 标准版
    "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate",       # 高精度含位置版
    "https://aip.baidubce.com/rest/2.0/ocr/v1/general"         # 标准含位置版
]

# 请求超时（秒）
REQUEST_TIMEOUT = 30

# Excel表头
EXCEL_HEADERS = ["序号", "客户姓名", "交强险", "意外险", "总金额", "佣金", "日期", "出单点"]

# 列宽配置
COLUMN_WIDTHS = {
    'A': 10,  # 序号
    'B': 20,  # 客户姓名
    'C': 15,  # 交强险
    'D': 15,  # 意外险
    'E': 15,  # 总金额
    'F': 15,  # 佣金
    'G': 15,  # 日期
    'H': 20,  # 出单点
}

# 台账模板文件名
LEDGER_TEMPLATE_NAME = "2025年3月摩托车台账.xlsx"
