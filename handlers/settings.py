import logging
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.notifications import notification_service
from models.database import db, User
from keyboards.menus import (
    get_settings_keyboard,
)


logger = logging.getLogger(__name__)


async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    message = "⚙️ <b>Settings</b>\n\n"
    message += "Configure your bot settings here.\n\n"
    
    await query.edit_message_text(
        message,
        reply_markup=get_settings_keyboard(),
        parse_mode="HTML"
    )


async def settings_slippage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "⚙️ <b>Slippage Settings</b>\n\n"
        "Configure slippage tolerance for trades.",
        reply_markup=get_slippage_keyboard(),
        parse_mode="HTML"
    )


async def slippage_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    slippage_value = query.data.replace("slippage_", "")
    
    await query.edit_message_text(
        f"⚙️ <b>Slippage Set</b>\n\n"
        f"Slippage set to: {slippage_value}%",
        parse_mode="HTML"
    )


async def settings_priority_fee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "⚙️ <b>Priority Fee Settings</b>\n\n"
        "Configure priority fee for transactions.",
        reply_markup=get_priority_fee_keyboard(),
        parse_mode="HTML"
    )


async def priority_fee_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    fee_value = query.data.replace("priority_", "")
    
    await query.edit_message_text(
        f"⚙️ <b>Priority Fee Set</b>\n\n"
        f"Priority fee set to: {fee_value}",
        parse_mode="HTML"
    )


async def settings_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "⚙️ <b>Notifications Settings</b>\n\n"
        "Configure notification preferences.",
        reply_markup=get_notification_keyboard(),
        parse_mode="HTML"
    )


async def settings_security(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "⚙️ <b>Security Settings</b>\n\n"
        "Configure security settings for your account.",
        parse_mode="HTML"
    )


async def settings_export_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "⚙️ <b>Export Key</b>\n\n"
        "Export your encryption key for backup.",
        parse_mode="HTML"
    )


async def settings_delete_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "⚙️ <b>Delete Account</b>\n\n"
        "Are you sure you want to delete your account?",
        parse_mode="HTML"
    )


async def settings_delete_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "⚙️ <b>Account Deleted</b>\n\n"
        "Your account has been deleted.",
        parse_mode="HTML"
    )