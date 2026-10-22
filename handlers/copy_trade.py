import logging
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.notifications import notification_service
from models.database import db, CopyTradeWallet
from keyboards.menus import (
    get_copy_trade_keyboard,
    get_copy_wallet_actions_keyboard,
)


logger = logging.getLogger(__name__)


async def copy_trade_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    message = "📋 <b>Copy Trade</b>\n\nSelect a copy trade wallet:"
    
    await query.edit_message_text(
        message,
        reply_markup=get_copy_trade_keyboard(),
        parse_mode="HTML"
    )


async def copy_add_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    context.user_data["awaiting_wallet_address"] = True
    
    await query.edit_message_text(
        "➕ <b>Add Wallet to Copy</b>\n\n"
        "Send the wallet address you want to copy.\n\n"
        "Example: <code>71V6zG5DhJjvM6Yt8bcmCW9rBDD3r5uSrqk7gJ6PYf2v</code>",
        reply_markup=get_confirm_keyboard("add", "add_cancel", "menu_copy_trade"),
        parse_mode="HTML"
    )


async def copy_add_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.pop("awaiting_wallet_address", None)
    await copy_trade_menu(update, context)


async def handle_copy_wallet_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_wallet_address"):
        address = update.message.text.strip()
        context.user_data["wallet_address"] = address
        context.user_data.pop("awaiting_wallet_address", None)
        
        await query.edit_message_text(
            "📝 <b>Wallet Name</b>\n\n"
            "Give this wallet a name for easy reference.",
            reply_markup=get_confirm_keyboard("name", "name_cancel", "menu_copy_trade"),
            parse_mode="HTML"
        )
        return True
    return False


async def handle_copy_wallet_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_wallet_name"):
        wallet_name = update.message.text.strip()
        wallet_address = context.user_data.get("wallet_address")
        
        if not wallet_address:
            await update.message.reply_text("❌ No wallet address provided")
            return True
        
        # Add wallet to database
        wallet = CopyTradeWallet(
            user_id=update.effective_user.id,
            wallet_address=wallet_address,
            wallet_name=wallet_name,
            is_active=True
        )
        db.add_copy_trade_wallet(wallet)
        
        await update.message.reply_text(
            f"✅ <b>Wallet Added!</b>\n\n"
            f"Wallet: <code>{wallet_address}</code>\n"
            f"Name: {wallet_name}\n\n"
            "You can now copy trades from this wallet.",
            parse_mode="HTML"
        )
        
        context.user_data.pop("awaiting_wallet_name", None)
        await copy_trade_menu(update, context)
        return True
    return False


async def copy_list_wallets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    wallets = db.get_copy_trade_wallets(update.from_user.id)
    
    if not wallets:
        await query.edit_message_text(
            "📋 <b>My Copy Wallets</b>\n\nNo wallets added yet.",
            reply_markup=get_copy_trade_keyboard(),
            parse_mode="HTML"
        )
        return
    
    message = "📋 <b>My Copy Wallets</b>\n\n"
    for wallet in wallets:
        message += (
            f"📍 <b>#{wallet.id}</b>: {wallet.wallet_name}\n"
            f"   Address: {wallet.wallet_address[:8]}...{wallet.wallet_address[-4:]}\n"
            f"   Status: {'Active' if wallet.is_active else 'Inactive'}\n\n"
        )
    
    await query.edit_message_text(
        message,
        reply_markup=get_copy_trade_keyboard(),
        parse_mode="HTML"
    )


async def copy_wallet_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    wallet_id = int(query.data.replace("copy_wallet_", ""))
    wallet = db.get_copy_trade_wallet(wallet_id)
    
    if not wallet:
        await query.edit_message_text("❌ Wallet not found", reply_markup=get_copy_trade_keyboard(), parse_mode="HTML")
        return
    
    message = (
        f"📋 <b>Wallet Details</b>\n\n"
        f"📍 Address: <code>{wallet.wallet_address}</code>\n"
        f"📛 Name: {wallet.wallet_name}\n"
        f"🔢 ID: {wallet.id}\n"
        f"🟢 Status: {'Active' if wallet.is_active else 'Inactive'}"
    )
    
    await query.edit_message_text(
        message,
        reply_markup=get_copy_wallet_actions_keyboard(wallet.id),
        parse_mode="HTML"
    )


async def copy_edit_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    wallet_id = int(query.data.replace("copy_edit_", ""))
    wallet = db.get_copy_trade_wallet(wallet_id)
    
    if not wallet:
        await query.edit_message_text("❌ Wallet not found", reply_markup=get_copy_trade_keyboard(), parse_mode="HTML")
        return
    
    await query.edit_message_text(
        "📝 <b>Edit Wallet Name</b>\n\n"
        f"Current name: {wallet.wallet_name}\n\n"
        "Send the new wallet name:",
        reply_markup=get_confirm_keyboard("edit", "edit_cancel", "menu_copy_trade"),
        parse_mode="HTML"
    )


async def copy_toggle_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    wallet_id = int(query.data.replace("copy_toggle_", ""))
    wallet = db.get_copy_trade_wallet(wallet_id)
    
    if not wallet:
        await query.edit_message_text("❌ Wallet not found", reply_markup=get_copy_trade_keyboard(), parse_mode="HTML")
        return
    
    wallet.is_active = not wallet.is_active
    db.update_copy_trade_wallet(wallet)
    
    status = "Active" if wallet.is_active else "Inactive"
    
    await query.edit_message_text(
        f"✅ <b>Wallet Toggled!</b>\n\n"
        f"Wallet: {wallet.wallet_name}\n"
        f"Status: {status}",
        reply_markup=get_copy_trade_keyboard(),
        parse_mode="HTML"
    )


async def copy_remove_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    wallet_id = int(query.data.replace("copy_remove_", ""))
    db.delete_copy_trade_wallet(wallet_id)
    
    await query.edit_message_text(
        "🗑️ <b>Wallet Removed!</b>\n\n"
        "The wallet has been removed from your copy trade list.",
        reply_markup=get_copy_trade_keyboard(),
        parse_mode="HTML"
    )


async def copy_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    message = "⚙️ <b>Copy Trade Settings</b>\n\n"
    message += "Configure your copy trade preferences here."
    
    await query.edit_message_text(
        message,
        reply_markup=get_copy_trade_keyboard(),
        parse_mode="HTML"
    )


async def copy_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    wallets = db.get_copy_trade_wallets(update.from_user.id)
    
    if not wallets:
        await query.edit_message_text(
            "📊 <b>Copy Trade History</b>\n\nNo trade history yet.",
            reply_markup=get_copy_trade_keyboard(),
            parse_mode="HTML"
        )
        return
    
    message = "📊 <b>Copy Trade History</b>\n\n"
    for wallet in wallets:
        message += (
            f"📍 Wallet #{wallet.id}: {wallet.wallet_name}\n"
        )
    
    await query.edit_message_text(
        message,
        reply_markup=get_copy_trade_keyboard(),
        parse_mode="HTML"
    )