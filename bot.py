from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import boto3
import random
import logging
import os
from dotenv import load_dotenv
load_dotenv()

# Initialize logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Fetch environment variables
TOKEN = os.environ.get('TELEGRAM_TOKEN')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

# Constants
BUCKET_NAME = 'telegramdorisbot'
IMAGE_FOLDER_PREFIX = 'dorispics/'

# Initialize Boto3 S3 client
s3_client = boto3.client('s3',
                         aws_access_key_id=AWS_ACCESS_KEY_ID,
                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                         region_name='us-east-2')

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! Send /photo to see a random image of the big bear.')

def get_random_image(update: Update, context: CallbackContext) -> None:
    try:
        logger.info("Attempting to list objects in S3 bucket.")
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=IMAGE_FOLDER_PREFIX)
        #logger.info(f"S3 list_objects_v2 response: {response}")
        images = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].lower().endswith(('.png', '.jpg', '.jpeg'))]
        #logger.info(f"Images found: {images}")
        if not images:
            update.message.reply_text('No images found!')
            return
        
        random_image_key = random.choice(images)
        logger.info(f"Selected random image key: {random_image_key}")
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': random_image_key},
            ExpiresIn=3600  # URL validity duration in seconds
        )
        logger.info(f"Generated presigned URL: {presigned_url}")
        update.message.reply_photo(photo=presigned_url)
        
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        update.message.reply_text('An error occurred. Please try again later.')

# Initialize Updater
print(f"Token value: {TOKEN}")
updater = Updater(token=TOKEN, use_context=True)

# Add handlers
updater.dispatcher.add_handler(CommandHandler("start", start))
updater.dispatcher.add_handler(CommandHandler("photo", get_random_image))

# Start the Bot
updater.start_polling()


# Start the Bot
updater.start_polling()

