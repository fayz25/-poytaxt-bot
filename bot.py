import os
import json
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN", "8641120442:AAEj8KZiRsHAmFZA0e_Ftt6s1iBbIix4U9A")
ADMIN_ID = os.environ.get("ADMIN_ID", "1835095856")
WEB_APP_URL = "https://harmonious-fenglisu-90f676.netlify.app"
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users = load_users()
    
    uid = str(user.id)
    now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
    is_new = uid not in users

    if uid not in users:
        users[uid] = {
            "id": user.id,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "username": user.username or "",
            "first_seen": now,
            "last_seen": now,
            "visits": 1
        }
    else:
        users[uid]["last_seen"] = now
        users[uid]["visits"] += 1

    save_users(users)

    # Уведомить администратора
    if ADMIN_ID:
        try:
            name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            username = f"@{user.username}" if user.username else "нет username"
            status = "🆕 НОВЫЙ пользователь" if is_new else f"↩️ Вернулся (визит #{users[uid]['visits']})"
            msg = (
                f"{status}\n"
                f"👤 {name}\n"
                f"🔗 {username}\n"
                f"🆔 ID: {user.id}\n"
                f"🕐 {now}"
            )
            await context.bot.send_message(chat_id=int(ADMIN_ID), text=msg)
        except Exception as e:
            print(f"Admin notify error: {e}")

    # Кнопка Web App
    keyboard = [[
        InlineKeyboardButton(
            "📋 Открыть регламенты",
            web_app=WebAppInfo(url=WEB_APP_URL)
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    name = user.first_name or "Коллега"
    await update.message.reply_text(
        f"Салом, {name}! 👋\n\n"
        f"📋 *База регламентов POYTAXT GROUP*\n\n"
        f"Здесь собраны все актуальные правила, инструкции и штрафы производственного цеха.\n\n"
        f"🔑 Пароль для входа: `My-Drop-Site`\n\n"
        f"Нажмите кнопку ниже 👇",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if ADMIN_ID and str(user.id) != str(ADMIN_ID):
        await update.message.reply_text("⛔ Нет доступа.")
        return

    users = load_users()
    total = len(users)
    
    if total == 0:
        await update.message.reply_text("Пока никто не заходил.")
        return

    text = f"📊 *Статистика бота*\n\n👥 Всего пользователей: *{total}*\n\n"
    
    # Последние 20 пользователей
    sorted_users = sorted(users.values(), key=lambda x: x.get("last_seen",""), reverse=True)
    text += "*Последние визиты:*\n"
    for u in sorted_users[:20]:
        name = f"{u.get('first_name','')} {u.get('last_name','')}".strip() or "Без имени"
        username = f"@{u['username']}" if u.get('username') else "нет"
        visits = u.get('visits', 1)
        last = u.get('last_seen','?')
        text += f"\n👤 {name} ({username})\n🕐 {last} | визитов: {visits}\n"

    await update.message.reply_text(text, parse_mode="Markdown")

async def users_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if ADMIN_ID and str(user.id) != str(ADMIN_ID):
        await update.message.reply_text("⛔ Нет доступа.")
        return

    users = load_users()
    total = len(users)
    text = f"👥 *Все пользователи ({total}):*\n\n"
    
    for u in users.values():
        name = f"{u.get('first_name','')} {u.get('last_name','')}".strip() or "Без имени"
        username = f"@{u['username']}" if u.get('username') else "нет username"
        first = u.get('first_seen','?')
        visits = u.get('visits',1)
        text += f"• {name} | {username} | первый вход: {first} | визитов: {visits}\n"

    if len(text) > 4000:
        text = text[:4000] + "\n..."

    await update.message.reply_text(text, parse_mode="Markdown")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("users", users_list))
    print("Bot started...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
