import re
import base64
import requests
from moto_ocr.config import API_KEY, SECRET_KEY, OCR_URLS, REQUEST_TIMEOUT

_NAME_PATTERNS = [
    re.compile(r"姓名：(\S+)"),
    re.compile(r"姓名\s*[\n\r]*(\S+)"),
]

_AMOUNT_PATTERNS = [
    re.compile(r"实付金额：￥(\d+(?:\.\d{2})?)"),
    re.compile(r"实付金额\s*[\n\r]*￥(\d+(?:\.\d{2})?)"),
]


def get_access_token():
    """获取百度OCR access_token。
    
    Returns:
        str: access_token，失败返回None
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": API_KEY,
        "client_secret": SECRET_KEY,
    }
    
    try:
        response = requests.post(url, params=params, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print("获取access_token失败")
            return None
    except Exception as e:
        print(f"获取access_token异常：{str(e)}")
        return None


def ocr_image(image_path, token):
    """对图片进行OCR识别。
    
    Args:
        image_path: 图片路径
        token: access_token
        
    Returns:
        str: 识别文本，失败返回None
    """
    with open(image_path, "rb") as f:
        img = base64.b64encode(f.read()).decode()
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = {"image": img, "access_token": token}
    
    for ocr_url in OCR_URLS:
        print(f"当前接口：{ocr_url}")
        try:
            response = requests.post(ocr_url, headers=headers, data=payload, timeout=REQUEST_TIMEOUT)
            if response.status_code != 200:
                print(f"接口请求失败，状态码：{response.status_code}")
                continue
                
            result = response.json()
            if 'error_code' in result:
                if result['error_code'] in [17, 18]:
                    print(f"接口配额不足，尝试下一个接口\n")
                    continue
                print(f"接口返回错误：{result['error_msg']}")
                continue
            
            if 'words_result' in result:
                if isinstance(result['words_result'], list):
                    return "\n".join([item["words"] for item in result["words_result"]])
                return "\n".join([item["words"] for item in result['words_result'].values()])
        except Exception as e:
            print(f"调用接口时发生错误：{str(e)}")
    
    print("所有OCR接口均调用失败")
    return None


def extract_info(text):
    """从OCR文本中提取姓名和金额。
    
    Args:
        text: OCR识别文本
        
    Returns:
        dict: {"姓名": str, "实付金额": str}
    """
    if not text:
        return {"姓名": "未识别到姓名", "实付金额": "未识别到金额"}
    
    name = "未识别到姓名"
    for pattern in _NAME_PATTERNS:
        match = pattern.search(text)
        if match:
            name = match.group(1)
            break
    
    amount = "未识别到金额"
    for pattern in _AMOUNT_PATTERNS:
        match = pattern.search(text)
        if match:
            amount = match.group(1).split('.')[0]
            break

    return {"姓名": name, "实付金额": amount}
