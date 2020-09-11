import subprocess
from credentials import BOT_TOKEN
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help_command(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def cpu_temp_check(update, context):
    bash_command = 'vcgencmd measure_temp'
    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    update.message.reply_text(output.decode("utf-8"))

def send_cpu_temp_msg(context):
    bash_command = 'vcgencmd measure_temp'
    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    job = context.job
    context.bot.send_message(job.context, text=output.decode("utf-8"))

def start_cpu_temp_check(update, context):
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    # args[0] should contain the time for the timer in seconds
    due = 10
    update.message.reply_text('Hourly CPU temp check on')

    # Add job to queue and stop current one if there is a timer already
    if 'cpu_check_job' in context.chat_data:
        old_job = context.chat_data['cpu_check_job']
        old_job.schedule_removal()
    new_job = context.job_queue.run_repeating(send_cpu_temp_msg, due, 1, context=chat_id)
    context.chat_data['cpu_check_job'] = new_job


def stop_cpu_temp_check(update, context):
    """Remove the job if the user changed their mind."""
    if 'cpu_check_job' not in context.chat_data:
        update.message.reply_text('You have no active CPU temperature check')
        return
    job = context.chat_data['cpu_check_job']
    job.schedule_removal()
    del context.chat_data['cpu_check_job']

    update.message.reply_text('Stopped checking CPU temperature!')


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(BOT_TOKEN, use_context=True)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("temp", cpu_temp_check))
    dp.add_handler(CommandHandler("start_cpu_check", start_cpu_temp_check,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("stop_cpu_check", stop_cpu_temp_check, pass_chat_data=True))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()