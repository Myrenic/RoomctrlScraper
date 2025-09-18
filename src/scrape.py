import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import asyncio
import aiohttp
import time
import os
import json
from html import escape

class RoomctrlScraper:

    def __init__(self, email: str, password: str, hostname: str, debug: bool = False):
        self.session = requests.Session()
        self.email = email
        self.password = password
        self.hostname = hostname
        self.cookies = None
        self.LOGIN_URL = f"https://{self.hostname}/NET/Identity/Account/Login"
        self.BASE_URL = f"https://{self.hostname}/Plot/Archive/"
        self.debug = debug
        self._login()

    def _debug(self, msg: str):
        if self.debug:
            print(msg)

    def _login(self):
        self._debug("[0.00s] Logging in...")
        start = time.perf_counter()
        resp = self.session.get(self.LOGIN_URL)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        token_tag = soup.find("input", {"name": "__RequestVerificationToken"})
        token = token_tag["value"] if token_tag else ""
        if not token:
            raise ValueError("Cannot find anti-CSRF token on login page.")

        payload = {
            "Input.Email": self.email,
            "Input.Password": self.password,
            "__RequestVerificationToken": token,
        }
        login_resp = self.session.post(self.LOGIN_URL, data=payload)
        login_resp.raise_for_status()
        if "Invalid login" in login_resp.text:
            raise ValueError("Login failed. Check your credentials.")
        self.cookies = self.session.cookies.get_dict()
        end = time.perf_counter()
        self._debug(f"[{end-start:.2f}s] Login successful!")

    def save_snapshot(self, data: list, filename: str = "snapshot.json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_snapshot(self, filename: str = "snapshot.json") -> list:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def compare_snapshots(self, old: list, new: list):
        # Use (name, date) as the identity key
        old_map = {(f["name"], f["date"]): f for f in old}
        new_map = {(f["name"], f["date"]): f for f in new}

        added_keys = set(new_map) - set(old_map)
        removed_keys = set(old_map) - set(new_map)

        # Files that are "new" or changed by name/date
        added = [new_map[k] for k in added_keys]
        removed = [old_map[k] for k in removed_keys]

        # Update URLs for unchanged files
        for k in set(new_map) & set(old_map):
            old_map[k]["url"] = new_map[k]["url"]

        if self.debug:
            if added:
                self._debug(f"New or updated files: {len(added)}")
                for f in added:
                    self._debug(f" + {f['name']} ({f['date']})")
            if removed:
                self._debug(f"Removed files: {len(removed)}")
                for f in removed:
                    self._debug(f" - {f['name']} ({f['date']})")
        return added, removed

    def get_category_urls(self) -> List[str]:
        start = time.perf_counter()
        self._debug(f"[{start:.2f}s] Fetching category URLs...")
        resp = self.session.get(self.BASE_URL + "default.asp")
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        links = soup.select("div.well ul.nav li a")
        urls = [self.BASE_URL + a["href"] for a in links if "href" in a.attrs]
        end = time.perf_counter()
        self._debug(f"[{end:.2f}s] Found {len(urls)} categories.")
        return urls

    async def scrape_files_from_category(
        self, session: aiohttp.ClientSession, url: str, start_time: float
    ) -> List[Dict[str, str]]:
        self._debug(f"[{time.perf_counter()-start_time:.2f}s] Starting fetch: {url}")
        async with session.get(url) as resp:
            text = await resp.text()
        soup = BeautifulSoup(text, "html.parser")
        container = soup.find("div", class_="col-md-9")
        table = container.find("table", class_="table") if container else None
        files = []
        if table:
            for row in table.find_all("tr")[1:]:
                cols = row.find_all("td")
                if len(cols) >= 5:
                    name_tag = cols[1].find("a")
                    link_tag = cols[4].find("a")
                    date = cols[3].text.strip() if len(cols) > 3 else ""
                    files.append(
                        {
                            "name": name_tag.text.strip() if name_tag else "",
                            "date": date,
                            "url": link_tag["href"] if link_tag else "",
                        }
                    )
        self._debug(
            f"[{time.perf_counter()-start_time:.2f}s] Finished {url} – {len(files)} files found"
        )
        return files

    async def scrape_all_async(self) -> List[Dict[str, str]]:
        start_time = time.perf_counter()
        category_urls = self.get_category_urls()
        all_files = []

        async with aiohttp.ClientSession(cookies=self.cookies) as session:
            tasks = [
                self.scrape_files_from_category(session, url, start_time)
                for url in category_urls
            ]
            for future in asyncio.as_completed(tasks):
                files = await future
                all_files.extend(files)

        end_time = time.perf_counter()
        self._debug(
            f"[{end_time-start_time:.2f}s] All categories done, total files: {len(all_files)}"
        )
        return all_files

def send_telegram_message(
    message: str, TELEGRAM_THREAD_ID: int = None, parse_mode: str = "HTML"
):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram token or chat ID not set, skipping message")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": parse_mode,
        "disable_web_page_preview": False,
    }
    if TELEGRAM_THREAD_ID is not None:
        payload["message_thread_id"] = TELEGRAM_THREAD_ID
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

def make_msg_html(f):
    name = escape(f["name"])
    url = escape(f["url"], quote=True)
    date = escape(f["date"])
    return f'➕ <a href="{url}">{name}</a> ({date})'

if __name__ == "__main__":
    email = os.environ.get("ROOMCTRL_EMAIL")
    password = os.environ.get("ROOMCTRL_PASSWORD")
    hostname = os.environ.get("ROOMCTRL_INSTANCE_ENDPOINT")
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
    TELEGRAM_THREAD_ID = os.environ.get("TELEGRAM_THREAD_ID")
    if not all([email, password, hostname]):
        raise ValueError(
            "Missing required environment variables: ROOMCTRL_EMAIL, ROOMCTRL_PASSWORD, ROOMCTRL_INSTANCE_ENDPOINT"
        )

    scraper = RoomctrlScraper(email=email, password=password, hostname=hostname)
    all_files = asyncio.run(scraper.scrape_all_async())

    previous_files = scraper.load_snapshot()
    if previous_files:
        added, removed = scraper.compare_snapshots(previous_files, all_files)
        if added:
            print(f"New or updated files: {len(added)}")
            for f in added:
                print(f" + {f['name']} ({f['date']})")
            send_telegram_message(
                f"🆕 Nieuwe of bijgewerkte bestanden vanuit {hostname}!: {len(added)}"
            )
            for f in added:
                send_telegram_message(make_msg_html(f), parse_mode="HTML")
    scraper.save_snapshot(all_files)
