import os
from datetime import datetime
from typing import List, Dict, Any

from dotenv import load_dotenv
from supabase import create_client, Client
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing in .env")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Supabase config is missing in .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


async def split_and_send(context: ContextTypes.DEFAULT_TYPE, chat_id: int, text: str, chunk_limit: int = 3800):
    buf = ""
    chunks: List[str] = []
    for line in text.split("\n"):
        candidate = (buf + "\n" + line) if buf else line
        if len(candidate) > chunk_limit:
            if buf:
                chunks.append(buf)
            buf = line
        else:
            buf = candidate
    if buf:
        chunks.append(buf)
    for ch in chunks:
        await context.bot.sendMessage(chat_id=chat_id, text=ch)


def format_task(t: Dict[str, Any]) -> str:
    p = (t.get("priority") or "").upper()
    due_raw = t.get("due_date")
    try:
        due = datetime.fromisoformat(str(due_raw).replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M") if due_raw else "—"
    except Exception:
        due = str(due_raw) if due_raw else "—"
    status = "✅ Выполнено" if t.get("is_completed") else "🕒 В работе"
    desc = (t.get("description") or "").strip()
    if len(desc) > 500:
        desc = desc[:500] + "…"
    body = [
        f"• {t.get('title')}",
        f"{status} | Приоритет: {p} | Дедлайн: {due}",
    ]
    if desc:
        body.append("Описание: " + desc)
    return "\n".join(body)


def find_user_by_tg_username(tg_username: str) -> Dict[str, Any] | None:
    if not tg_username:
        return None
    name = (tg_username or "").strip()
    norm = name.lstrip('@').lower()
    candidates = list({
        name,
        name.lower(),
        '@' + norm,
        norm,
    })
    res = supabase.table("users").select("id, username, email, tg_username").in_("tg_username", candidates).limit(1).execute()
    data = res.data or []
    return data[0] if data else None


def get_accessible_boards(user_id: str) -> List[Dict[str, Any]]:
    boards_map: Dict[str, Dict[str, Any]] = {}

    created = supabase.table("boards").select("id, title").eq("creator_id", user_id).execute()
    for b in (created.data or []):
        boards_map[b["id"]] = b

    roles = supabase.table("user_roles").select("board_id").eq("user_id", user_id).execute()
    role_ids = list({r["board_id"] for r in (roles.data or []) if r.get("board_id")})
    if role_ids:
        role_boards = supabase.table("boards").select("id, title").in_("id", role_ids).execute()
        for b in (role_boards.data or []):
            boards_map[b["id"]] = b

    return list(boards_map.values())


def get_columns(board_id: str) -> List[Dict[str, Any]]:
    res = supabase.table("columns").select("id, title, position").eq("board_id", board_id).order("position", desc=False).execute()
    return res.data or []


def get_tasks(column_id: str) -> List[Dict[str, Any]]:
    res = supabase.table("tasks").select("id, title, description, priority, due_date, is_completed, position").eq("column_id", column_id).order("position", desc=False).execute()
    return res.data or []


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    tg_name = (update.effective_user.username or "").strip()

    if not tg_name:
        await context.bot.sendMessage(chat_id, "У вас не задан Telegram юзернейм. Задайте его в настройках Telegram, затем подключите бота через сайт в профиле.")
        return

    user = find_user_by_tg_username(tg_name)
    if not user:
        await context.bot.sendMessage(chat_id, "Вы не привязаны к боту. Зайдите на сайт, профиль, укажите свой Telegram юзернейм и нажмите \"Подключить\".")
        return

    boards = get_accessible_boards(user["id"])
    if not boards:
        await context.bot.sendMessage(chat_id, "Доски не найдены. Создайте доску на сайте или попросите добавить вас в участники.")
        return

    keyboard = [[InlineKeyboardButton(b["title"], callback_data=f"board:{b['id']}")] for b in boards]
    await context.bot.sendMessage(chat_id, "Выберите доску:", reply_markup=InlineKeyboardMarkup(keyboard))


async def cmd_boards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    tg_name = (update.effective_user.username or "").strip()
    user = find_user_by_tg_username(tg_name)
    if not user:
        await context.bot.sendMessage(chat_id, "Вы не привязаны к боту. Подключите через профиль на сайте.")
        return
    boards = get_accessible_boards(user["id"])
    if not boards:
        await context.bot.sendMessage(chat_id, "Доски не найдены.")
        return
    keyboard = [[InlineKeyboardButton(b["title"], callback_data=f"board:{b['id']}")] for b in boards]
    await context.bot.sendMessage(chat_id, "Выберите доску:", reply_markup=InlineKeyboardMarkup(keyboard))


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat.id
    tg_name = (query.from_user.username or "").strip()
    user = find_user_by_tg_username(tg_name)
    if not user:
        await context.bot.sendMessage(chat_id, "Подключите бота через сайт (профиль).")
        return

    data = query.data or ""
    if data.startswith("board:"):
        board_id = data.split(":", 1)[1]
        cols = get_columns(board_id)
        if not cols:
            await context.bot.sendMessage(chat_id, "В этой доске пока нет колонок.")
            return
        keyboard = [[InlineKeyboardButton(c["title"], callback_data=f"column:{c['id']}")] for c in cols]
        await context.bot.sendMessage(chat_id, "Выберите колонку:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("column:"):
        column_id = data.split(":", 1)[1]
        tasks = get_tasks(column_id)
        if not tasks:
            await context.bot.sendMessage(chat_id, "В этой колонке пока нет задач.")
            return
        text = "\n\n".join(format_task(t) for t in tasks)
        await split_and_send(context, chat_id, text)
        return


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("boards", cmd_boards))
    app.add_handler(CallbackQueryHandler(on_callback))
    print("[BOT] Python Telegram bot started. Listening for updates…")
    app.run_polling()


if __name__ == "__main__":
    main()