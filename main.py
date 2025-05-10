from ds_api import ds_api
from chunk_process import chunk_process
import os

MAX_CHUNK_LENGTH = 30000  # 单次处理的最大文本长度
DEFAULT_TOKEN_NUM = 20480  # 默认API token限额
BLOCK_NUM_REDUCE = 3  # 递归分块处理时的分块数量


def process_book(book_file, output_md):
    """
    书籍处理主函数
    参数：
        book_path: str, 原始书籍文件路径
        chunk_output: str, 初始分块总结输出路径
        output_md: str, 最终输出文件路径
    """

    # 加载原始书籍内容
    with open(book_file, 'r', encoding='utf-8') as f:
        book_content = f.read()
    print(f"成功加载{os.path.splitext(os.path.basename(book_file))[0]}书籍内容，长度：{len(book_content)}字符")

    # 初始分块处理
    summary_template = """用英语总结文本块，文本块如下：
    {text}
    """
    combined_summaries = chunk_process(
        book_content=book_content,
        summary_template=summary_template,
    )
    print(f"初始分块处理完成，总长度：{len(combined_summaries)}字符")

    # 递归处理长文本（当总结过长时进行多级分块）
    while len(combined_summaries) > MAX_CHUNK_LENGTH:
        print("检测到总结过长，进行递归分块处理...")
        combined_summaries = chunk_process(
            book_content=combined_summaries,
            summary_template=summary_template,
            block_num=BLOCK_NUM_REDUCE
        )
        print(f"递归处理后长度：{len(combined_summaries)}字符")

    # 生成最终摘要（Introduction部分）
    final_template = """以下是某长文本的分段总结，请将其整合为一个连贯的摘要，突出整体逻辑和结论。多个文本片段总结如下：
{summaries}
输出格式如下，不要分点输出，并全部使用英文输出：
## Introduction
“正文内容......”
"""
    final_prompt = final_template.format(summaries=combined_summaries)

    print("\n" + "=" * 30)
    print("Generating Introduction...")
    final_analysis = ds_api(final_prompt, token_num=DEFAULT_TOKEN_NUM)
    final_analysis += '\n\n'

    # 保存Introduction部分
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write(final_analysis)
    print(f"成功生成Introduction，已保存至：{output_md}")

    # 生成关键点
    points_template = """根据我为你提供的资料，帮我生成5到7个关键点。多个文本摘要如下:
{summaries}
输出格式如下，不要分点输出，并全部使用英文输出：
## 关键点1的标题
“正文内容（至少三段）......”
## 关键点2的标题
“正文内容（至少三段）......”
......(至少5个关键点)
"""
    points_prompt = points_template.format(summaries=combined_summaries)

    print("\n" + "=" * 30)
    print("Generating key points...")
    points_analysis = ds_api(points_prompt, DEFAULT_TOKEN_NUM)

    # 追加关键点分析到文件
    with open(output_md, 'a', encoding='utf-8') as f:
        f.write(points_analysis)
    print(f"成功生成关键点分析，已追加至：{output_md}")


if __name__ == "__main__":
    # 获取所有书
    book_dir = './load_books/format_data'
    book_list = []
    for root, dirs, files in os.walk(book_dir):
        for file in files:
            # 拼接文件的完整路径
            file_path = os.path.join(root, file)
            book_list.append(file_path)
            print(file_path)

    # 遍历所有书
    for book_path in book_list:
        process_book(book_path, output_md=os.path.splitext(os.path.basename(book_path))[0]+".md")
    print("\n处理流程全部完成！")
