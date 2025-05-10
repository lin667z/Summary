from langchain.text_splitter import RecursiveCharacterTextSplitter
from ds_api import ds_api
import re
from typing import Optional


def chunk_process(
        book_content: str,
        summary_template: str,
        token_num: int = 10240,
        chunk_size: int = 3200,
        chunk_overlap: int = 64,
        block_num: Optional[int] = None
) -> str:
    """
    处理文本内容的分块摘要生成流程

    参数:
        book_content (str): 原始文本内容
        summary_template (str): 摘要生成模板，需包含{text}占位符
        output_path (str): 输出文件路径，默认'output_file.txt'
        token_num (int): API调用的最大token数，默认10240
        chunk_size (int): 文本块最大尺寸，默认3200字符
        chunk_overlap (int): 块间重叠字符数，默认64
        block_num (Optional[int]): 预处理块分组数量，默认不启用

    返回:
        str: 合并后的摘要文本
    """

    # 初始化递归文本分割器
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", ". ", "! ", "? "],  # 按段落>句子分割
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

        # 按block_num分组处理原始块
        processed_chunks = []
        for i in range(0, len(pre_chunks), block_num):
            group = "".join(pre_chunks[i:i + block_num])
            processed_chunks.append('<|Im_start|>'+group+'<|Im_end|>')
        chunks = processed_chunks
    else:
        # 直接分割原始文本
        chunks = text_splitter.split_text(book_content)

    # 摘要生成与结果保存
    chunk_summaries = []
    for idx, chunk in enumerate(chunks):
        # 进度显示（每处理10个块显示进度）
        if idx % 10 == 0:
            print(f"Processing chunk {idx + 1}/{len(chunks)}...")

        # 生成摘要提示词并调用API
        summary_prompt = summary_template.format(text=chunk)
        summary = ds_api(summary_prompt, token_num=token_num)

        # 保存结果（使用特殊标记包裹摘要）
        chunk_summaries.append(f'<|Im_start|>{summary}<|Im_end|>\n')

        # 调试
        if idx < 2:
            print(f"Sample summary {idx + 1}:\n{summary}")  # 截短显示

    # 合并所有摘要为最终结果
    combined_summaries = "\n\n".join(chunk_summaries)
    return combined_summaries
