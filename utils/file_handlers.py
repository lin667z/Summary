import os
from typing import List
from utils.logger import configure_logger

logger = configure_logger()

def get_book_list(book_dir: str) -> List[str]:
    """获取指定目录下的所有书籍文件"""
    try:
        book_list = []
        for root, _, files in os.walk(book_dir):
            book_list.extend([os.path.join(root, f) for f in files])
        logger.info(f"Found {len(book_list)} books in directory")
        return book_list
    except Exception as e:
        logger.error(f"Error listing books: {str(e)}")
        raise

def save_content(content: str, filepath: str) -> None:
    """安全保存内容到文件"""
    try:
        # os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Successfully saved to {filepath}")
    except (IOError, PermissionError) as e:
        logger.error(f"Save failed: {str(e)}")
        raise