import random


def load_user_agents(file_path="data/user_agents.txt"):
    """
    Kullanıcı ajanları listesini dosyadan yükler.

    Args:
        file_path (str): Kullanıcı ajanlarının bulunduğu dosya yolu.

    Returns:
        list: Kullanıcı ajanlarının bulunduğu liste.

    Raises:
        FileNotFoundError: Dosya bulunamazsa hata fırlatır.
    """
    try:
        with open(file_path, "r") as file:
            user_agents = [line.strip() for line in file.readlines() if line.strip()]
        if not user_agents:
            raise ValueError("Kullanıcı ajanları listesi boş.")
        return user_agents
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Kullanıcı ajanları dosyası bulunamadı: {e}")


def get_random_user_agent(user_agents):
    """
    Rastgele bir kullanıcı ajanı döner.

    Args:
        user_agents (list): Kullanıcı ajanlarının bulunduğu liste.

    Returns:
        str: Rastgele bir kullanıcı ajanı.

    Raises:
        ValueError: Kullanıcı ajanları listesi boşsa hata fırlatır.
    """
    if not user_agents:
        raise ValueError("Kullanıcı ajanları listesi boş.")
    return random.choice(user_agents)
