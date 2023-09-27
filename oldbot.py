import asyncio
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler
import boto3
import random


# Constants
TOKEN = '6326106440:AAHHS7rgUwuf85MOJJ0KlEI7glD5c-PaDrc'
BUCKET_NAME = 'telegramdorisbot'
IMAGE_FOLDER_PREFIX = 'dorispics/'
AWS_ACCESS_KEY_ID = 'AKIA2PKLHPIXQBBP4EEG'
AWS_SECRET_ACCESS_KEY = '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'

# Initialize Boto3 S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

async def start(update: Update, context):
    """Send a welcome message when the /start command is issued."""
    await update.message.reply_text('Hello! Send /photo to get a random image.')

async def get_random_image(update: Update, context):
    # List the objects in the "dorispics/" prefix of the S3 bucket
    response = s3_client.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix=IMAGE_FOLDER_PREFIX
    )

    # Get the list of image objects and filter out non-image files (like .DS_Store)
    images = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].lower().endswith(('.png', '.jpg', '.jpeg'))]

    if not images:
        await update.message.reply_text('No images found.')
        return

    # Randomly select an image
    selected_image = random.choice(images)

    # Generate a presigned URL for the selected image (valid for 1 hour)
    presigned_url = s3_client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': BUCKET_NAME,
            'Key': selected_image
        },
        ExpiresIn=3600
    )

    # Send the image to the user
    await update.message.reply_photo(photo=presigned_url)


async def main():
    """Start the bot."""
    # Create a bot instance
    bot_instance = Bot(TOKEN)
    
    # Create an asyncio queue for updates
    update_queue = asyncio.Queue()
    
    # Initialize the Updater with bot instance and queue
    updater = Updater(bot=bot_instance, update_queue=update_queue)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Register command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("photo", get_random_image))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    asyncio.run(main())  # This runs the async main function.