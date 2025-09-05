import json
import requests
from bs4 import BeautifulSoup
import pandas as pd

BASE_URL = "https://ministry.saynschuman.pp.ua/psalm/"

def load_json(filename="psalms.json"):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def parse_psalm(psalm_id, title):
    url = f"{BASE_URL}{psalm_id}"
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f"Ошибка при запросе {url}")
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
    results = []

    for item in data["results"]:
        psalm_id = item["id"]
        title = item["title"]
        results.append(parse_psalm(psalm_id, title))

    df = pd.DataFrame(results)

    # выводим в консоль
    print(df.to_string(index=False))

    # сохраняем в Excel
    df.to_excel("psalms_with_dates.xlsx", index=False)

if __name__ == "__main__":
    main()
