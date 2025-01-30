import requests
from typing import Dict, Any
import datetime

from .plugin import Plugin

class CryptoPlugin(Plugin):
    """
    A plugin to fetch the current rate, 7d change, community sentiment
    and latest news of a cryptocurrency from Coingecko.
    It first searches by the user's query, then gets detailed info.
    Finally, it returns a nicely formatted string with emojis.
    """

    def get_source_name(self) -> str:
        return "Coingecko (detailed)"

    def get_spec(self) -> [Dict]:
        return [{
            "name": "get_crypto_info",
            "description": (
                "Get detailed info about a cryptocurrency from Coingecko, including 7d price change, "
                "community sentiment (bullish %), some recent news, and a final opinion. "
                "Searches by name/symbol for flexibility."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "asset": {
                        "type": "string",
                        "description": (
                            "User query for the crypto asset (e.g. 'bitcoin', 'toncoin', 'baby doge')."
                            " Must be in a format recognized by Coingecko search."
                        )
                    }
                },
                "required": ["asset"],
            },
        }]

    async def execute(self, function_name, helper, **kwargs) -> Dict[str, Any]:
        """
        1) Поиск монеты по /search (чтобы находить и новые, малоизвестные монеты).
        2) Берём первый результат -> coin_id
        3) Делаем запрос /coins/{coin_id} с market_data=true, community_data=true, developer_data=true
                4) Извлекаем:
           - current_price (usd)
           - price_change_7d_percent
           - sentiment_votes_up_percentage (процент 'bullish')
           - status_updates (последние новости)
        5) Формируем ответ c эмодзи и возвращаем в поле "formatted_answer"
        """

        user_query = kwargs["asset"].strip()
        if not user_query:
            return {
                "error": "Empty asset query",
                "formatted_answer": "❓ Пожалуйста, введите название или символ монеты."
            }

        # --- Шаг 1: поиск по /search ---
        search_url = "https://api.coingecko.com/api/v3/search"
        try:
            search_resp = requests.get(search_url, params={"query": user_query}, timeout=10)
            search_data = search_resp.json()
        except Exception as e:
            return {
                "error": f"Failed to call Coingecko /search: {e}",
                "formatted_answer": "🚧 Произошла ошибка при запросе к Coingecko /search.",
            }

        coins_found = search_data.get("coins", [])
        if not coins_found:
            return {
                "error": f"No coin found for '{user_query}'",
                "formatted_answer": (
                    f"❌ Не нашёл монету по запросу '{user_query}'. "
                    "Попробуйте ввести официальное название или символ (на англ.), например: BTC, bitcoin."
                ),
            }

        first_coin = coins_found[0]
        coin_id = first_coin["id"]  # реальный ID на Coingecko (например, 'toncoin')

        # --- Шаг 2: детальный запрос /coins/{coin_id} ---
        details_url = (
            f"https://api.coingecko.com/api/v3/coins/{coin_id}"
            "?localization=false&tickers=false"
            "&market_data=true&community_data=true&developer_data=true"
            "&sparkline=false"
                    )
        try:
            resp = requests.get(details_url, timeout=10)
            coin_data = resp.json()
        except Exception as e:
            return {
                "error": f"Failed to fetch coin details for '{coin_id}': {e}",
                "formatted_answer": f"🚧 Ошибка запроса к /coins/{coin_id} : {e}",
            }

        # --- Извлекаем данные ---
        name = coin_data.get("name", "?")
        symbol = coin_data.get("symbol", "?").upper()
        market_data = coin_data.get("market_data", {})

        # Текущая цена (USD)
        current_price = market_data.get("current_price", {}).get("usd")
        # Изменение цены за 7 дней (в %)
        price_change_7d = None
        if market_data.get("price_change_percentage_7d_in_currency"):
            price_change_7d = market_data["price_change_percentage_7d_in_currency"].get("usd")

        # Процент bullish-настроений
        votes_up = coin_data.get("sentiment_votes_up_percentage", 0.0)
        bullish_percent = votes_up  # Округлим позже при выводе

        # Последние новости (status_updates)
        status_updates = coin_data.get("status_updates", [])
        # Возьмём, например, до 2 новостей
        news_list = []
        for update in status_updates[:2]:
            created_at = update.get("created_at")  # иногда ISO8601, иногда unix timestamp
            desc = update.get("description", "")
            # Сформируем короткую строку
            news_item = f"• {desc} (дата: {created_at})"
            news_list.append(news_item)

        # --- Формируем красивый текст с эмодзи ---
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        price_str = f"{current_price:.2f} $" if current_price is not None else "нет данных"
        change_7d_str = f"{price_change_7d:.2f}%" if price_change_7d is not None else "N/A"
        bullish_str = f"{bullish_percent:.2f}%"
        answer_lines = [
            f"🪙 *{name}* (символ: {symbol})",
            f"💰 Текущая цена: {price_str}",
            f"📈 Изменение за 7 дней: {change_7d_str}",
            f"👥 Примерно {bullish_str} сообщества считает, что монета будет расти",
            "",
        ]

        if news_list:
            answer_lines.append("📰 *Последние новости*:")
            for n in news_list:
                answer_lines.append(n)
        else:
            answer_lines.append("📰 Новостей не найдено на Coingecko.")

        answer_lines.append("")
        answer_lines.append("🤔 Мой совет: DYOR и удачи! 🚀")
        answer_lines.append(f"_Данные актуальны на {date_str}_")

        formatted_answer = "\n".join(answer_lines)

        return {
            "asset_searched": user_query,
            "coin_id": coin_id,
            "formatted_answer": formatted_answer,
            "name": name,
            "symbol": symbol,
            "current_price_usd": current_price,
            "price_change_7d_percent": price_change_7d,
            "bullish_percent": bullish_percent,
            "latest_news_count": len(news_list),
        }
