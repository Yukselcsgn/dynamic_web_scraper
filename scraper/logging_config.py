import logging

def setup_logging():
    logging.basicConfig(
        filename='scraper.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
