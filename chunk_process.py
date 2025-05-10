from langchain.text_splitter import RecursiveCharacterTextSplitter
from ds_api import ds_api
import re

def chunk_process(book_content,
                  summary_template,
                  output_path:str = 'output_file.txt',
                  token_num: int = 10240,
                  chunk_size:int = 3200,
                  chunk_overlap:int = 64,
                  block_num=None):
    # 初始化文本分割器
    text_splitter_01 = RecursiveCharacterTextSplitter(
        separators=["\n\n", ". ", "! ", "? "],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    # 分割文本块
    if block_num:
        chunks = []
        pre_chunks = re.findall(r'<\|Im_start\|>(.*?)<\|Im_end\|>', book_content, flags=re.DOTALL)
        for i in range(0,len(pre_chunks),block_num):
            for j in range(i,i+block_num):
                if i == 0:
                    print(pre_chunks[j])
                chunks.append(pre_chunks[j])
        chunks = text_splitter_01.split_text(book_content)
    else :
        chunks = text_splitter_01.split_text(book_content)

    # 处理所有文本块
    chunk_summaries = []
    # with open(output_path, 'w', encoding='utf-8') as f:
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i + 1}/{len(chunks)}...")
        summary_prompt = summary_template.format(text=chunk)
        summary = ds_api(summary_prompt, token_num=token_num)
        # f.write('<|Im_start|>'+summary+'<|Im_end|>')
        chunk_summaries.append(summary)
        if i in [0, 1]:
            print(summary)
        print(f"Chunk {i + 1} summary completed")


    # 合并所有摘要
    combined_summaries = "\n\n".join(chunk_summaries)

    return combined_summaries


