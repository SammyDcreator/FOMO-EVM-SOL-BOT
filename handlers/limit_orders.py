import logging
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.solana import solana_service
from services.notifications import notification_service
from models.database import db, LimitOrder
from keyboards.menus import (
    get_limit_orders_keyboard,
)


logger = logging.getLogger(__name__)


async def limit_orders_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    limit_orders = db.get_limit_orders(user_id, active_only=True)
    
    if not limit_orders:
        await query.edit_message_text(
            "📋 <b>Limit Orders</b>\n\nNo active limit orders.",
            reply_markup=get_limit_orders_keyboard(False),
            parse_mode="HTML"
        )
        return
    
    message = "📋 <b>Your Limit Orders</b>\n\n"
    
    for order in limit_orders:
        message += (
            f"📋 <b>Order #{order.id}</b>\n"
            f"   Token: {order.token_symbol}\n"
            f"   Side: {order.side}\n"
            f"   Amount: {order.amount:.6f}\n"
            f"   Target: {order.target_price_sol:.6f} SOL\n"
            f"   Status: {'Active' if order.is_active else 'Inactive'}\n\n"
        )
    
    await query.edit_message_text(
        message,
        reply_markup=get_limit_orders_keyboard(True),
        parse_mode="HTML"
    )


async def limit_create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "➕ <b>Create Limit Order</b>\n\n"
        "Send the details for your limit order:\n\n"
        "Format: <code>token_address side target_price amount</code>\n\n"
        "Example: <code>EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v buy 0.05 0.5</code>\n\n"
        "This will buy 0.5 SOL worth of the token at or below 0.05 SOL",
        reply_markup=get_confirm_keyboard("create", "create_cancel", "menu_limit_orders"),
        parse_mode="HTML"
    )


async def limit_buy_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "📋 <b>Create Buy Limit Order</b>\n\n"
        "Send: token_address target_price amount\n\n"
        "Example: <code>EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v 0.05 1</code>",
        reply_markup=get_confirm_keyboard("create", "create_cancel", "menu_limit_orders"),
        parse_mode="HTML"
    )


async def limit_sell_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "📋 <b>Create Sell Limit Order</b>\n\n"
        "Send: token_address target_price amount\n\n"
        "Example: <code>EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v 0.05 1</code>",
        reply_markup=get_confirm_keyboard("create", "create_cancel", "menu_limit_orders"),
        parse_mode="HTML"
    )


async def limit_sell_pos_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    position_id = int(query.data.replace("limit_sell_pos_", ""))
    from models.database import db, Position
    position = db.get_positions(query.from_user.id)
    position = next((p for p in position if p.id == position_id), None)
    
    if not position:
        await query.edit_message_text("❌ Position not found", reply_markup=get_limit_orders_keyboard(False), parse_mode="HTML")
        return
    
    await query.edit_message_text(
        "📋 <b>Create Sell Limit Order</b>\n\n"
        f"Position: {position.token_symbol} ({position.amount:.6f})\n\n"
        "Send: target_price amount\n\n"
        "Example: <code>0.05 0.5</code>",
        reply_markup=get_confirm_keyboard("create", "create_cancel", "menu_limit_orders"),
        parse_mode="HTML"
    )


async def limit_execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if data.startswith("limit_execute_"):
        order_id = int(data.replace("limit_execute_", ""))
    else:
        order_id = None
    
    from models.database import db, LimitOrder
    order = db.get_limit_order(order_id)
    
    if not order:
        await query.edit_message_text("❌ Order not found", reply_markup=get_limit_orders_keyboard(False), parse_mode="HTML")
        return
    
    # Execute the limit order
    token_address = order.token_mint
    target_price = order.target_price_sol
    amount = order.amount
    side = order.side
    
    # Simple execution logic
    await query.edit_message_text(
        "⏳ <b>Executing Limit Order</b>\n\n"
        "Processing your limit order...",
        parse_mode="HTML"
    )
    
    # Placeholder - in real implementation, would execute via Jupiter API
    await query.edit_message_text(
        "✅ <b>Limit Order Executed</b>\n\n"
        f"Order: {side} {amount:.6f} {order.token_symbol}\n"
        f"at target price: {target_price:.6f} SOL",
        parse_mode="HTML"
    )


async def limit_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    from models.database import db, LimitOrder
    limit_orders = db.get_limit_orders(user_id, active_only=True)
    
    if not limit_orders:
        await query.edit_message_text(
            "📋 <b>Limit Orders</b>\n\nNo active limit orders.",
            reply_markup=get_limit_orders_keyboard(False),
            parse_mode="HTML"
        )
        return
    
    message = "📋 <b>Your Limit Orders</b>\n\n"
    
    for order in limit_orders:
        message += (
            f"📋 <b>Order #{order.id}</b>\n"
            f"   Token: {order.token_symbol}\n"
            f"   Side: {order.side}\n"
            f"   Amount: {order.amount:.6f}\n"
            f"   Target: {order.target_price_sol:.6f} SOL\n"
            f"   Status: {'Active' if order.is_active else 'Inactive'}\n\n"
        )
    
    await query.edit_message_text(
        message,
        reply_markup=get_limit_orders_keyboard(True),
        parse_mode="HTML"
    )


async def limit_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data.startswith("limit_cancel_"):
        order_id = int(data.replace("limit_cancel_", ""))
    else:
        order_id = None
    
    from models.database import db, LimitOrder
    db.cancel_limit_order(order_id)
    
    await query.edit_message_text(
        "✅ <b>Limit Order Cancelled</b>\n\n"
        "The limit order has been cancelled.",
        reply_markup=get_limit_orders_keyboard(False),
        parse_mode="HTML"
    )


async def handle_limit_token_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text and update.message.text.startswith("/"):
        command = update.message.text.split()[0].lower()
        if command == "/setlimit":
            args = update.message.text.split()[1:]
            if len(args) >= 3:
                token_address = args[0]
                target_price = float(args[1])
                amount = float(args[2])
                # Logic to set limit order
                await update.message.reply_text(
                    f"✅ <b>Limit Order Set</b>\n\n"
                    f"Token: {token_address}\n"
                    f"Target Price: {target_price:.6f} SOL\n"
                    f"Amount: {amount:.6f} SOL",
                    parse_mode="HTML"
                )
            else:
                await update.message.reply_text(
                    "❌ Usage: /setlimit <token_address> <target_price> <amount>",
                    parse_mode="HTML"
                )
        else:
            await update.message.reply_text(
                "Unknown command. Use /setlimit <token_address> <target_price> <amount>",
                parse_mode="HTML"
            )
    return False


async def handle_limit_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text and update.message.text.startswith("/"):
        command = update.message.text.split()[0].lower()
        if command == "/setlimitprice":
            args = update.message.text.split()[1:]
            if len(args) >= 2:
                token_address = args[0]
                limit_price = float(args[1])
                # Logic to set limit price
                await update.message.reply_text(
                    f"✅ <b>Limit Price Set</b>\n\n"
                    f"Token: {token_address}\n"
                    f"Limit Price: {limit_price:.6f} SOL",
                    parse_mode="HTML"
                )
            else:
                await update.message.reply_text(
                    "❌ Usage: /setlimitprice <token_address> <limit_price>",
                    parse_mode="HTML"
                )
        else:
            await update.message.reply_text(
                "Unknown command. Use /setlimitprice <token_address> <limit_price>",
                parse_mode="HTML"
            )
    return False


async def handle_limit_amount_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text and update.message.text.startswith("/"):
        command = update.message.text.split()[0].lower()
        if command == "/setlimitamount":
            args = update.message.text.split()[1:]
            if len(args) >= 1:
                amount = float(args[0])
                await update.message.reply_text(
                    f"✅ <b>Limit Amount Set</b>\n\n"
                    f"Amount: {amount:.6f} SOL",
                    parse_mode="HTML"
                )
            else:
                await update.message.reply_text(
                    "❌ Usage: /setlimitamount <amount>",
                    parse_mode="HTML"
                )
        else:
            await update.message.reply_text(
                "Unknown command. Use /setlimitamount <amount>",
                parse_mode="HTML"
            )
    return False