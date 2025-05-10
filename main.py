from ds_api import ds_api
from chunk_process import chunk_process


# 文本处理主函数
def process_book(book_path, output_md="book_analysis.md"):
    # # 加载书籍内容
    # with open(book_path, 'r', encoding='utf-8') as f:
    #     book_content = f.read()
    #
    # # 第一次进行分块总结
    summary_template = """用英语总结文本块，文本块如下：
    {text}
    """
    # combined_summaries = chunk_process(book_content=book_content,
    #                                    summary_template=summary_template,
    #                                    output_path=output_md,)
    with open('summaries.txt', 'r',encoding='utf8') as f:
        combined_summaries = f.read()
    print(len(combined_summaries))
    while True:
        if len(combined_summaries) > 30000:
            combined_summaries = chunk_process(book_content=combined_summaries,summary_template=summary_template, output_path='summaries_02.txt', block_num=3)
        else:
            break

    # Introduction的提示词模板
    final_template = """以下是某长文本的分段总结，请将其整合为一个连贯的摘要，突出整体逻辑和结论。多个文本片段总结如下：
{summaries}
输出格式如下，不要分点输出，并全部使用英文输出：
## Introduction
“正文内容......”
"""
    final_prompt = final_template.format(summaries=combined_summaries)
    # 生成Introduction
    print("Generating Introduction...")
    final_analysis = ds_api(final_prompt,token_num=20480)
    final_analysis = final_analysis+'\n\n'

    # 保存结果
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write(final_analysis)
    print(f"Final_analysis saved to {output_md}")


    # key points的提示词模板
    points_template = """根据我为你提供的资料，帮我生成5到7个关键点。多个文本摘要如下:
{summaries}
输出格式如下，不要分点输出，并全部使用英文输出：
## 关键点1的标题
“正文内容（至少三段）......”
## 关键点2的标题
“正文内容（至少三段）......”
......(至少5个关键点)
"""
    print("summaries:",len(combined_summaries))
    points_prompt = points_template.format(summaries=combined_summaries)
    # 生成points
    print("Generating key points...")
    points_analysis = ds_api(points_prompt,20480)
    # 保存结果
    with open(output_md, 'a', encoding='utf-8') as f:
        f.write(points_analysis)
    print(f"Points_analysis saved to {output_md}")


if __name__ == "__main__":
    book_path = "D:\py\Interview\load_books/format_data/5step.txt"
    process_book(book_path)

