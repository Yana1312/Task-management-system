import os
from datetime import datetime, timezone
import asyncio
import httpx
from typing import List, Dict, Any

from dotenv import load_dotenv
from supabase import create_client, Client
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    BotCommand,
    MenuButtonCommands,
)
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not BOT_TOKEN:
    raise RuntimeError("В .env отсутствует BOT_TOKEN")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("В .env отсутствует конфигурация Supabase (SUPABASE_URL/SUPABASE_KEY)")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


async def post_init(app):
    commands = [
        BotCommand("start", "Запуск бота и помощь"),
        BotCommand("profile", "Показать профиль"),
        BotCommand("boards", "Список доступных досок"),
    ]
    await app.bot.set_my_commands(commands)
    try:
        await app.bot.set_chat_menu_button(menu_button=MenuButtonCommands())
    except Exception:
        pass


def default_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[KeyboardButton("Профиль"), KeyboardButton("Доски")]],
        resize_keyboard=True,
        one_time_keyboard=False,
    )


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
        await context.bot.sendMessage(chat_id=chat_id, text=ch, parse_mode=ParseMode.MARKDOWN_V2)


MDV2_ESCAPE_CHARS = "_*[]()~`>#+-=|{}.!"


def escape_md(text: Any) -> str:
    s = str(text or "")
    out = []
    for c in s:
        if c in MDV2_ESCAPE_CHARS:
            out.append("\\" + c)
        else:
            out.append(c)
    return "".join(out)


def first_upper(s: str) -> str:
    s = str(s or "")
    if not s:
        return s
    return s[0].upper() + s[1:]


def chunk_text(text: str, chunk_limit: int = 3800) -> List[str]:
    buf = ""
    chunks: List[str] = []
    for line in str(text).split("\n"):
        candidate = (buf + "\n" + line) if buf else line
        if len(candidate) > chunk_limit:
            if buf:
                chunks.append(buf)
            buf = line
        else:
            buf = candidate
    if buf:
        chunks.append(buf)
    return chunks


async def send_chunks(context: ContextTypes.DEFAULT_TYPE, chat_id: int, chunks: List[str]) -> List[int]:
    ids: List[int] = []
    for ch in chunks:
        msg = await context.bot.sendMessage(chat_id=chat_id, text=ch, parse_mode=ParseMode.MARKDOWN_V2)
        try:
            ids.append(msg.message_id)
        except Exception:
            pass
    return ids


async def delete_messages_safe(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_ids: List[int]):
    for mid in message_ids or []:
        try:
            await context.bot.deleteMessage(chat_id=chat_id, message_id=mid)
        except Exception:
            pass


def format_task(t: Dict[str, Any]) -> str:
    p = (t.get("priority") or "").upper()
    due_raw = t.get("due_date")
    try:
        due = datetime.fromisoformat(str(due_raw).replace("Z", "+00:00")).strftime("%Y-%m-%d") if due_raw else "—"
    except Exception:
        due = str(due_raw) if due_raw else "—"
    status = "✅ Выполнено" if t.get("is_completed") else "🕒 В работе"
    desc = (t.get("description") or "").strip()
    if len(desc) > 500:
        desc = desc[:500] + "…"
    title = escape_md(t.get("title") or "Без названия")
    p_md = escape_md(p) if p else "—"
    due_md = escape_md(due)
    body = [
        f"📌 *{title}*",
        f"{status}  • _Приоритет:_ {p_md}  • _Дедлайн:_ {due_md}",
    ]
    if desc:
        body.append("📝 _Описание:_ " + escape_md(desc))
    return "\n".join(body)


def build_profile_text(info: Dict[str, Any], tg_name: str) -> str:
    created_at = info.get("created_at")
    try:
        created_fmt = datetime.fromisoformat(str(created_at).replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M") if created_at else "—"
    except Exception:
        created_fmt = str(created_at) if created_at else "—"

    text = (
        "👤 *Ваш профиль*\n"
        f"• _Имя:_ {escape_md(info.get('username') or '—')}\n"
        f"• _Email:_ {escape_md(info.get('email') or '—')}\n"
        f"• _Telegram:_ @{escape_md(info.get('tg_username') or tg_name)}\n"
        f"• _Дата регистрации:_ {escape_md(created_fmt)}\n"
    )
    return text


def get_user_stats(user_id: str) -> Dict[str, Any]:
    try:
        boards = get_accessible_boards(user_id)
        board_ids = [b.get("id") for b in boards if b.get("id")]
        columns_res = supabase.table("columns").select("id, board_id").in_("board_id", board_ids or ["_none_"]).execute()
        columns = columns_res.data or []
        column_ids = [c.get("id") for c in columns if c.get("id")]
        tasks_res = supabase.table("tasks").select("id, title, is_completed, priority, due_date, assignee_id, creator_id, created_at, updated_at").in_("column_id", column_ids or ["_none_"]).execute()
        tasks = tasks_res.data or []
    except httpx.ReadTimeout:
        return {"error": "timeout"}
    except Exception as e:
        return {"error": str(e)}

    total_tasks = len(tasks)
    assigned = [t for t in tasks if t.get("assignee_id") == user_id]
    created = [t for t in tasks if t.get("creator_id") == user_id]
    done_assigned = [t for t in assigned if t.get("is_completed")]
    progress_assigned = [t for t in assigned if not t.get("is_completed")]

    pr_counts: Dict[str, int] = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "URGENT": 0}
    for t in assigned:
        pr = str(t.get("priority") or "").upper()
        if pr in pr_counts:
            pr_counts[pr] += 1
        else:
            pr_counts[pr] = pr_counts.get(pr, 0) + 1

    def parse_iso(dt: Any):
        if not dt:
            return None
        try:
            s = str(dt)
            d = datetime.fromisoformat(s.replace("Z", "+00:00"))
            if d.tzinfo is None:
                d = d.replace(tzinfo=timezone.utc)
            return d.astimezone(timezone.utc)
        except Exception:
            return None

    now = datetime.now(timezone.utc)
    upcoming = []
    overdue_count = 0
    no_due_count = 0
    for t in progress_assigned:
        due = parse_iso(t.get("due_date"))
        if not due:
            no_due_count += 1
            continue
        if due < now:
            overdue_count += 1
        else:
            upcoming.append({"title": t.get("title"), "due": due})
    upcoming.sort(key=lambda x: x["due"])
    upcoming_top = upcoming[:3]

    ages = []
    for t in progress_assigned:
        c = parse_iso(t.get("created_at"))
        if c:
            ages.append((now - c).total_seconds() / 86400.0)
    avg_age_days = round(sum(ages) / len(ages), 1) if ages else 0.0

    return {
        "boards_count": len(board_ids),
        "columns_count": len(column_ids),
        "total_tasks": total_tasks,
        "assigned_count": len(assigned),
        "created_count": len(created),
        "done_assigned": len(done_assigned),
        "progress_assigned": len(progress_assigned),
        "priority": pr_counts,
        "overdue_count": overdue_count,
        "no_due_count": no_due_count,
        "upcoming_top": upcoming_top,
        "avg_age_days": avg_age_days,
    }


def format_stats_text(stats: Dict[str, Any]) -> str:
    text = (
        "📊 *Ваша статистика*\n"
        f"• _Досок доступно:_ {stats.get('boards_count', 0)}\n"
        f"• _Колонок доступно:_ {stats.get('columns_count', 0)}\n"
        f"• _Всего задач:_ {stats.get('total_tasks', 0)}\n"
        f"• _Назначено вам:_ {stats.get('assigned_count', 0)}\n"
        f"• _Создано вами:_ {stats.get('created_count', 0)}\n"
        f"• _В работе:_ {stats.get('progress_assigned', 0)}\n"
    )
    return text


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
    try:
        res = supabase.table("users").select("id, username, email, tg_username").in_("tg_username", candidates).limit(1).execute()
        data = res.data or []
    except Exception:
        data = []
    return data[0] if data else None


def get_accessible_boards(user_id: str) -> List[Dict[str, Any]]:
    boards_map: Dict[str, Dict[str, Any]] = {}
    try:
        created = supabase.table("boards").select("id, title").eq("creator_id", user_id).execute()
        for b in (created.data or []):
            boards_map[b["id"]] = b

        roles = supabase.table("user_roles").select("board_id").eq("user_id", user_id).execute()
        role_ids = list({r["board_id"] for r in (roles.data or []) if r.get("board_id")})
        if role_ids:
            role_boards = supabase.table("boards").select("id, title").in_("id", role_ids).execute()
            for b in (role_boards.data or []):
                boards_map[b["id"]] = b
    except Exception:
        return []

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

    intro = (
        "👋 *Добро пожаловать*\n\n"
        "*Что умеет бот*\n"
        "— Показывает доступные вам доски\n"
        "— Открывает колонки выбранной доски\n"
        "— Показывает задачи: статус, приоритет, дедлайн, описание\n\n"
        "*Навигация*\n"
        "— Кнопка «Доски» — список ваших досок\n"
        "— После выбора доски — нажмите на нужную колонку\n"
        "— Кнопка «Профиль» — данные вашего аккаунта\n"
        "— Меню слева — команды: /start /profile /boards\n"
    )
    await context.bot.sendMessage(chat_id, intro, reply_markup=default_keyboard(), parse_mode=ParseMode.MARKDOWN_V2)


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
    await context.bot.sendMessage(chat_id, "*Выберите доску:*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN_V2)


async def cmd_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    tg_name = (update.effective_user.username or "").strip()
    if not tg_name:
        await context.bot.sendMessage(chat_id, "У вас не задан Telegram юзернейм. Задайте его в настройках Telegram.")
        return
    user = find_user_by_tg_username(tg_name)
    if not user:
        await context.bot.sendMessage(chat_id, "Вы не привязаны к боту. Подключите через профиль на сайте.")
        return
    res = supabase.table("users").select("id, created_at, username, email, avatar_url, tg_username").eq("id", user["id"]).limit(1).execute()
    info = (res.data or [user])[0]
    text = build_profile_text(info, tg_name)
    ikb = InlineKeyboardMarkup([[InlineKeyboardButton("📊 Статистика", callback_data="user_stats")]])
    await context.bot.sendMessage(chat_id, text, reply_markup=ikb, parse_mode=ParseMode.MARKDOWN_V2)


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
        prev_prompt_id = context.user_data.get("last_columns_prompt_id")
        if prev_prompt_id:
            try:
                await delete_messages_safe(context, chat_id, [prev_prompt_id])
            except Exception:
                pass

        cols = get_columns(board_id)
        if not cols:
            msg = await context.bot.sendMessage(chat_id, "В этой доске пока нет колонок.")
            try:
                context.user_data["last_columns_prompt_id"] = msg.message_id
            except Exception:
                pass
            return
        keyboard = [[InlineKeyboardButton(first_upper(c.get("title") or ""), callback_data=f"column:{c['id']}")] for c in cols]
        msg = await context.bot.sendMessage(chat_id, "Выберите колонку:", reply_markup=InlineKeyboardMarkup(keyboard))
        try:
            context.user_data["last_columns_prompt_id"] = msg.message_id
        except Exception:
            pass
        return

    if data.startswith("column:"):
        column_id = data.split(":", 1)[1]
        tasks = get_tasks(column_id)
        if tasks:
            text = "\n\n".join(format_task(t) for t in tasks)
        else:
            text = escape_md("В этой колонке пока нет задач.")

        chunks = chunk_text(text)

        prev_ids = (context.user_data.get("last_tasks_message_ids") or [])

        if prev_ids and len(prev_ids) == 1 and len(chunks) == 1:
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=prev_ids[0],
                    text=chunks[0],
                    parse_mode=ParseMode.MARKDOWN_V2,
                )
                context.user_data["last_tasks_message_ids"] = prev_ids
                return
            except Exception:
                await delete_messages_safe(context, chat_id, prev_ids)
                new_ids = await send_chunks(context, chat_id, chunks)
                context.user_data["last_tasks_message_ids"] = new_ids
                return
        else:
            await delete_messages_safe(context, chat_id, prev_ids)
            new_ids = await send_chunks(context, chat_id, chunks)
            context.user_data["last_tasks_message_ids"] = new_ids
        return

    if data == "user_stats":
        if context.user_data.get("busy_stats"):
            await context.bot.sendMessage(chat_id, "Пожалуйста, подождите — идёт загрузка статистики…")
            return
        context.user_data["busy_stats"] = True
        try:
            stats = await asyncio.to_thread(get_user_stats, user["id"])
            if isinstance(stats, dict) and stats.get("error"):
                msg = "Сервис данных недоступен (таймаут). Попробуйте позже." if stats["error"] == "timeout" else "Не удалось получить статистику. Попробуйте позже."
                back_kb = InlineKeyboardMarkup([[InlineKeyboardButton("↩️ Назад к профилю", callback_data="back_profile")]])
                await context.bot.sendMessage(chat_id, msg, reply_markup=back_kb)
                return
            stats_text = format_stats_text(stats)
            back_kb = InlineKeyboardMarkup([[InlineKeyboardButton("↩️ Назад к профилю", callback_data="back_profile")]])
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=query.message.message_id,
                    text=stats_text,
                    parse_mode=ParseMode.MARKDOWN_V2,
                    reply_markup=back_kb,
                )
            except Exception:
                await context.bot.sendMessage(chat_id, stats_text, reply_markup=back_kb, parse_mode=ParseMode.MARKDOWN_V2)
        finally:
            context.user_data["busy_stats"] = False
        return

    if data == "back_profile":
        res = supabase.table("users").select("id, created_at, username, email, avatar_url, tg_username").eq("id", user["id"]).limit(1).execute()
        info = (res.data or [user])[0]
        text = build_profile_text(info, tg_name)
        ikb = InlineKeyboardMarkup([[InlineKeyboardButton("📊 Статистика", callback_data="user_stats")]])
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=query.message.message_id,
                text=text,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=ikb,
            )
        except Exception:
            await context.bot.sendMessage(chat_id, text, reply_markup=ikb, parse_mode=ParseMode.MARKDOWN_V2)
        return


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("profile", cmd_profile))
    app.add_handler(CommandHandler("boards", cmd_boards))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^Профиль$"), cmd_profile))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^Доски$"), cmd_boards))
    app.add_handler(CallbackQueryHandler(on_callback))
    async def on_error(update_obj: object, context_obj: ContextTypes.DEFAULT_TYPE):
        try:
            print("[ERROR] Unhandled exception:", context_obj.error)
            chat_id_local = None
            if hasattr(update_obj, "effective_chat") and update_obj.effective_chat:
                chat_id_local = update_obj.effective_chat.id
            elif hasattr(update_obj, "callback_query") and update_obj.callback_query and update_obj.callback_query.message:
                chat_id_local = update_obj.callback_query.message.chat.id
            if chat_id_local:
                await app.bot.sendMessage(chat_id_local, "Произошла ошибка. Пожалуйста, повторите попытку позже.")
        except Exception:
            pass
    app.add_error_handler(on_error)
    print("[БОТ] Telegram-бот запущен. Ожидаю обновления…")
    app.run_polling()


if __name__ == "__main__":
    main()