import os
import logging
from datetime import datetime
import random
import string
import io
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
PRIVATE_CHANNEL_ID = os.getenv('PRIVATE_CHANNEL_ID')
GATE_LOG_CHANNEL = os.getenv('GATE_LOG_CHANNEL_ID')
SUCCESS_LOG_CHANNEL = os.getenv('SUCCESS_LOG_CHANNEL_ID')

# Customization settings with defaults
CAPTCHA_LENGTH = int(os.getenv('CAPTCHA_LENGTH', '4'))
DISTORTION_LINES = int(os.getenv('DISTORTION_LINES', '8'))
INVITE_EXPIRE_MINUTES = int(os.getenv('INVITE_EXPIRE_MINUTES', '60'))

# Store user captcha data temporarily
user_captcha = {}
user_current_input = {}

def generate_captcha_image(text, width=400, height=100):
    # Create image with white background
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Draw random lines through letters (customizable amount)
    for _ in range(DISTORTION_LINES):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line([(x1, y1), (x2, y2)], fill='black', width=2)
    
    # Draw text
    font_size = 60
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Calculate text position to center it
    text_width = draw.textlength(text, font=font)
    x = (width - text_width) // 2
    y = (height - font_size) // 2
    
    # Draw each character with slight random offset
    for i, char in enumerate(text):
        char_x = x + i * (text_width / len(text))
        char_y = y + random.randint(-10, 10)
        draw.text((char_x, char_y), char, font=font, fill='black')
    
    # Convert to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

def create_keyboard(captcha_text):
    # Create a set of available characters (including captcha characters)
    available_chars = set(captcha_text.upper())
    # Add some random characters
    while len(available_chars) < max(12, CAPTCHA_LENGTH * 3):  # At least 3x the captcha length
        available_chars.add(random.choice(string.ascii_uppercase + string.digits))
    
    # Convert to list and shuffle
    chars = list(available_chars)
    random.shuffle(chars)
    
    # Create keyboard layout (3 rows of 4 buttons)
    keyboard = []
    for i in range(0, len(chars), 4):
        row = [InlineKeyboardButton(c, callback_data=f"char_{c}") for c in chars[i:i+4]]
        keyboard.append(row)
    
    # Add Clear and Submit buttons
    keyboard.append([
        InlineKeyboardButton("🔄 Clear", callback_data="clear"),
        InlineKeyboardButton("✅ Submit", callback_data="submit")
    ])
    
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Log new user attempt in gate log channel
    await context.bot.send_message(
        chat_id=GATE_LOG_CHANNEL,
        text=f"🚪 New user at gate:\nID: {user.id}\nUsername: @{user.username}\nName: {user.first_name}"
    )
    
    keyboard = [
        [InlineKeyboardButton("I'm not a robot", callback_data="verify")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Welcome to the Gate Bot! 🚪\n\n"
        f"To get access to the private channel, you'll need to verify you're human.\n"
        f"Click the button below to start the verification process.",
        reply_markup=reply_markup
    )

async def verify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    
    await query.answer()
    
    # Generate new captcha with customizable length
    captcha = ''.join(random.choices(string.ascii_uppercase, k=CAPTCHA_LENGTH))
    user_captcha[user.id] = captcha
    user_current_input[user.id] = ""
    
    # Generate and send captcha image
    captcha_image = generate_captcha_image(captcha)
    keyboard = create_keyboard(captcha)
    
    await query.message.delete()
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=InputFile(captcha_image, filename='captcha.png'),
        caption=f"Select the characters you see in the image.\nCurrent input: ",
        reply_markup=keyboard
    )

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    
    if user.id not in user_captcha:
        await query.answer("Session expired. Please start over.", show_alert=True)
        return
    
    await query.answer()
    data = query.data
    
    if data.startswith("char_"):
        char = data.split("_")[1]
        current = user_current_input.get(user.id, "") + char
        # Limit input to captcha length
        if len(current) <= CAPTCHA_LENGTH:
            user_current_input[user.id] = current
    elif data == "clear":
        current = ""
        user_current_input[user.id] = current
    elif data == "submit":
        if user_current_input.get(user.id) == user_captcha[user.id]:
            try:
                # Create a single-use invite link with customizable expiration
                invite_link = await context.bot.create_chat_invite_link(
                    chat_id=PRIVATE_CHANNEL_ID,
                    member_limit=1,
                    expire_date=int((datetime.now().timestamp() + INVITE_EXPIRE_MINUTES * 60)),
                    creates_join_request=False
                )
                
                # Log successful verification
                await context.bot.send_message(
                    chat_id=SUCCESS_LOG_CHANNEL,
                    text=f"✅ User verified successfully:\nID: {user.id}\nUsername: @{user.username}\nName: {user.first_name}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nInvite Link: {invite_link.invite_link}"
                )
                
                # Send invite link with button
                keyboard = [[InlineKeyboardButton("Join Channel 🚀", url=invite_link.invite_link)]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.message.delete()
                # Format minutes into hours and minutes for display
                time_str = (
                    f"{INVITE_EXPIRE_MINUTES} minute{'s' if INVITE_EXPIRE_MINUTES != 1 else ''}"
                    if INVITE_EXPIRE_MINUTES < 60
                    else f"{INVITE_EXPIRE_MINUTES // 60} hour{'s' if INVITE_EXPIRE_MINUTES // 60 != 1 else ''} "
                         f"and {INVITE_EXPIRE_MINUTES % 60} minute{'s' if INVITE_EXPIRE_MINUTES % 60 != 1 else ''}"
                )
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"✅ Verification successful! Here's your unique invite link:\n{invite_link.invite_link}\n\n"
                         f"⚠️ Note: This link will expire in {time_str} and can only be used once!",
                    reply_markup=reply_markup
                )
                
                # Clean up
                del user_captcha[user.id]
                del user_current_input[user.id]
                return
                
            except Exception as e:
                logger.error(f"Error creating invite link: {e}")
                await query.message.edit_caption(
                    caption="❌ Sorry, there was an error generating your invite link. Please try again later or contact an administrator."
                )
                return
        else:
            await query.message.delete()
            keyboard = [[InlineKeyboardButton("Try Again", callback_data="verify")]]
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Incorrect captcha. Please try again.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return
    
    # Update message with current input
    keyboard = create_keyboard(user_captcha[user.id])
    await query.message.edit_caption(
        caption=f"Select the characters you see in the image.\nCurrent input: {user_current_input[user.id]}",
        reply_markup=keyboard
    )

def main():
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(verify_callback, pattern="^verify$"))
    application.add_handler(CallbackQueryHandler(handle_button, pattern="^(char_|clear|submit)"))

    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
