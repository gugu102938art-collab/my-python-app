import logging
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# -------------------- LOGGING --------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# -------------------- ENV VARIABLES --------------------
TOKEN = os.getenv("8215624443:AAHb3jSVaJjh5k7Pr3b74Zfdjm38XuUzm90")

if not TOKEN:
    raise ValueError("❌ TOKEN not found. Set it in Railway Variables.")

# -------------------- GOOGLE SHEETS SETUP --------------------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

try:
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("SnackOrders").sheet1
except Exception as e:
    print("❌ Google Sheets setup failed:", e)
    sheet = None

# -------------------- SNACK DATA --------------------
SNACKS = {
    "chips": {
        "name": "Classic Chips",
        "price": "$2.50",
        "pic": "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=400"
    },
    "soda": {
        "name": "Cold Soda",
        "price": "$1.50",
        "pic": "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=400"
    }
}

# -------------------- COMMAND: /start --------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🍿 Welcome to the Snack Shop!\nChoose a snack below:")

    for key, item in SNACKS.items():
        keyboard = [[
            InlineKeyboardButton(
                f"Order {item['name']} - {item['price']}",
                callback_data=key
            )
        ]]

        await update.message.reply_photo(
            photo=item['pic'],
            caption=f"Item: {item['name']}\nPrice: {item['price']}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# -------------------- BUTTON CLICK --------------------
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    snack_key = query.data
    snack = SNACKS.get(snack_key)

    if not snack:
        await query.edit_message_caption(caption="❌ Invalid item.")
        return

    user = query.from_user.username or query.from_user.first_name

    try:
        if sheet:
            sheet.append_row([
                str(query.message.date),
                user,
                snack["name"],
                snack["price"]
            ])
            status = "✅ Saved to Google Sheets"
        else:
            status = "⚠️ Sheet not connected"

        await query.edit_message_caption(
            caption=f"✅ Order Confirmed!\n\nItem: {snack['name']}\n{status}"
        )

    except Exception as e:
        print("❌ Error saving:", e)
        await query.edit_message_caption(
            caption="❌ Error saving order. Check setup."
        )

# -------------------- MAIN --------------------
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))

    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
