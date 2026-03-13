import os
import requests
from groq import Groq
from datetime import datetime
import pytz

# ── Config from environment variables ──────────────────────────────────────────
GROQ_API_KEY     = os.environ["GROQ_API_KEY"]
TELEGRAM_TOKEN   = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# ── Groq LLM call ───────────────────────────────────────────────────────────────
def generate_meal_plan() -> str:
    client = Groq(api_key=GROQ_API_KEY)

    ist = pytz.timezone("Asia/Kolkata")
    today = datetime.now(ist).strftime("%A, %d %B %Y")

    prompt = f"""You are a helpful Indian home chef assistant. Today is {today}.

Generate a complete meal plan for an Indian household for today.
The family enjoys BOTH North Indian and South Indian cuisine — mix them up.
They eat vegetarian, eggs, and non-vegetarian food.

Format your response EXACTLY like this (use emojis as shown):

🌅 *BREAKFAST*
• Dish name — one line description (e.g., key ingredients or style)

☀️ *LUNCH*
• Dish name — one line description
• Side dish / accompaniment — one line description

🌙 *DINNER*
• Dish name — one line description
• Side dish / accompaniment — one line description

💡 *Today's Kitchen Tip*
One practical Indian cooking tip relevant to today's meals.

Rules:
- Keep dish names authentic (use proper Indian names)
- Vary between North & South Indian dishes across meals
- Don't repeat dishes from a typical weekly plan
- Keep descriptions concise and appetizing
- Today suggest {"a non-veg option" if datetime.now(ist).weekday() in [4, 5, 6] else "a mix of veg and egg dishes"}
"""

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.85,
        max_tokens=600,
    )

    return response.choices[0].message.content.strip()


# ── Telegram sender ─────────────────────────────────────────────────────────────
def send_telegram(message: str):
    ist = pytz.timezone("Asia/Kolkata")
    today = datetime.now(ist).strftime("%A, %d %B %Y")

    full_message = (
        f"🍽️ *Daily Meal Plan — {today}*\n"
        f"{'─' * 30}\n\n"
        f"{message}\n\n"
        f"{'─' * 30}\n"
        f"_Bon appétit! Enjoy your meals today_ 🙏"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": full_message,
        "parse_mode": "Markdown",
    }

    response = requests.post(url, json=payload, timeout=15)
    response.raise_for_status()
    print(f"✅ Meal plan sent successfully! Status: {response.status_code}")


# ── Main ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🍳 Generating today's Indian meal plan...")
    meal_plan = generate_meal_plan()
    print("📤 Sending to Telegram...")
    send_telegram(meal_plan)
