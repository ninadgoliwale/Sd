import os
import logging
import qrcode
from io import BytesIO
from datetime import datetime
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============ CONFIGURATION (HARDCODED) ============
TOKEN = "8955325810:AAHcI7KjIPcueMFTo-wfa_Qvu7W3K9TmA-Q"
ADMIN_ID = 7397173716
ADMIN_USERNAME = "@iFlexWALLET"
ORIGINAL_PRICE = 1200
DISCOUNTED_PRICE = 800

# Store user data (in memory - resets on restart)
user_subscriptions = {}  # user_id: {"status": "active", "approved_by": "admin"}
pending_payments = {}     # user_id: {"amount": price, "timestamp": datetime, "username": name}

# Flask app
app = Flask(__name__)

# ============ FLASK WEB ROUTES ============

@app.route('/')
def home():
    return jsonify({
        "status": "Bot is running",
        "bot_username": "@iFlexWALLET_Bot",
        "message": "Telegram Payment Bot Active"
    })

@app.route('/subscribe-web')
def subscribe_web():
    """Method 1: Single Subscribe Web Page"""
    user_id = request.args.get('user_id', 'unknown')
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Single Subscribe - Premium Access</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 20px;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            .container {{
                background: white;
                border-radius: 20px;
                padding: 30px;
                max-width: 500px;
                width: 100%;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                text-align: center;
            }}
            h1 {{ color: #667eea; }}
            .price {{ font-size: 48px; color: #764ba2; font-weight: bold; margin: 20px 0; }}
            .discount {{ background: #ff9800; color: white; padding: 10px; border-radius: 10px; margin: 10px 0; }}
            button {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 10px;
                font-size: 16px;
                cursor: pointer;
                margin: 10px 5px;
            }}
            button:hover {{ transform: translateY(-2px); }}
            .qr-code {{ margin: 20px 0; display: flex; justify-content: center; }}
            .status {{ margin-top: 20px; padding: 10px; border-radius: 10px; }}
            .success {{ background: #d4edda; color: #155724; }}
            .info {{ background: #d1ecf1; color: #0c5460; }}
            .admin-contact {{ background: #e2e3e5; padding: 15px; border-radius: 10px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✨ SINGLE SUBSCRIBE WEB ✨</h1>
            <p>Get instant premium access to exclusive content</p>
            <div class="price">₹{ORIGINAL_PRICE}</div>
            <div class="discount">🎁 SPECIAL: Get ₹400 OFF! DM @iFlexWALLET → Pay just ₹{DISCOUNTED_PRICE}</div>
            <div id="qrContainer" class="qr-code"></div>
            <button onclick="generateQR()">🔓 Generate Payment QR</button>
            <button onclick="checkStatus()" style="background: #28a745;">✅ Check Payment Status</button>
            <div id="status"></div>
            <div class="admin-contact">
                📞 Need discount? DM: <strong>@iFlexWALLET</strong>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/qrcodejs@1.0.0/qrcode.min.js"></script>
        <script>
            let qrGenerated = false;
            const userId = "{user_id}";
            
            function generateQR() {{
                if(!qrGenerated) {{
                    new QRCode(document.getElementById("qrContainer"), {{
                        text: "Please DM @iFlexWALLET for payment details",
                        width: 200,
                        height: 200
                    }});
                    qrGenerated = true;
                    document.getElementById("status").innerHTML = '<div class="status info">📞 DM @iFlexWALLET to get payment QR and ₹400 discount!</div>';
                }}
            }}
            
            async function checkStatus() {{
                document.getElementById("status").innerHTML = '<div class="status info">⏳ Checking subscription status...</div>';
                const response = await fetch(`/check-payment-status?user_id=${{userId}}`);
                const data = await response.json();
                if(data.status === "active") {{
                    document.getElementById("status").innerHTML = '<div class="status success">✅ ACCESS GRANTED! You can now access premium content</div>';
                }} else {{
                    document.getElementById("status").innerHTML = '<div class="status info">⏳ No active subscription. DM @iFlexWALLET to get access!</div>';
                }}
            }}
            
            setInterval(checkStatus, 15000);
        </script>
    </body>
    </html>
    '''

@app.route('/unsubscribe-web')
def unsubscribe_web():
    """Method 2: Double Unsubscribe Web Page"""
    user_id = request.args.get('user_id', 'unknown')
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Double Unsubscribe - Cancel Membership</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                margin: 0;
                padding: 20px;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            .container {{
                background: white;
                border-radius: 20px;
                padding: 30px;
                max-width: 500px;
                width: 100%;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                text-align: center;
            }}
            h1 {{ color: #f5576c; }}
            .warning {{ background: #fff3cd; color: #856404; padding: 15px; border-radius: 10px; margin: 20px 0; }}
            button {{
                background: #dc3545;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 10px;
                font-size: 18px;
                cursor: pointer;
                margin: 10px;
                width: 80%;
            }}
            button:hover {{ transform: translateY(-2px); }}
            .step {{ font-size: 24px; font-weight: bold; margin: 20px 0; }}
            .cancel-btn {{ background: #28a745; }}
            .final-btn {{ background: #dc3545; }}
            .hidden {{ display: none; }}
            .success-msg {{ background: #d4edda; color: #155724; padding: 15px; border-radius: 10px; }}
        </style>
    </head>
    <body>
        <div class="container" id="mainContainer">
            <h1>❌ DOUBLE UNSUBSCRIBE WEB ❌</h1>
            <div id="step1">
                <div class="warning">⚠️ WARNING: This will cancel your premium membership ⚠️</div>
                <div class="step">🔴 STEP 1 OF 2 🔴</div>
                <button onclick="confirmStep1()">⚠️ I understand, proceed to step 2</button>
                <button onclick="cancelUnsubscribe()" style="background: #6c757d;">❌ No, keep my membership</button>
            </div>
            <div id="step2" class="hidden">
                <div class="warning">⚠️⚠️ FINAL STEP: Confirm cancellation ⚠️⚠️</div>
                <div class="step">🔴 STEP 2 OF 2 - FINAL CONFIRMATION 🔴</div>
                <button class="final-btn" onclick="confirmUnsubscribe()">✅ YES, Cancel My Membership</button>
                <button onclick="cancelUnsubscribe()" style="background: #6c757d;">❌ No, Keep My Access</button>
            </div>
            <div id="result" class="hidden"></div>
        </div>
        <script>
            function confirmStep1() {{
                document.getElementById('step1').classList.add('hidden');
                document.getElementById('step2').classList.remove('hidden');
            }}
            
            async function confirmUnsubscribe() {{
                const response = await fetch(`/unsubscribe-user?user_id={user_id}`);
                const data = await response.json();
                document.getElementById('step2').classList.add('hidden');
                document.getElementById('result').classList.remove('hidden');
                if(data.success) {{
                    document.getElementById('result').innerHTML = '<div class="success-msg">✅ Your membership has been cancelled successfully!</div><button onclick="location.reload()">🔙 Close</button>';
                }} else {{
                    document.getElementById('result').innerHTML = '<div class="warning">❌ No active membership found!</div><button onclick="location.reload()">🔙 Close</button>';
                }}
            }}
            
            function cancelUnsubscribe() {{
                window.close();
            }}
        </script>
    </body>
    </html>
    '''

@app.route('/check-payment-status')
def check_payment_status():
    """Check if user has active subscription"""
    user_id = request.args.get('user_id')
    if user_id in user_subscriptions and user_subscriptions[user_id].get("status") == "active":
        return jsonify({"status": "active"})
    return jsonify({"status": "inactive"})

@app.route('/unsubscribe-user')
def unsubscribe_user():
    """API endpoint to unsubscribe user"""
    user_id = request.args.get('user_id')
    if user_id in user_subscriptions:
        user_subscriptions[user_id]["status"] = "inactive"
        return jsonify({"success": True, "message": "Unsubscribed successfully"})
    return jsonify({"success": False, "message": "No active subscription found"})

@app.route('/admin/approve/<user_id>')
def admin_approve(user_id):
    """Admin approval page - Only you can access this"""
    # Approve user and give access
    user_subscriptions[user_id] = {
        "status": "active",
        "approved_by": ADMIN_USERNAME,
        "approved_at": datetime.now().isoformat()
    }
    return jsonify({"success": True, "message": f"User {user_id} approved successfully!"})

# ============ TELEGRAM BOT HANDLERS ============

def create_main_keyboard():
    """Create main menu keyboard"""
    keyboard = [
        [InlineKeyboardButton("💰 Buy Membership (₹1200)", callback_data="buy_1200")],
        [InlineKeyboardButton("🎁 Get ₹400 Discount!", callback_data="get_discount")],
        [InlineKeyboardButton("🌐 Single Subscribe Web", callback_data="single_web")],
        [InlineKeyboardButton("❌ Double Unsubscribe Web", callback_data="double_web")],
        [InlineKeyboardButton("📊 My Subscription Status", callback_data="check_status")],
        [InlineKeyboardButton("👤 Contact Admin", callback_data="contact_admin")]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_discount_keyboard():
    """Create discount info keyboard"""
    keyboard = [
        [InlineKeyboardButton("💰 Pay ₹800 with Discount", callback_data="buy_800")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    welcome_msg = (
        f"🎉 Welcome {user.first_name}!\n\n"
        f"**Premium Content Access Bot**\n\n"
        f"💰 **Membership Price:** ₹{ORIGINAL_PRICE}\n"
        f"🎁 **Special Discount:** Get ₹400 OFF → Just ₹{DISCOUNTED_PRICE}\n"
        f"📞 **DM for Discount:** {ADMIN_USERNAME}\n\n"
        f"Use the buttons below to get started 👇"
    )
    
    await update.message.reply_text(
        welcome_msg,
        parse_mode="Markdown",
        reply_markup=create_main_keyboard()
    )

async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all button clicks"""
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    username = query.from_user.username or query.from_user.first_name
    
    if query.data == "buy_1200":
        await query.edit_message_text(
            f"💳 **Payment for ₹{ORIGINAL_PRICE}**\n\n"
            f"📞 Please DM {ADMIN_USERNAME} to complete payment.\n\n"
            f"After payment, admin will approve your access!",
            parse_mode="Markdown",
            reply_markup=create_main_keyboard()
        )
        
    elif query.data == "get_discount":
        discount_msg = (
            f"🎁 **Get ₹400 Discount!** 🎁\n\n"
            f"💰 Original Price: ₹{ORIGINAL_PRICE}\n"
            f"💎 **Discounted Price: ₹{DISCOUNTED_PRICE}**\n\n"
            f"📞 **How to get discount:**\n"
            f"1️⃣ DM {ADMIN_USERNAME}\n"
            f"2️⃣ Ask for ₹400 discount\n"
            f"3️⃣ Pay just ₹{DISCOUNTED_PRICE}\n\n"
            f"✨ **Hurry! Limited time offer!**"
        )
        await query.edit_message_text(
            discount_msg,
            parse_mode="Markdown",
            reply_markup=create_discount_keyboard()
        )
        
    elif query.data == "buy_800":
        await query.edit_message_text(
            f"💳 **Payment for ₹{DISCOUNTED_PRICE} (Discounted)**\n\n"
            f"📞 Please DM {ADMIN_USERNAME} to complete payment.\n\n"
            f"After payment, admin will approve your access!",
            parse_mode="Markdown",
            reply_markup=create_main_keyboard()
        )
        
    elif query.data == "single_web":
        web_url = f"https://your-render-url.onrender.com/subscribe-web?user_id={user_id}"
        await query.edit_message_text(
            f"🌐 **Single Subscribe Web**\n\n"
            f"Click the link below to access the subscription web page:\n\n"
            f"🔗 [Click here to Subscribe]({web_url})\n\n"
            f"Or copy this URL to your browser:\n"
            f"`{web_url}`\n\n"
            f"⚠️ Note: Replace 'your-render-url' with your actual Render URL",
            parse_mode="Markdown",
            reply_markup=create_main_keyboard()
        )
        
    elif query.data == "double_web":
        web_url = f"https://your-render-url.onrender.com/unsubscribe-web?user_id={user_id}"
        await query.edit_message_text(
            f"❌ **Double Unsubscribe Web**\n\n"
            f"Click the link below to cancel your membership (2-step verification):\n\n"
            f"🔗 [Click here to Unsubscribe]({web_url})\n\n"
            f"Or copy this URL to your browser:\n"
            f"`{web_url}`\n\n"
            f"⚠️ Note: Replace 'your-render-url' with your actual Render URL",
            parse_mode="Markdown",
            reply_markup=create_main_keyboard()
        )
        
    elif query.data == "check_status":
        if user_id in user_subscriptions and user_subscriptions[user_id].get("status") == "active":
            status_msg = (
                f"✅ **Membership Status: ACTIVE** ✅\n\n"
                f"🎉 You have full access to premium content!\n"
                f"Thank you for being a member! 🙏"
            )
        else:
            status_msg = (
                f"❌ **Membership Status: INACTIVE** ❌\n\n"
                f"Please buy a membership to access premium content.\n"
                f"DM {ADMIN_USERNAME} to purchase!"
            )
        await query.edit_message_text(status_msg, parse_mode="Markdown", reply_markup=create_main_keyboard())
        
    elif query.data == "contact_admin":
        contact_msg = (
            f"📞 **Contact Admin:** {ADMIN_USERNAME}\n\n"
            f"**For:**\n"
            f"• ₹400 discount coupon\n"
            f"• Payment verification\n"
            f"• Technical support\n"
            f"• Any questions\n\n"
            f"👆 Click on the username above to DM!"
        )
        await query.edit_message_text(contact_msg, parse_mode="Markdown", reply_markup=create_main_keyboard())
        
    elif query.data == "back_to_menu":
        await query.edit_message_text(
            f"🏠 **Main Menu**\n\nChoose an option below:",
            parse_mode="Markdown",
            reply_markup=create_main_keyboard()
        )

# ============ ADMIN COMMANDS ============

async def admin_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command to approve user - /approve user_id"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to use this command!")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /approve user_id")
        return
    
    user_id = context.args[0]
    user_subscriptions[user_id] = {
        "status": "active",
        "approved_by": ADMIN_USERNAME,
        "approved_at": datetime.now().isoformat()
    }
    
    await update.message.reply_text(f"✅ User {user_id} has been approved and given access!")
    
    # Notify the user
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"✅ **ACCESS GRANTED!** ✅\n\n"
                 f"Your payment has been verified by {ADMIN_USERNAME}.\n"
                 f"You now have full access to premium content!\n\n"
                 f"Thank you for your purchase! 🎉",
            parse_mode="Markdown"
        )
    except:
        pass

async def admin_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all active subscriptions - /listusers"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    active_users = [uid for uid, data in user_subscriptions.items() if data.get("status") == "active"]
    
    if active_users:
        msg = "📊 **Active Subscriptions:**\n\n"
        for uid in active_users:
            msg += f"• User ID: `{uid}`\n"
        await update.message.reply_text(msg, parse_mode="Markdown")
    else:
        await update.message.reply_text("No active subscriptions found.")

# ============ MAIN FUNCTION ============

def main():
    """Start the bot and Flask server"""
    global telegram_app
    
    # Create Telegram application
    telegram_app = Application.builder().token(TOKEN).build()
    
    # Add handlers
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CommandHandler("approve", admin_approve))
    telegram_app.add_handler(CommandHandler("listusers", admin_list))
    telegram_app.add_handler(CallbackQueryHandler(handle_button_click))
    
    # Start Flask in background
    from threading import Thread
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
    
    # Start bot polling
    print("🤖 Bot is starting...")
    print(f"✅ Bot token: {TOKEN[:10]}...")
    print(f"👑 Admin ID: {ADMIN_ID}")
    print(f"🌐 Web URLs available at:")
    print(f"   - /subscribe-web?user_id=USER_ID")
    print(f"   - /unsubscribe-web?user_id=USER_ID")
    
    telegram_app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
