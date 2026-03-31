import os
import datetime
import time
from moto_ocr.commission import match_premium
from moto_ocr.config import LEDGER_TEMPLATE_NAME
from moto_ocr.ocr_service import get_access_token, ocr_image, extract_info
from moto_ocr.output_manager import (
    move_to_processed,
    create_ledger,
    find_last_ledger_row,
    create_group_excel,
    write_ledger_row_for_result,
    generate_settlement_files,
)


def batch_process(image_folder):
    """批量处理图片文件夹。
    
    Args:
        image_folder: 图片根目录路径（如 "./图片"）
    """
    access_token = get_access_token()
    if not access_token:
        print("获取access_token失败，退出")
        return
    
    group_results = {}
    current_date = datetime.datetime.now()
    current_date_str = current_date.strftime("%Y.%m.%d")
    current_month = current_date.month
    date_str = current_date.strftime("%m月%d日")
    
    ocr_failed_files = []
    
    for root, dirs, files in os.walk(image_folder):
        for filename in files:
            if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                image_path = os.path.join(root, filename)
                text = ocr_image(image_path, access_token)
                
                if text is None:
                    ocr_failed_files.append(os.path.relpath(image_path, image_folder))
                    print(f"  ⚠ OCR识别失败，跳过：{filename}")
                    continue
                
                info = extract_info(text)
                
                processed_path = move_to_processed(image_path, image_folder)
                
                info["图片名称"] = os.path.relpath(processed_path, os.path.dirname(image_folder))
                folder_path = os.path.dirname(os.path.relpath(processed_path, os.path.dirname(image_folder)))
                info["所属文件夹"] = folder_path if folder_path else "根目录"
                
                path_parts = folder_path.split(os.sep)
                group_name = path_parts[-1] if len(path_parts) > 2 else "默认群组"
                
                person_name = os.path.basename(os.path.dirname(os.path.dirname(image_path)))
                date_folder = os.path.join(os.path.dirname(image_folder), "结果", date_str)
                result_folder = os.path.join(date_folder, person_name)
                
                if group_name not in group_results:
                    group_results[group_name] = {
                        "results": [],
                        "date_folder": result_folder,
                    }
                group_results[group_name]["results"].append(info)
                
                time.sleep(0.5)
    
    if ocr_failed_files:
        print(f"\n⚠ 共 {len(ocr_failed_files)} 张图片OCR识别失败，未移动：")
        for f in ocr_failed_files:
            print(f"  - {f}")
    
    if not group_results:
        print("未找到任何图片")
        return
    
    # 准备台账
    ledger_filename = f"{current_date.year}年{current_date.month}月摩托车台账.xlsx"
    ledger_path = os.path.join(os.path.dirname(os.path.abspath(image_folder)), "结果", ledger_filename)
    template_path = os.path.join(os.path.dirname(os.path.abspath(image_folder)), "结果", LEDGER_TEMPLATE_NAME)
    
    ledger_wb, ledger_ws = create_ledger(ledger_path, template_path)
    if ledger_ws is None:
        return
    
    last_row, last_number = find_last_ledger_row(ledger_ws)
    
    # 处理每个群组
    commission_stats = {}
    for group_name, data in group_results.items():
        os.makedirs(data["date_folder"], exist_ok=True)
        
        excel_path, stats = create_group_excel(
            group_name, data["results"], data["date_folder"], current_date_str, current_month
        )
        commission_stats[group_name] = stats
        
        # 同步到台账
        for result in data["results"]:
            raw_amount = result["实付金额"]
            if raw_amount == "未识别到金额":
                total_amount = 0
            else:
                try:
                    total_amount = int(raw_amount)
                except ValueError:
                    print(f"  ⚠ 金额格式异常：{raw_amount!r}，按0处理")
                    total_amount = 0
            matched = match_premium(total_amount, month=current_month)
            
            if matched:
                compulsory = matched["compulsory"]
                accident = matched["accident"]
            else:
                person_name = os.path.basename(data["date_folder"])
                print(f"【{person_name}】的【{group_name}】中出现金额不匹配保单：【{result['姓名']}】，金额【{total_amount}】")
                compulsory = 0
                accident = 0
            
            last_number, last_row = write_ledger_row_for_result(
                ledger_ws, last_row, last_number, result,
                compulsory, accident, total_amount, group_name, current_date_str
            )
    
    # 保存台账
    try:
        ledger_wb.save(ledger_path)
        ledger_wb.close()
        print(f"\n月度台账已更新：{ledger_path}")
    except Exception as e:
        print(f"保存月度台账时出错：{str(e)}")
    
    # 生成结算文件
    generate_settlement_files(commission_stats)


if __name__ == "__main__":
    batch_process("./图片")
