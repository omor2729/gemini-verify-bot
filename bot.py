import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from main import GeminiVerifier  # এটি আপনার main.py থেকে কাজ ধার করবে

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 স্বাগতম! আপনার Google One Student ভেরিফিকেশন লিঙ্কটি এখানে পেস্ট করুন।")

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if "sheerid.com" not in url:
        await update.message.reply_text("❌ এটি সঠিক লিঙ্ক নয়। লিঙ্কে অবশ্যই sheerid.com থাকতে হবে।")
        return

    status_msg = await update.message.reply_text("⏳ কাজ শুরু হচ্ছে... (এটি ১-২ মিনিট সময় নিতে পারে)")
    
    try:
        # ভেরিফিকেশন অবজেক্ট তৈরি
        verifier = GeminiVerifier(url)
        
        # লিঙ্ক চেক করা
        check = verifier.check_link()
        if not check.get("valid"):
            await status_msg.edit_text(f"❌ এরর: {check.get('error')}")
            return
        
        # ভেরিফিকেশন শুরু
        result = verifier.verify()
        
        if result.get("success"):
            response = (
                f"✅ **ভেরিফিকেশন সফলভাবে সাবমিট হয়েছে!**\n\n"
                f"👤 নাম: {result.get('student')}\n"
                f"📧 ইমেইল: {result.get('email')}\n"
                f"🏫 ইউনিভার্সিটি: {result.get('school')}\n\n"
                f"📢 সাধারণত ২৪-৪৮ ঘণ্টার মধ্যে গুগল থেকে কনফার্মেশন মেইল পাবেন।"
            )
        else:
            response = f"❌ ব্যর্থ হয়েছে: {result.get('error')}"
            
        await status_msg.edit_text(response, parse_mode='Markdown')
        
    except Exception as e:
        await status_msg.edit_text(f"⚠️ সার্ভার এরর: {str(e)}")

if __name__ == '__main__':
    # Koyeb-এর Environment Variable থেকে টোকেন নিবে
    TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_url))
    
    print("Bot is running...")
    app.run_polling()
  
