from concurrent import futures
import os
import re
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

def extract_epub_text(epub_path):
    """从单个EPUB文件中提取文本"""
    book = epub.read_epub(epub_path)
    text = []
    # 遍历所有文档类型的item
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        # 使用BeautifulSoup解析内容
        soup = BeautifulSoup(item.get_content(), 'xml')
        # 提取纯文本并合并
        fina_text = re.sub(r' {2,}', '\n', soup.get_text().strip().replace('\n',' ').replace('\xa0', ''))
        text.append(fina_text)

    return '\n\n'.join(text)

def process_epub_directory(directory, output_dir):
    """批量处理目录下的所有EPUB文件"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(directory):
        if filename.endswith('.epub'):
            epub_path = os.path.join(directory, filename)
            try:
                print(f"正在处理: {filename}")
                text = extract_epub_text(epub_path)
                # 生成输出文件名
                output_name = os.path.splitext(filename)[0] + '.txt'
                output_path = os.path.join(output_dir, output_name)
                # 写入文本文件
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                print(f"已保存: {output_name}")
            except Exception as e:
                print(f"处理 {filename} 时出错: {str(e)}")

if __name__ == '__main__':
    epub_dir = 'data'       # EPUB文件所在目录
    output_dir = 'format_data'    # 提取的文本存放目录
    process_epub_directory(epub_dir, output_dir)