import os
from typing import List
from config.setting import Config
from utils.file_handlers import get_book_list, save_content
from utils.logger import configure_logger
from core.processor import BookProcessor

logger = configure_logger()


def main():
    processor = BookProcessor()

    try:
        # 获取书籍列表
        books: List[str] = get_book_list(Config.BOOK_DIR)
        if not books:
            logger.error("No books found to process")
            return

        # 处理所有书籍
        success_count = 0
        for idx, book_path in enumerate(books, 1):
            try:
                logger.info(f"Processing book {idx}/{len(books)}")
                output_name = f"{os.path.splitext(os.path.basename(book_path))[0]}.md"

                if processor.process_single_book(book_path, output_name):
                    success_count += 1

            except Exception as e:
                logger.error(f"Failed to process {book_path}: {str(e)}")
                continue

        logger.info(f"Process completed. Success: {success_count}/{len(books)}")

    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise


if __name__ == "__main__":
    main()