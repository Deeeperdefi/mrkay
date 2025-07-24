import logging
import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# --- Configuration ---
# It's best practice to use environment variables for sensitive data like bot tokens.
# On Render.com, you can set this in the 'Environment' section for your service.
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN')

# --- Logging Setup ---
# Enable logging to see errors and bot activity, which is helpful for debugging on Render.
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Data Storage (IMPORTANT NOTE) ---
# The following lists and dictionaries are stored in memory. This means all data,
# including who has registered and which keys are left, will be ERASED if the bot
# restarts. For a production bot on Render.com, you should use a persistent
# storage solution like a database (e.g., SQLite with a persistent disk, or a
# free-tier cloud database like ElephantSQL or Neon).

# List of unique keys to be distributed.
AIRDROP_KEYS = [
    "J7#kL9@mN2!pQ", "xY5$fT8&zR1*wP", "qW3^bV6%nM4#sX", "8K@dH5!jL9$rF2", "pE7&mU3*zT6#qY",
    "aB4$cN8!kO2%jI", "9X#gZ5@hP1&lK3", "rS6^vD2*wF7%mQ", "3L@kY9!tR5$jH8", "bN7%mW4#qV1&pX",
    "5T#fK8@jH2!lP6", "wQ3$dM7%nB4^vZ", "7G!kX5@mN9#rT2", "yV4&pL6*zH1%qW", "2J#bR8@cK5!sF9",
    "eD6$fN3%mP7^wQ", "8H@kL1!jM4$rB5", "sX7%vZ2*wK9#pY", "4F#gT6@hQ3!lR8", "nB5$cV9%mW2^jX",
    "1K@mY7!tP4$jH6", "qZ3&wD8*zF5%rS", "6L#bN9@kM2!sV4", "dR5$fH7%nJ1^wT", "9P!gX3@mQ6#rK8",
    "yW4&pB1*zL7%vN", "3T#jR5@cK8!sF2", "eM6$dN9%mP4^qV", "7H@kL2!jX5$rB8", "sZ1%vQ6*wK3#pY",
    "5F#gT7@hR4!lN9", "nV8$cW2%mX1^jB", "2K@mY6!tP9$jH3", "qD4&wZ7*zF8%rS", "8L#bN3@kM5!sV7",
    "dH1$fR6%nJ9^wT", "4P!gX2@mQ5#rK7", "yB8&pL3*zN6%vW", "1T#jR4@cK7!sF9", "eN5$dM8%mP2^qV",
    "6H@kL9!jX3$rB7", "sQ2%vZ5*wK8#pY", "3F#gT4@hR1!lN6", "nW7$cX9%mB2^jV", "9K@mY5!tP8$jH4",
    "qZ6&wD3*zF7%rS", "5L#bN2@kM4!sV8", "dR8$fH1%nJ6^wT", "2P!gX7@mQ3#rK5", "yB4&pL9*zN1%vW",
    "7T#jR3@cK6!sF8", "eM9$dN5%mP2^qV", "4H@kL8!jX1$rB6", "sQ5%vZ2*wK7#pY", "1F#gT9@hR4!lN3",
    "nW6$cX8%mB5^jV", "8K@mY4!tP7$jH2", "qD3&wZ9*zF6%rS", "6L#bN1@kM7!sV5", "dH2$fR5%nJ8^wT",
    "3P!gX6@mQ4#rK9", "yB7&pL2*zN5%vW", "9T#jR1@cK4!sF7", "eN8$dM3%mP6^qV", "5H@kL7!jX2$rB9",
    "sQ4%vZ1*wK6#pY", "2F#gT8@hR5!lN4", "nW3$cX7%mB9^jV", "7K@mY2!tP5$jH1", "qZ8&wD4*zF9%rS",
    "4L#bN6@kM3!sV8", "dR9$fH4%nJ7^wT", "1P!gX5@mQ2#rK6", "yB3&pL8*zN7%vW", "6T#jR9@cK2!sF5",
    "eM7$dN1%mP4^qV", "3H@kL6!jX9$rB2", "sQ8%vZ3*wK5#pY", "9F#gT1@hR6!lN7", "nW4$cX2%mB8^jV",
    "5K@mY8!tP3$jH7", "qD2&wZ6*zF1%rS", "7L#bN4@kM9!sV3", "dH5$fR8%nJ2^wT", "2P!gX9@mQ7#rK4",
    "yB6&pL1*zN3%vW", "8T#jR7@cK1!sF4", "eN3$dM6%mP9^qV", "4H@kL5!jX8$rB1", "sQ7%vZ4*wK2#pY",
    "1F#gT2@hR9!lN6", "nW5$cX1%mB7^jV", "6K@mY9!tP4$jH8", "qZ7&wD5*zF2%rS", "3L#bN8@kM6!sV1",
    "dR2$fH9%nJ5^wT", "9P!gX8@mQ1#rK3", "yB1&pL7*zN4%vW", "5T#jR6@cK9!sF2", "eM4$dN7%mP3^qV"
]

# Dictionary to store user information and prevent duplicate entries.
registered_users = {}

# --- Conversation States ---
NAME, SURNAME, EMAIL = range(3)

# --- Bot Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation when the user sends /start."""
    user_id = update.message.from_user.id

    if user_id in registered_users:
        await update.message.reply_text(
            "You have already received a key for this airdrop. "
            "Please wait for the next event!"
        )
        return ConversationHandler.END

    if not AIRDROP_KEYS:
        await update.message.reply_text(
            "Sorry, all airdrop keys have been claimed for this month. "
            "Please come back next month for a new airdrop!"
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "Welcome to the Airdrop Bot! To receive your token key, "
        "I need a few details from you.\n\n"
        "First, what is your name?\n\n"
        "You can send /cancel at any time to stop."
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the name and asks for the surname."""
    context.user_data['name'] = update.message.text
    logger.info(f"Name of user {update.message.from_user.id}: {update.message.text}")
    await update.message.reply_text(
        f"Great, {update.message.text}! Now, please tell me your surname."
    )
    return SURNAME

async def get_surname(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the surname and asks for the email."""
    context.user_data['surname'] = update.message.text
    logger.info(f"Surname of user {update.message.from_user.id}: {update.message.text}")
    await update.message.reply_text(
        "Thanks! Lastly, what is your email address?"
    )
    return EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the email, validates it, and distributes a key."""
    user_email = update.message.text
    user_id = update.message.from_user.id

    if '@' not in user_email or '.' not in user_email:
        await update.message.reply_text(
            "That doesn't look like a valid email address. Please try again."
        )
        return EMAIL

    context.user_data['email'] = user_email
    logger.info(f"Email of user {user_id}: {user_email}")

    if not AIRDROP_KEYS:
        await update.message.reply_text(
            "I'm very sorry, but it looks like the last key was just claimed while you were signing up. "
            "Please check back next month!"
        )
        return ConversationHandler.END

    # Distribute the key
    key = AIRDROP_KEYS.pop(0)
    user_data = context.user_data
    
    # Save the user's data permanently (in memory for this example)
    registered_users[user_id] = {
        "name": user_data['name'],
        "surname": user_data['surname'],
        "email": user_data['email'],
        "key": key
    }
    
    logger.info(f"User {user_id} ({user_data['name']}) has been given a key.")

    await update.message.reply_text(
        "Thank you for registering! You're all set.\n\n"
        "Here is your unique token password. Keep it safe!\n\n"
        f"🔑 `{key}` 🔑"
    )

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info(f"User {user.first_name} canceled the conversation.")
    await update.message.reply_text(
        "Registration canceled. You can start again by sending /start anytime."
    )
    context.user_data.clear()
    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    if TELEGRAM_BOT_TOKEN == 'YOUR_TELEGRAM_BOT_TOKEN':
        logger.error("Bot token not set! Please replace 'YOUR_TELEGRAM_BOT_TOKEN' or set the TELEGRAM_BOT_TOKEN environment variable.")
        return

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Setup conversation handler with states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_surname)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    # Start the Bot
    logger.info("Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()
