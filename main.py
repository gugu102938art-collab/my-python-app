import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# 1. Setup Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("SnackOrders").sheet1 # Make sure the name matches exactly

# 2. Bot Configuration
TOKEN = "8215624443:AAHb3jSVaJjh5k7Pr3b74Zfdjm38XuUzm90
"

# Snack Data (Image URL, Name, Price)
SNACKS = {
    "chips": {"name": "Classic Chips", "price": "$2.50", "pic": "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=400"},
    "soda": {"name": "Cold Soda", "price": "$1.50", "pic": "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=400"}
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends the menu when /start is typed."""
    await update.message.reply_text("Welcome to the Snack Shop! Choose a snack below:")
    
    for key, item in SNACKS.items():
        keyboard = [[InlineKeyboardButton(f"Order {item['name']} - {item['price']}", callback_data=key)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_photo(
            photo=item['pic'],
            caption=f"Item: {item['name']}\nPrice: {item['price']}",
            reply_markup=reply_markup
        )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the order button click."""
    query = update.callback_query
    await query.answer()
    
    snack_key = query.data
    snack_name = SNACKS[snack_key]['name']
    snack_price = SNACKS[snack_key]['price']
    user = query.from_user.username or query.from_user.first_name

    try:
        # Append to Google Sheet
        sheet.append_row([str(query.message.date), user, snack_name, snack_price])
        await query.edit_message_caption(caption=f"✅ Order Confirmed!\n\nItem: {snack_name}\nStatus: Sent to Google Sheets")
    except Exception as e:
        await query.edit_message_caption(caption="❌ Error saving to Sheet. Check credentials.")

if __name__ == "__main__":
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_click))
    
    print("Bot is running...")
    application.run_polling()
