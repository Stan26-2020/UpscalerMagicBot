APP_URL = os.getenv("RENDER_URL")

async def main():
    await app.bot.set_webhook(url=APP_URL + f"/{TOKEN}")
    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 10000)),
        webhook_url=APP_URL + f"/{TOKEN}"
    )