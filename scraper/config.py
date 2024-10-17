class Config:
    URL = "https://www.teknosa.com/akilli-saat-c-100004001"
    HEADLESS = True
    PROXIES = [
        "http://113.160.218.14:8888",
        "http://133.18.234.13:80",
        "http://102.130.125.86:80",
        # Daha fazla proxy buraya eklenebilir
    ]
    USER_AGENTS_FILE = "data/user_agents.txt"
    PROXIES_FILE = "data/proxies.txt"