# config.py

BASE_URL = "https://dsebd.org"


# Dhaka Stock Exchange URLs
DHAKA_STOCK_URLS = {
    "LATEST_DATA": f"{BASE_URL}/latest_share_price_scroll_l.php",
    "DSEX": f"{BASE_URL}/dseX_share.php",
    "TOP_30": f"{BASE_URL}/dse30_share.php",
    "HISTORICAL_DATA": f"{BASE_URL}/day_end_archive.php"
}

# Request Configuration
REQUEST_CONFIG = {
    "TIMEOUT": 30,
    "MAX_RETRIES": 3,
    "BACKOFF_FACTOR": 2,
    "MAX_CONNECTIONS": 10,
    "MAX_CONNECTIONS_PER_HOST": 5
}