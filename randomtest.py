import random
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials

# =========================
# CONFIG
# =========================
SERVICE_ACCOUNT_FILE = "service_account.json"
SPREADSHEET_ID = "1uml8_D_bCd1eZoGVA1Xqs5y_JzrqMl3utu2g-jhvQZw"

TEST_MODE = True   # ✅ Set to False for normal random mode

MAX_COUNTRIES_PER_RUN = 12
MAX_NUMBERS_PER_COUNTRY = 6
MAX_MESSAGES_PER_NUMBER = 1

# =========================
# SERVICES
# =========================
services = [
    "Google", "WhatsApp", "Telegram", "Facebook", "Instagram",
    "Twitter", "Amazon", "Netflix", "Discord", "Microsoft",
    "Apple", "Binance", "PayPal", "Snapchat", "TikTok",
    "Uber", "Airbnb"
]

# =========================
# GOOGLE SHEETS CONNECT
# =========================
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=scopes
)

client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID)

numbers_ws = sheet.worksheet("numbers")
messages_ws = sheet.worksheet("messages")

# =========================
# COMMON FUNCTIONS
# =========================
def random_code(service):
    if service == "Google":
        return f"G-{random.randint(100000, 999999)}"
    return str(random.randint(100000, 999999))

def random_time():
    return (
        datetime.now() - timedelta(minutes=random.randint(1, 180))
    ).strftime("%Y-%m-%d %H:%M:%S")

messages_to_insert = []

# =========================
# TEST MODE
# =========================
if TEST_MODE:
    TEST_NUMBER = "1 555 123 4567"

    service = random.choice(services)
    code = random_code(service)

    messages_to_insert.append([
        TEST_NUMBER,
        service,
        code,
        f"Your {service} verification code is {code}",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "active"
    ])

    print("🧪 Running in TEST MODE")

# =========================
# NORMAL RANDOM MODE
# =========================
else:
    rows = numbers_ws.get_all_records()
    active_numbers = {}

    for row in rows:
        if row.get("status") != "active":
            continue

        country = row.get("country")
        number = row.get("number")

        if not country or not number:
            continue

        active_numbers.setdefault(country, []).append(number)

    selected_countries = random.sample(
        list(active_numbers.keys()),
        min(MAX_COUNTRIES_PER_RUN, len(active_numbers))
    )

    for country in selected_countries:
        numbers = active_numbers[country]

        selected_numbers = random.sample(
            numbers,
            min(MAX_NUMBERS_PER_COUNTRY, len(numbers))
        )

        for number in selected_numbers:
            for _ in range(random.randint(1, MAX_MESSAGES_PER_NUMBER)):
                service = random.choice(services)
                code = random_code(service)

                messages_to_insert.append([
                    number,
                    service,
                    code,
                    f"Your {service} verification code is {code}",
                    random_time(),
                    "active"
                ])

    print("🚀 Running in NORMAL RANDOM MODE")

# =========================
# APPEND TO SHEET
# =========================
if messages_to_insert:
    messages_ws.append_rows(messages_to_insert, value_input_option="RAW")
    print(f"✅ {len(messages_to_insert)} SMS message(s) generated")
else:
    print("⚠️ No messages generated")