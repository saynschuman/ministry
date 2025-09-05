import json
import os
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd

BASE_URL = "https://ministry.saynschuman.pp.ua/psalm/"

def load_json(filename="psalms.json"):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def parse_psalm(psalm_id, title):
    url = f"{BASE_URL}{psalm_id}"
    try:
        resp = requests.get(url, timeout=10)
    except requests.RequestException as e:
        print(f"Ошибка запроса {url}: {e}")
        return {"Название псалма": title, "Даты спевов": "-", "Даты служений": "-"}
    if resp.status_code != 200:
        print(f"Ошибка при запросе {url}: статус {resp.status_code}")
        return {"Название псалма": title, "Даты спевов": "-", "Даты служений": "-"}

    soup = BeautifulSoup(resp.text, "html.parser")

    # ⚠️ Нужно заменить на реальные селекторы
    spevky = [el.get_text(strip=True) for el in soup.select(".spevka-date")]
    sluzhinnya = [el.get_text(strip=True) for el in soup.select(".sluzhinnya-date")]

    return {
        "Название псалма": title,
        "Даты спевов": ", ".join(spevky) if spevky else "-",
        "Даты служений": ", ".join(sluzhinnya) if sluzhinnya else "-"
    }

def main():
    data = load_json()  # загружаем ваш JSON
    # Необязательное ограничение количества элементов для быстрого прогона
    limit_env = os.environ.get("PSALMS_LIMIT")
    try:
        limit = int(limit_env) if limit_env else None
    except ValueError:
        limit = None
    results = []

    items = data.get("results", [])
    if limit is not None:
        items = items[:limit]

    for item in items:
        psalm_id = item["id"]
        title = item["title"]
        try:
            results.append(parse_psalm(psalm_id, title))
        except Exception as e:
            print(f"Не удалось обработать {psalm_id} ({title}): {e}")
            results.append({
                "Название псалма": title,
                "Даты спевов": "-",
                "Даты служений": "-",
            })
        # маленькая пауза, чтобы не спамить сервер
        time.sleep(0.2)

    df = pd.DataFrame(results)

    # выводим в консоль
    print(df.to_string(index=False))

    # сохраняем в Excel
    df.to_excel("psalms_with_dates.xlsx", index=False)

if __name__ == "__main__":
    main()
