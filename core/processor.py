import os
from typing import Optional
from ds_api import ds_api
from chunk_process import chunk_process
from config.setting import Config
from utils.logger import configure_logger
from utils.file_handlers import save_content

logger = configure_logger()


class BookProcessor:
    def __init__(self):
        # prompt可优化
        self.summary_template = """用英语总结文本块，文本块如下：
        {text}
        """

    def _recursive_summarize(self, content: str) -> str:
        """递归处理长文本"""
        while len(content) > Config.MAX_CHUNK_LENGTH:
            logger.info("Starting recursive summarization...")
            content = chunk_process(
                book_content=content,
                summary_template=self.summary_template,
                block_num=Config.BLOCK_NUM_REDUCE
            )
            logger.debug(f"Recursive iteration length: {len(content)}")
        return content

    def generate_introduction(self, summaries: str) -> Optional[str]:
        """生成引言部分 (prompt可优化)"""
        final_template = """以下是某长文本的分段总结，请将其整合为一个连贯的摘要，突出整体逻辑和结论。多个文本片段总结如下：
{summaries}
输出格式如下，不要分点输出，并全部使用英文输出：
Introduction
“正文内容......”
"""
        try:
            return ds_api(final_template.format(summaries=summaries), token_num=Config.DEFAULT_TOKEN_NUM)
        except Exception as e:
            logger.error(f"Introduction generation failed: {str(e)}")
            return None

    def generate_key_points(self, summaries: str) -> Optional[str]:
        """生成关键点 (prompt可优化)"""
        points_template = """根据我为你提供的资料，帮我生成5到7个关键点。多个文本摘要如下:
{summaries}
输出格式如下，不要分点输出，并全部使用英文输出：
关键点1的标题
“正文内容（至少三段）......”
关键点2的标题
“正文内容（至少三段）......”
......(至少5个关键点)
"""
        try:
            return ds_api(points_template.format(summaries=summaries), Config.DEFAULT_TOKEN_NUM)
        except Exception as e:
            logger.error(f"Key points generation failed: {str(e)}")
            return None

    def process_single_book(self, book_path: str, output_path: str) -> bool:
        """处理单本书籍"""
        try:
            # 读取书籍内容
            with open(book_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"Processing: {os.path.basename(book_path)} ({len(content)} chars)")

            # 初始分块处理
            summaries = chunk_process(content, self.summary_template)
            with open('temp_sum.txt', 'w', encoding='utf-8') as f:
                f.write(summaries)

            # summaries = self._recursive_summarize(summaries)
            # with open('temp_sum.txt', 'w', encoding='utf-8') as f:
            #     f.write(summaries)

            # 生成最终内容
            introduction = self.generate_introduction(summaries)
            key_points = self.generate_key_points(summaries)

            if introduction:
                final_content = f"{introduction}\n\n"
                save_content(final_content, output_path)

            if key_points:
                final_content = f"{key_points}\n\n"
                with open(output_path, 'a', encoding='utf-8') as f:
                    f.write(final_content)

            if introduction and key_points:
                return True
            return False



        except Exception as e:
            logger.error(f"Book processing failed: {str(e)}")
            return False
