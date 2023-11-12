import json
import threading
import datetime
import inspect
import telebot
from telebot import types
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP


"""
This tg bot use "data.json" to collect user_data (chat.id, message.text, date, time).
In "token.json" write your own telegram bot token.
"""


# Here we open json file with token
with open('token.json', 'r', encoding='utf-8') as json_token:
    py_token = json.load(json_token)
    token = py_token['TOKEN']

# Here we open json file with user_data
with open('data.json', 'w', encoding='utf-8') as user_data:
    json.dump({'remind_names': {}}, user_data, indent=2)

months = {
    '1': 'January',
    '2': 'February',
    '3': 'March',
    '4': 'April',
    '5': 'May',
    '6': 'June',
    '7': 'July',
    '8': 'August',
    '9': 'September',
    '10': 'October',
    '11': 'November',
    '12': 'December'
}
no_reply = True

bot = telebot.TeleBot(token)
print('-ONLINE-')


@bot.message_handler(commands=['start'])
def start(message):
    """
    Adds Reply buttons and send main info about bot
    """

    bot.delete_message(
        chat_id=message.chat.id,
        message_id=message.message_id,
        timeout=10
    )

    markup = types.InlineKeyboardMarkup()
    add_github_button = types.InlineKeyboardButton('🌐 Github', url='https://github.com/mynameniks')
    markup.add(add_github_button)

    markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    add_remind_reply = types.KeyboardButton('🔔 Add reminder')
    add_my_reply = types.KeyboardButton('📆 My reminders')
    add_delete_reply = types.KeyboardButton('🚫 Delete')
    add_datetime_reply = types.KeyboardButton('⏳ Change time')
    add_commands_reply = types.KeyboardButton('⚙️ Commands')
    markup_reply.add(
        add_remind_reply,
        add_my_reply,
        add_delete_reply,
        add_datetime_reply,
        add_commands_reply
    )

    bot.send_message(
        message.chat.id,
        '👋 *Sup!*\n'
        'I am bot *More*.',
        parse_mode='Markdown',
        reply_markup=markup_reply

    )

    bot.send_message(
        message.chat.id,
        'I will help you not to forget something important, '
        'or maybe not very important. '
        'Just write me, what and when I need to remind you, the rest of work is up to me.',
        parse_mode='Markdown',
        reply_markup=markup
    )

    @bot.callback_query_handler(func=lambda callback: callback.data == 'start_commands')
    def button_start_help(callback):
        """
        Runs 'commands' func
        """

        commands(callback.message)

    @bot.callback_query_handler(func=lambda callback: callback.data == 'start_remind')
    def button_start_remind(callback):
        """
        Runs 'set_remind' func
        """

        set_remind(callback.message)
        bot.delete_message(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            timeout=2
        )


@bot.message_handler(commands=['commands'])
def commands(message):
    """
    Sends a photo with the commands
    """

    bot.delete_message(
        chat_id=message.chat.id,
        message_id=message.message_id,
        timeout=10
    )

    markup = types.InlineKeyboardMarkup()
    add_destroy_button = types.InlineKeyboardButton('Click to delete', callback_data='commands_delete')
    markup.add(add_destroy_button)

    bot.send_photo(
        message.chat.id,
        'https://imgur.com/a/spj4rCK',
        reply_markup=markup
    )

    @bot.callback_query_handler(lambda callback: callback.data == 'commands_delete')
    def commands_delete(callback):
        """
        Deletes a photo with the commands
        """

        bot.delete_message(
            chat_id=message.chat.id,
            message_id=callback.message.message_id,
            timeout=2
        )


@bot.message_handler(commands=['remind'])
def set_remind(message):
    """
    Sets reminder name
    (also here 'no_reply' arg become 'False' to let 'text_handler' func get reminder name)
    """

    global no_reply
    no_reply = False

    bot.delete_message(
        chat_id=message.chat.id,
        message_id=message.message_id,
        timeout=10
    )

    bot.send_message(
        message.chat.id,
        'What i must remind you?'
    )

def set_remind_datetime(message):
    """
    Sets date and time of reminder
    (Check comments to see details)
    """

    # Here we create calendar (to set date)
    calendar, step = DetailedTelegramCalendar().build()

    bot.send_message(
        message.chat.id,
        f"Select date:",
        reply_markup=calendar
    )

    @bot.callback_query_handler(func=DetailedTelegramCalendar.func())
    def calendar(callback):
        """
        Works with calendar buttons
        """

        result, key, step = DetailedTelegramCalendar().process(callback.data)

        if not result and key:
            bot.edit_message_text(f"Select date:",
                                  callback.message.chat.id,
                                  callback.message.message_id,
                                  reply_markup=key)
        elif result:
            bot.delete_message(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                timeout=2
            )
            temp_date = str(result)

            # Here we create numpad (to set time)
            list_time = []
            markup = types.InlineKeyboardMarkup(row_width=3)

            add_1_button = types.InlineKeyboardButton(text='1', callback_data='time_1')
            add_2_button = types.InlineKeyboardButton(text='2', callback_data='time_2')
            add_3_button = types.InlineKeyboardButton(text='3', callback_data='time_3')
            add_4_button = types.InlineKeyboardButton(text='4', callback_data='time_4')
            add_5_button = types.InlineKeyboardButton(text='5', callback_data='time_5')
            add_6_button = types.InlineKeyboardButton(text='6', callback_data='time_6')
            add_7_button = types.InlineKeyboardButton(text='7', callback_data='time_7')
            add_8_button = types.InlineKeyboardButton(text='8', callback_data='time_8')
            add_9_button = types.InlineKeyboardButton(text='9', callback_data='time_9')
            add_0_button = types.InlineKeyboardButton(text='0', callback_data='time_0')
            add_remove_button = types.InlineKeyboardButton(text='<<', callback_data='time_<<')
            add_none_button = types.InlineKeyboardButton(text=' ', callback_data='none')
            add_ready_button = types.InlineKeyboardButton(text='Ready', callback_data='time_ready')

            markup.add(
                add_1_button,
                add_2_button,
                add_3_button,
                add_4_button,
                add_5_button,
                add_6_button,
                add_7_button,
                add_8_button,
                add_9_button,
                add_remove_button,
                add_0_button,
                add_none_button,
                add_ready_button
            )

            bot.send_message(
                message.chat.id,
                'Select time:',
                reply_markup=markup
            )

            @bot.callback_query_handler(func=lambda callback: callback.data.startswith('time_'))
            def button_time_callback(callback):
                """
                Works with numpad buttons
                """

                if len(list_time) == 2 and callback.data != 'time_<<':
                    list_time.append(':')

                if callback.data == 'time_<<':
                    if len(list_time) > 0:

                        if len(list_time) == 4:
                            list_time.pop(-1)
                        list_time.pop(-1)

                        bot.edit_message_text(
                            chat_id=callback.message.chat.id,
                            message_id=callback.message.message_id,
                            text=f'Select time: {''.join(list_time)}',
                            reply_markup=markup
                        )

                    else:
                        pass

                elif callback.data != 'time_ready' and len(list_time) < 5:
                    list_time.append(callback.data[-1])

                    bot.edit_message_text(
                        chat_id=callback.message.chat.id,
                        message_id=callback.message.message_id,
                        text=f'Select time: {''.join(list_time)}',
                        reply_markup=markup
                    )

                elif callback.data == 'time_ready':
                    temp_time = ''.join(list_time)
                    list_time.clear()

                    bot.delete_message(
                        chat_id=callback.message.chat.id,
                        message_id=callback.message.message_id,
                    )

                    # Here we check date and time and add a reminder to the dict
                    try:
                        remind_time = datetime.datetime.strptime(f'{temp_date} {temp_time}:10', '%Y-%m-%d %H:%M:%S')
                        current_time = datetime.datetime.now()
                        delta = remind_time - current_time

                        if delta.total_seconds() <= 0:
                            bot.send_message(
                                message.chat.id,
                                '❗️ This time has already passed, specify another!'
                            )
                            set_remind_datetime(message)

                        else:
                            date = ['%s' % remind_time.day, '%s' % remind_time.month, '%s' % remind_time.year]
                            time = ['%s' % remind_time.hour, '%s' % remind_time.minute]

                            for rep in range(2):
                                if int(date[rep]) < 10:
                                    date[rep] = '0' + date[rep]
                                if int(time[rep]) < 10:
                                    time[rep] = '0' + time[rep]

                            str_date = f'{date[0]} {months[date[1]]}, {'%s' % date[2]}'
                            str_time = f'{time[0]}:{time[1]}'

                            with open('data.json', 'r', encoding='utf-8') as user_data:
                                temp_data = json.load(user_data)
                            with open('data.json', 'w', encoding='utf-8') as user_data:
                                name = temp_data['remind_names'][str(message.chat.id)]
                                temp_data[str(message.chat.id)][name.lower()] = (str_date, str_time, name)
                                json.dump(temp_data, user_data, indent=2)

                            bot.send_message(
                                message.chat.id,
                                '📌 *All set!*',
                                parse_mode='Markdown'
                            )

                            bot.send_message(
                                message.chat.id,
                                f'*{temp_data[str(message.chat.id)][name.lower()][2]}*\n\n'
                                f' Date:\n_- {str_date}_\nTime:\n_- {str_time}_',
                                parse_mode='Markdown'
                            )

                            remind_timer = threading.Timer(
                                delta.total_seconds(),
                                send_remind,
                                [message.chat.id, message.text]
                            )

                            remind_timer.start()
                            with open('data.json', 'w', encoding='utf-8') as user_data:
                                del temp_data['remind_names'][str(message.chat.id)]
                                json.dump(temp_data, user_data, indent=2)

                    except ValueError:
                        bot.send_message(
                            message.chat.id,
                            '❗️ Incorrect date format!'
                        )
                        set_remind_datetime(message)


def send_remind(chat_id, remind_name):
    """
    Sends a reminder when timer is gone
    (Runs from 'remind_datetime' func)
    """

    with open('data.json', 'r', encoding='utf-8') as user_data:
        temp_data = json.load(user_data)

    if remind_name.lower() in temp_data[str(chat_id)]:
        bot.send_message(
            chat_id,
            f'❕ Hey, you asked me to remind:',
        )

        bot.send_message(
            chat_id,
            f'*{remind_name}*',
            parse_mode='Markdown',
            reply_markup=markup
        )

        with open('data.json', 'w', encoding='utf-8') as user_data:
            del temp_data[str(chat_id)][remind_name.lower()]
            json.dump(temp_data, user_data, indent=2)


@bot.message_handler(commands=['my'])
def my_reminders(message):
    """
    Sends message with all reminders
    """

    bot.delete_message(
        chat_id=message.chat.id,
        message_id=message.message_id,
        timeout=10
    )

    with open('data.json', 'r', encoding='utf-8') as user_data:
        temp_data = json.load(user_data)

    if (temp_data != {'remind_names': {}}) and (temp_data[str(message.chat.id)] != {}):
        amount = len(temp_data[str(message.chat.id)].keys())
        if amount == 1:
            text = f'{amount} reminder'
        else:
            text = f'{amount} reminders'

        bot.send_message(
            message.chat.id,
            '📌 *List of your reminders:*\n'
            f'_({text})_',
            parse_mode='Markdown'
        )

        for key in temp_data[str(message.chat.id)].keys():
            bot.send_message(
                message.chat.id,
                f'*{temp_data[str(message.chat.id)][key][2]}*\n\n'
                f'Date:\n_- {temp_data[str(message.chat.id)][key][0]}_'
                f'\nTime:\n_- {temp_data[str(message.chat.id)][key][1]}_',
                parse_mode='Markdown'
            )
    else:
        bot.send_message(
            message.chat.id,
            '❕ There is no reminders yet, but you can add one with command /remind'
        )


def get_reminds(message):
    """
    Returns markup with reply buttons with reminder names
    (Used for 'delete_remind' and 'datetime_remind' funcs)
    """

    with open('data.json', 'r', encoding='utf-8') as user_data:
        temp_data = json.load(user_data)

    markup = types.InlineKeyboardMarkup()

    if (temp_data != {'remind_names': {}}) and (temp_data[str(message.chat.id)] != {}):
        for char in temp_data[str(message.chat.id)].keys():
            if message.text == '🚫 Delete':
                remind_button = types.InlineKeyboardButton(
                    temp_data[str(message.chat.id)][char][2],
                    callback_data=f'delete_{temp_data[str(message.chat.id)][char][2]}'
                )
            else:
                remind_button = types.InlineKeyboardButton(
                    temp_data[str(message.chat.id)][char][2],
                    callback_data=f'datetime_{temp_data[str(message.chat.id)][char][2]}'
                )
            markup.add(remind_button)
        return markup
    else:
        bot.send_message(
            message.chat.id,
            '❕ There is no reminders yet, but you can add one with command /remind'
        )


@bot.message_handler(commands=['delete'])
def delete_remind(message):
    """
    Deletes remind from dict
    (this func use markup from 'get_remind' func)
    """

    bot.delete_message(
        chat_id=message.chat.id,
        message_id=message.message_id,
        timeout=10
    )

    markup = get_reminds(message)

    if markup is not None:
        bot.send_message(
            message.chat.id,
            'Choose remind to delete:',
            reply_markup=markup
        )

    @bot.callback_query_handler(func=lambda callback: callback.data.startswith('delete_'))
    def delete_remind_button(callback):
        with open('data.json', 'r', encoding='utf-8') as user_data:
            temp_data = json.load(user_data)
        with open('data.json', 'w', encoding='utf-8') as user_data:
            del temp_data[str(callback.message.chat.id)][callback.data[7:].lower()]
            json.dump(temp_data, user_data, indent=2)

        bot.send_message(
            callback.message.chat.id,
            f'Reminder deleted!'
        )

# Command to change date/time of reminder
@bot.message_handler(commands=['datetime'])
def datetime_remind(message):
    """
    Changes reminder date/time in dict
    (this func use markup from 'get_remind' func)
    """

    bot.delete_message(
        chat_id=message.chat.id,
        message_id=message.message_id,
        timeout=10
    )

    markup = get_reminds(message)

    if markup is not None:
        bot.send_message(
            message.chat.id,
            'Where change date/time?',
            reply_markup=markup
        )

    @bot.callback_query_handler(func=lambda callback: callback.data.startswith('datetime_'))
    def time_remind_button(callback):
        with open('data.json', 'r', encoding='utf-8') as user_data:
            temp_data = json.load(user_data)
        with open('data.json', 'w', encoding='utf-8') as user_data:
            del temp_data[str(callback.message.chat.id)][callback.data[9:].lower()]
            temp_data['remind_names'][str(message.chat.id)] = callback.data[9:]
            json.dump(temp_data, user_data, indent=2)

        set_remind_datetime(callback.message)

# Command - text handler
@bot.message_handler(content_types=['text'])
def text_handler(message):
    """
    Works with:
    'no_reply' var which we set in 'set_remind' func
    text from reply keyboard buttons
    everything else is deleted
    """

    global no_reply

    if no_reply is False:
        remind_name = message.text

        with open('data.json', 'r', encoding='utf-8') as user_data:
            temp_data = json.load(user_data)

        if str(message.chat.id) not in temp_data.keys():
            with open('data.json', 'w', encoding='utf-8') as user_data:
                temp_data[str(message.chat.id)] = {}
                json.dump(temp_data, user_data, indent=2)

        if remind_name.lower() in temp_data[str(message.chat.id)].keys():
            bot.send_message(
                message.chat.id,
                f'❗️ There is already such a reminder!'
            )

            bot.send_message(
                message.chat.id,
                f'*{temp_data[str(message.chat.id)][remind_name.lower()][2]}*\n\n'
                f'Дата:\n_- {temp_data[str(message.chat.id)][remind_name.lower()][0]}_\n'
                f'Время:\n_- {temp_data[str(message.chat.id)][remind_name.lower()][1]}_',
                parse_mode='Markdown'
            )
        else:
            with open('data.json', 'w', encoding='utf-8') as user_data:
                temp_data['remind_names'][message.chat.id] = remind_name
                json.dump(temp_data, user_data, indent=2)

            markup = types.InlineKeyboardMarkup(row_width=2)

            add_true_button = types.InlineKeyboardButton('Yep', callback_data='correct_true')
            add_false_button = types.InlineKeyboardButton('Nope', callback_data='correct_false')

            markup.add(
                add_true_button,
                add_false_button
            )

            bot.send_message(
                message.chat.id,
                f'Correct?',
                reply_markup=markup
            )

            @bot.callback_query_handler(lambda callback: callback.data.startswith('correct_'))
            def button_correct(callback):
                """
                handle callback from 'Yep' or 'Nope' buttons
                """

                if callback.data == 'correct_true':
                    set_remind_datetime(message)
                else:
                    with open('data.json', 'r', encoding='utf-8') as user_data:
                        temp_data = json.load(user_data)
                    with open('data.json', 'w', encoding='utf-8') as user_data:
                        del temp_data['remind_names'][str(message.chat.id)]
                        json.dump(temp_data, user_data, indent=2)
                    set_remind(message)

                bot.delete_message(
                    chat_id=message.chat.id,
                    message_id=callback.message.message_id,
                    timeout=2
                )
        no_reply = True

    else:
        # Here we handle text from buttons and start funcs
        if message.text == '🔔 Add reminder':
            set_remind(message)
        elif message.text == '📆 My reminders':
            my_reminders(message)
        elif message.text == '🚫 Delete':
            delete_remind(message)
        elif message.text == '⏳ Change time':
            datetime_remind(message)
        elif message.text == '⚙️ Commands':
            commands(message)
        else:
            bot.delete_message(
                chat_id=message.chat.id,
                message_id=message.message_id,
                timeout=10
            )


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
