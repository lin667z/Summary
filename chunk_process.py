from langchain.text_splitter import RecursiveCharacterTextSplitter
from ds_api import ds_api
import re
import os
import time
from typing import Optional


def chunk_process(
        book_content: str,
        summary_template: str,
        output_path: str = "output_file.txt",
        token_num: int = 8192,
        chunk_size: int = 3200,
        chunk_overlap: int = 64,
        block_num: Optional[int] = None
) -> str:
    """
    处理文本内容的分块摘要生成流程（支持断点续传和API重试）

    参数:
        book_content (str): 原始文本内容
        summary_template (str): 摘要生成模板，需包含{text}占位符
        output_path (str): 输出文件路径，默认'output_file.txt'
        token_num (int): API调用的最大token数，默认8192
        chunk_size (int): 文本块最大尺寸，默认3200字符
        chunk_overlap (int): 块间重叠字符数，默认64
        block_num (Optional[int]): 预处理块分组数量，默认不启用

    返回:
        str: 合并后的摘要文本
    """

    # 初始化递归文本分割器
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", ". ", "! ", "? "],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )

    # 文本分块处理逻辑
    if block_num:
        pre_chunks = re.findall(
            r'<\|Im_start\|>(.*?)<\|Im_end\|>',
            book_content,
            flags=re.DOTALL
        )
        processed_chunks = []
        for i in range(0, len(pre_chunks), block_num):
            group = "".join(pre_chunks[i:i + block_num])
            processed_chunks.append(f'<|Im_start|>{group}<|Im_end|>')
        chunks = processed_chunks
    else:
        chunks = text_splitter.split_text(book_content)

    # 断点续传初始化
    start_index = 0
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            existing_content = f.read()
        existing_summaries = re.findall(r'<\|Im_start\|>(.*?)<\|Im_end\|>', existing_content, flags=re.DOTALL)
        start_index = len(existing_summaries)
        print(f"检测到已有进度，从第 {start_index + 1} 个块继续处理")

    # 处理每个文本块
    for idx in range(start_index, len(chunks)):
        chunk = chunks[idx]
        current_chunk = idx + 1

        # 进度显示
        print(f"正在处理块 {current_chunk}/{len(chunks)}...")

        # API调用重试机制
        while True:
            try:
                summary_prompt = summary_template.format(text=chunk)
                summary = ds_api(summary_prompt, token_num=token_num)

                # 写入结果并跳出循环
                with open(output_path, "a", encoding="utf-8") as f:
                    f.write(f"<|Im_start|>{summary}<|Im_end|>\n\n")
                break
            except Exception as e:
                print(f"API调用失败: {str(e)}")
                print("10秒后重试...")
                time.sleep(10)

    # 读取最终结果
    with open(output_path, "r", encoding="utf-8") as f:
        combined_summaries = f.read().strip()

    return combined_summaries