# __init__.py
# Bu dosya, scraper modülünü bir Python paketi olarak tanımlar.
# İçe aktarma işlemlerini burada tanımlayabilirsiniz.

from .scraper import Scraper
from .config import load_config
from .main import main

config = load_config() 