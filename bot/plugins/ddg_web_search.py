import os
import re
import requests
from itertools import islice
from typing import Dict, Any, List, Union

from duckduckgo_search import DDGS
from bs4 import BeautifulSoup

from .plugin import Plugin

# ------------------- Константы настройки -------------------
MAX_RESULTS = 8            # Берём ограниченное кол-во ссылок из DDG
MAX_PAGE_CHARS = 2000     # Сколько максимум символов берём из страницы
CHUNK_SIZE = 2000          # Размер «чанка» при дроблении текста
MAX_SUMMARY_PER_PAGE = 3000  # Максимальная длина сводки по одной странице
# -----------------------------------------------------------

def detect_region_auto(query: str) -> str:
    """
    Если в запросе есть кириллица, используем 'ru-ru', иначе 'us-en'.
    """
    if re.search('[а-яА-ЯёЁ]', query):
        return 'ru-ru'
    return 'us-en'

def detect_timelimit(query: str) -> Union[str, None]:
    """
    Простейшая логика «свежих» ссылок:
    - 'последний', 'неделя', 'week' => timelimit='w'
    - 'месяц', 'month' => timelimit='m'
    Иначе None.
    """
    q_lower = query.lower()
    if any(word in q_lower for word in ["последний", "последние", "неделя", "week", "recent"]):
        return 'w'
    if any(word in q_lower for word in ["месяц", "month"]):
        return 'm'
    return None

def fetch_page_text(url: str) -> str:
    """
    Скачиваем HTML (с timeout=10) и берём текст <body>, обрезаем до MAX_PAGE_CHARS.
    Возвращаем чистый текст.
    """
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
    except requests.RequestException:
        return ""

    soup = BeautifulSoup(resp.text, "html.parser")
    if not soup.body:
        return ""

    text = soup.body.get_text(separator=' ').strip()
    if len(text) > MAX_PAGE_CHARS:
        text = text[:MAX_PAGE_CHARS] + "..."
    return text

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> List[str]:
    """
    Дробим текст на чанки по chunk_size символов.
    """
    chunks = []
    start = 0
    length = len(text)
    while start < length:
        end = min(start + chunk_size, length)
        chunk = text[start:end]
        chunks.append(chunk)
        start = end
    return chunks

def naive_chunk_summarize(chunk: str, max_sentences: int = 10, max_chars: int = 1200) -> str:
    """
    Наивная суммаризация чанка:
    - Разделяем по точкам -> берём первые max_sentences предложений
    - Обрезаем до max_chars символов
    """
    chunk = chunk.strip()
    sentences = chunk.split('.')
    selected = sentences[:max_sentences]
    short_text = '.'.join(s.strip() for s in selected).strip()
    if not short_text.endswith('.'):
        short_text += '.'
    if len(short_text) > max_chars:
        short_text = short_text[:max_chars] + "..."
    return short_text

def summarize_whole_page(full_text: str) -> str:
    """
    1) Дробим текст страницы на чанки
    2) Суммируем каждый чанк
    3) Склеиваем частичные суммаризации
    4) Если итог > MAX_SUMMARY_PER_PAGE, обрезаем
    """
    if not full_text.strip():
        return "(На странице нет текста или она не загрузилась)"

    chunks = chunk_text(full_text, CHUNK_SIZE)
    partials = []
    for c in chunks:
        partial = naive_chunk_summarize(c)
        partials.append(partial)

    combined = "\n\n".join(partials)
    if len(combined) > MAX_SUMMARY_PER_PAGE:
        combined = combined[:MAX_SUMMARY_PER_PAGE] + "..."
    return combined

class DDGWebSearchPlugin(Plugin):
    """
    Плагин, который:
    1) Делает DuckDuckGo поиск (до 3 ссылок)
    2) Скачивает каждую ссылку, парсит <body>, режет на чанки, суммирует
    3) Возвращает подробную сводку (и форматированный список ссылок)
    """

    def __init__(self):
        self.safesearch = os.getenv('DUCKDUCKGO_SAFESEARCH', 'moderate')

    def get_source_name(self) -> str:
        return "DuckDuckGo-Thorough"

    def get_spec(self) -> List[Dict[str, Any]]:
        return [{
            "name": "web_search",
            "description": (
                "Perform a DuckDuckGo web search for the given query, then "
                "fetch the pages and provide a thorough summary of each."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "User query (keywords, question, etc.)."
                    }
                },
                "required": ["query"],
            },
        }]

    async def execute(self, function_name, helper, **kwargs) -> Dict[str, Union[str, List[Dict[str, str]]]]:
        query = kwargs.get("query", "").strip()
        if not query:
            return {
                "Result": [],
                "formatted_answer": "❓ Не задан поисковый запрос."
            }

        region = detect_region_auto(query)
        timelimit = detect_timelimit(query)

        # Шаг 1: Поиск через duckduckgo_search
        try:
            with DDGS() as ddgs:
                ddgs_gen = ddgs.text(
                    keywords=query,
                    region=region,
                    safesearch=self.safesearch,
                    timelimit=timelimit
                )
                raw_results = list(islice(ddgs_gen, MAX_RESULTS))  # берём до 3 ссылок
        except requests.RequestException as e:
            return {
                "Result": [],
                "formatted_answer": f"Ошибка сети или DuckDuckGo: {e}"
            }
        except Exception as e:
            return {
                "Result": [],
                "formatted_answer": f"Ошибка во время поиска: {e}"
            }

        if not raw_results:
            return {
                "Result": [],
                "formatted_answer": f"По запросу '{query}' ничего не найдено."
            }

        # Удаляем дубли по ссылке
        seen_links = set()
        final_links = []
        for r in raw_results:
            link = r.get("href")
            if link and link not in seen_links:
                seen_links.add(link)
                final_links.append(r)

        # Шаг 2: Скачиваем и суммируем
        final_data = []
        for item in final_links:
            title = item.get("title", "No Title")
            url = item.get("href", "")

            page_text = fetch_page_text(url)
            summary = summarize_whole_page(page_text)

            final_data.append({
                "title": title,
                "link": url,
                "summary": summary
            })

        # Формируем Markdown
        lines = []
        for i, fd in enumerate(final_data, start=1):
            t = fd["title"] or "No Title"
            l = fd["link"]
            lines.append(f"{i}. [{t}]({l})")

        date_info = " (фильтр по свежим результатам)" if timelimit else ""
        formatted_answer = (
            f"**Результаты поиска (подробно) для**: {query}{date_info}\n\n" +
            "\n".join(lines)
        )

        return {
            "Result": final_data,
            "formatted_answer": formatted_answer
        }
