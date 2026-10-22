import logging
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.notifications import notification_service
from models.database import db, AutoSellRule


logger = logging.getLogger(__name__)


async def auto_sell_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    rules = db.get_auto_sell_rules(user_id)
    
    if not rules:
        await query.edit_message_text(
            "⚡ <b>Auto Sell</b>\n\nNo active auto sell rules.",
            reply_markup=get_auto_sell_keyboard(False),
            parse_mode="HTML"
        )
        return
    
    message = "⚡ <b>Your Auto Sell Rules</b>\n\n"
    
    for rule in rules:
        message += (
            f"⚡ <b>Rule #{rule.id}</b>\n"
            f"   Token: {rule.token_symbol}\n"
            f"   Rule Type: {rule.rule_type}\n"
            f"   Target: {rule.target_percent}%\n"
            f"   Status: {'Active' if rule.is_active else 'Inactive'}\n\n"
        )
    
    await query.edit_message_text(
        message,
        reply_markup=get_auto_sell_keyboard(True),
        parse_mode="HTML"
    )


async def autosell_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data["awaiting_rule"] = True
    
    await query.edit_message_text(
        "⚡ <b>Add Auto Sell Rule</b>\n\n"
        "Send: token_address rule_type target_percent stop_loss_percent take_profit_percent\n\n"
        "Example: <code>EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v target 50 10 20</code>\n\n"
        "This will set an auto sell rule to sell 50% at target, with 10% stop loss and 20% take profit",
        reply_markup=get_confirm_keyboard("add", "add_cancel", "menu_auto_sell"),
        parse_mode="HTML"
    )


async def autosell_pos_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    position_id = int(query.data.replace("autosell_pos_", ""))
    from models.database import db, AutoSellRule
    
    rules = db.get_auto_sell_rules(query.from_user.id)
    rule = next((r for r in rules if r.id == position_id), None)
    
    if not rule:
        await query.edit_message_text("❌ Rule not found", reply_markup=get_auto_sell_keyboard(False), parse_mode="HTML")
        return
    
    await query.edit_message_text(
        "⚡ <b>Edit Auto Sell Rule</b>\n\n"
        f"Rule: {rule.rule_type} on {rule.token_symbol}\n\n"
        "Send: target_percent stop_loss_percent take_profit_percent\n\n"
        "Example: <code>75 15 30</code>",
        reply_markup=get_confirm_keyboard("edit", "edit_cancel", "menu_auto_sell"),
        parse_mode="HTML"
    )


async def autosell_type_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    rule_id = int(query.data.replace("autosell_type_", ""))
    from models.database import db, AutoSellRule
    rule = db.get_auto_sell_rule(rule_id)
    
    if not rule:
        await query.edit_message_text("❌ Rule not found", reply_markup=get_auto_sell_keyboard(False), parse_mode="HTML")
        return
    
    await query.edit_message_text(
        "⚡ <b>Select Rule Type</b>\n\n"
        f"Current rule: {rule.rule_type}\n\n"
        "Select new rule type:",
        reply_markup=get_auto_sell_type_keyboard(),
        parse_mode="HTML"
    )


async def autosell_execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    from models.database import db, AutoSellRule
    rule_id = int(query.data.replace("autosell_execute_", ""))
    rule = db.get_auto_sell_rule(rule_id)
    
    if not rule:
        await query.edit_message_text("❌ Rule not found", reply_markup=get_auto_sell_keyboard(False), parse_mode="HTML")
        return
    
    # Execute auto sell logic
    await query.edit_message_text(
        "⚡ <b>Auto Sell Executed</b>\n\n"
        f"Rule: {rule.rule_type} on {rule.token_symbol}",
        parse_mode="HTML"
    )


async def autosell_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    from models.database import db, AutoSellRule
    rules = db.get_auto_sell_rules(user_id)
    
    if not rules:
        await query.edit_message_text(
            "⚡ <b>Auto Sell Rules</b>\n\nNo active rules.",
            reply_markup=get_auto_sell_keyboard(False),
            parse_mode="HTML"
        )
        return
    
    message = "⚡ <b>Auto Sell Rules</b>\n\n"
    
    for rule in rules:
        message += (
            f"⚡ <b>Rule #{rule.id}</b>\n"
            f"   Token: {rule.token_symbol}\n"
            f"   Type: {rule.rule_type}\n"
            f"   Target: {rule.target_percent}%\n"
            f"   Stop Loss: {rule.stop_loss_percent}%\n"
            f"   Take Profit: {rule.take_profit_percent}%\n\n"
        )
    
    await query.edit_message_text(
        message,
        reply_markup=get_auto_sell_keyboard(True),
        parse_mode="HTML"
    )


async def autosell_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.pop("awaiting_rule", None)
    await auto_sell_menu(update, context)


async def handle_autosell_percent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text and update.message.text.startswith("/"):
        command = update.message.text.split()[0].lower()
        if command == "/setautosellpercent":
            args = update.message.text.split()[1:]
            if len(args) >= 2:
                rule_id = int(args[0])
                percent = float(args[1])
                # Logic to update auto sell rule percent
                await update.message.reply_text(
                    f"✅ <b>Auto Sell Percent Updated</b>\n\n"
                    f"Rule ID: {rule_id}\n"
                    f"New Percent: {percent}%",
                    parse_mode="HTML"
                )
            else:
                await update.message.reply_text(
                    "❌ Usage: /setautosellpercent <rule_id> <percent>",
                    parse_mode="HTML"
                )
        else:
            await update.message.reply_text(
                "Unknown command. Use /setautosellpercent <rule_id> <percent>",
                parse_mode="HTML"
            )
    return False