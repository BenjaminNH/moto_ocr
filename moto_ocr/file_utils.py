import os


def get_unique_filename(file_path, max_attempts=100):
    """生成不重复的文件名。
    
    Args:
        file_path: 目标文件路径
        max_attempts: 最大尝试次数
        
    Returns:
        str: 不重复的文件路径
        
    Raises:
        RuntimeError: 无法生成唯一文件名时
    """
    if not os.path.exists(file_path):
        return file_path
    
    directory = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    name, ext = os.path.splitext(filename)
    
    for counter in range(1, max_attempts + 1):
        new_filename = os.path.join(directory, f"{name}{counter}{ext}")
        if not os.path.exists(new_filename):
            return new_filename
    
    raise RuntimeError(f"无法生成唯一文件名，已尝试 {max_attempts} 次")
