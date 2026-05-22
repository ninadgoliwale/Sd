import logging
from datetime import datetime
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============ CONFIGURATION ============
TOKEN = "8955325810:AAHcI7KjIPcueMFTo-wfa_Qvu7W3K9TmA-Q"
ADMIN_ID = 7397173716
ADMIN_USERNAME = "@iFlexWALLET"
ORIGINAL_PRICE = 1200
DISCOUNTED_PRICE = 800

# Store user data
user_subscriptions = {}  # user_id: {"status": "active"}
pending_payments = {}

app = Flask(__name__)

# ============ FLASK WEB PAGES ============

@app.route('/')
def home():
    return jsonify({"status": "Bot is running", "bot": "@iFlexWALLET_Bot"})

@app.route('/subscribe-web')
def subscribe_web():
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
                text-align: center;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
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
            .status {{ margin-top: 20px; padding: 10px; border-radius: 10px; }}
            .success {{ background: #d4edda; color: #155724; }}
            .info {{ background: #d1ecf1; color: #0c5460; }}
            .payment-info {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 10px;
                margin: 15px 0;
                text-align: left;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✨ SINGLE SUBSCRIBE WEB ✨</h1>
            <p>Get premium access to exclusive content</p>
            <div class="price">₹{ORIGINAL_PRICE}</div>
            <div class="discount">🎁 SPECIAL: ₹400 OFF → Pay ₹{DISCOUNTED_PRICE}</div>
            
            <div class="payment-info">
                <strong>📱 How to Get Access:</strong><br><br>
                1️⃣ DM <strong>@iFlexWALLET</strong> for ₹400 discount<br>
                2️⃣ Make payment of ₹{DISCOUNTED_PRICE}<br>
                3️⃣ Admin will approve your access<br>
                4️⃣ Start enjoying premium content! 🎉
            </div>
            
            <button onclick="checkStatus()">✅ Check My Subscription Status</button>
            <div id="status"></div>
        </div>
        <script>
            const userId = "{user_id}";
            
            async function checkStatus() {{
                document.getElementById("status").innerHTML = '<div class="status info">⏳ Checking...</div>';
                try {{
                    const response = await fetch(`/check-status?user_id=${{userId}}`);
                    const data = await response.json();
                    if(data.status === "active") {{
                        document.getElementById("status").innerHTML = '<div class="status success">✅ ACCESS GRANTED! You can now access premium content!</div>';
                    }} else {{
                        document.getElementById("status").innerHTML = '<div class="status info">⏳ No active subscription. DM @iFlexWALLET to get access!</div>';
                    }}
                }} catch(e) {{
                    document.getElementById("status").innerHTML = '<div class="status info">Check your connection</div>';
                }}
            }}
            
            checkStatus();
            setInterval(checkStatus, 15000);
        </script>
    </body>
    </html>
    '''

@app.route('/unsubscribe-web')
def unsubscribe_web():
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
                text-align: center;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
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
            .hidden {{ display: none; }}
            .success-msg {{ background: #d4edda; color: #155724; padding: 15px; border-radius: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>❌ DOUBLE UNSUBSCRIBE WEB ❌</h1>
            <div id="step1">
                <div class="warning">⚠️ WARNING: This will cancel your premium membership ⚠️</div>
                <div class="step">🔴 STEP 1 OF 2 🔴</div>
                <button onclick="confirmStep1()">⚠️ Proceed to Step 2</button>
                <button onclick="cancelUnsubscribe()" class="cancel-btn">❌ Keep My Membership</button>
            </div>
            <div id="step2" class="hidden">
                <div class="warning">⚠️⚠️ FINAL STEP: Confirm Cancellation ⚠️⚠️</div>
                <div class="step">🔴 STEP 2 OF 2 - FINAL CONFIRMATION 🔴</div>
                <button onclick="confirmUnsubscribe()">✅ YES, Cancel My Membership</button>
                <button onclick="cancelUnsubscribe()" class="cancel-btn">❌ No, Keep Access</button>
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
                    document.getElementById('result').innerHTML = '<div class="success-msg">✅ Your membership has been cancelled!</div><button onclick="window.location.reload()">Close</button>';
                }} else {{
                    document.getElementById('result').innerHTML = '<div class="warning">❌ No active membership found!</div><button onclick="window.location.reload()">Close</button>';
                }}
            }}
            
            function cancelUnsubscribe() {{
                window.close();
            }}
        </script>
    </body>
    </html>
    '''

@app.route('/check-status')
def check_status():
    user_id = request.args.get('user_id')
    if user_id in user_subscriptions and user_subscriptions[user_id].get("status") == "active":
        return jsonify({"status": "active"})
    return jsonify({"status": "inactive"})

@app.route('/unsubscribe-user')
def unsubscribe_user():
    user_id = request.args.get('user_id')
    if user_id in user_subscriptions:
        user_subscriptions[user_id]["status"] = "inactive"
        return jsonify({"success": True})
    return jsonify({"success": False})

# ============ TELEGRAM BOT ============

def create_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("💰 Buy Membership (₹1200)", callback_data="buy")],
        [InlineKeyboardButton("🌐 Single Subscribe Web", callback_data="single_web")],
        [InlineKeyboardButton("❌ Double Unsubscribe Web", callback_data="double_web")],
        [InlineKeyboardButton("📊 My Subscription Status", callback_data="check_status")],
        [InlineKeyboardButton("👤 Contact Admin", callback_data="contact_admin")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"🎉 Welcome {user.first_name}!\n\n"
        f"💰 Membership: ₹{ORIGINAL_PRICE}\n"
        f"🎁 Discount: ₹400 OFF → ₹{DISCOUNTED_PRICE}\n"
        f"📞 DM {ADMIN_USERNAME}\n\n"
        f"Choose an option:",
        reply_markup=create_main_keyboard()
    )

async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    render_url = "YOUR_RENDER_URL_HERE"  # CHANGE THIS AFTER DEPLOYMENT
    
    if query.data == "buy":
        await query.edit_message_text(
            f"💳 **How to Buy:**\n\n"
            f"1️⃣ DM {ADMIN_USERNAME}\n"
            f"2️⃣ Ask for ₹400 discount\n"
            f"3️⃣ Pay ₹{DISCOUNTED_PRICE}\n"
            f"4️⃣ Admin approves your access\n\n"
            f"✅ You'll get access immediately after approval!",
            parse_mode="Markdown",
            reply_markup=create_main_keyboard()
        )
    elif query.data == "single_web":
        url = f"https://{render_url}/subscribe-web?user_id={user_id}"
        await query.edit_message_text(
            f"🌐 **Single Subscribe Web:**\n\n"
            f"🔗 {url}\n\n"
            f"Click the link to check your subscription status!",
            parse_mode="Markdown",
            reply_markup=create_main_keyboard()
        )
    elif query.data == "double_web":
        url = f"https://{render_url}/unsubscribe-web?user_id={user_id}"
        await query.edit_message_text(
            f"❌ **Double Unsubscribe Web:**\n\n"
            f"🔗 {url}\n\n"
            f"⚠️ 2-step verification required to cancel membership!",
            parse_mode="Markdown",
            reply_markup=create_main_keyboard()
        )
    elif query.data == "check_status":
        if user_id in user_subscriptions and user_subscriptions[user_id].get("status") == "active":
            await query.edit_message_text(
                "✅ **Your membership is ACTIVE!**\n\nYou have full access to premium content!",
                parse_mode="Markdown",
                reply_markup=create_main_keyboard()
            )
        else:
            await query.edit_message_text(
                "❌ **No active membership found**\n\nPlease buy a membership to access premium content!",
                parse_mode="Markdown",
                reply_markup=create_main_keyboard()
            )
    elif query.data == "contact_admin":
        await query.edit_message_text(
            f"📞 **Contact Admin:** {ADMIN_USERNAME}\n\n"
            f"For:\n"
            f"• ₹400 discount coupon\n"
            f"• Payment verification\n"
            f"• Technical support\n\n"
            f"DM now! 💬",
            parse_mode="Markdown",
            reply_markup=create_main_keyboard()
        )

async def admin_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /approve USER_ID\n\nExample: /approve 7397173716")
        return
    
    user_id = context.args[0]
    user_subscriptions[user_id] = {
        "status": "active",
        "approved_at": datetime.now().isoformat()
    }
    
    await update.message.reply_text(f"✅ User {user_id} has been approved and given access!")
    
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text="✅ **ACCESS GRANTED!** ✅\n\nYour payment has been verified.\nYou now have full access to premium content!\n\nThank you for your purchase! 🎉",
            parse_mode="Markdown"
        )
    except:
        pass

async def admin_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    active_users = [uid for uid, data in user_subscriptions.items() if data.get("status") == "active"]
    
    if active_users:
        msg = "📊 **Active Subscriptions:**\n\n"
        for uid in active_users:
            msg += f"• `{uid}`\n"
        await update.message.reply_text(msg, parse_mode="Markdown")
    else:
        await update.message.reply_text("No active subscriptions found.")

# ============ MAIN ============

def main():
    from threading import Thread
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080, debug=False)).start()
    
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("approve", admin_approve))
    application.add_handler(CommandHandler("listusers", admin_list))
    application.add_handler(CallbackQueryHandler(handle_button_click))
    
    print("🤖 Bot is running!")
    print(f"✅ Bot token: {TOKEN[:10]}...")
    print(f"👑 Admin ID: {ADMIN_ID}")
    
    application.run_polling()

if __name__ == "__main__":
    main()