import os
from environment import LOGS_DIR_PATH, BOT_CONFIG_PATH

import modules.support_functions as sup_f
from modules.data_presenter import DataPresenter
from telegram import Update, ForceReply, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    ConversationHandler
)

logger = sup_f.init_custome_logger(
    os.path.join(LOGS_DIR_PATH, 'all.log'),
    os.path.join(LOGS_DIR_PATH, 'error.log'),
)

CHAT_CONFIG = sup_f.get_config(BOT_CONFIG_PATH, 'CHAT')
DB_CONFIG = sup_f.get_config(BOT_CONFIG_PATH, 'DB')

data_presenter = DataPresenter(CHAT_CONFIG, DB_CONFIG)

# The layer for choosing an around
CHOOSING_AROUND = 0

# The layer for working with the menu of chosen around
CHOOSING_MAIN_MENU_ITEM = 1

# The layer for choosing stat group
CHOOSING_STAT_GROUP = 2

# The layer for choosing an item in selected stat group
CHOOSING_FLAT_TYPE, CHOOSING_RB_NAME = range(3, 5)

# The layer for choosing a sub item based on main item for displaying its data
CHOOSING_RB_NAME_BY_FLAT_TYPE, CHOOSING_FLAT_TYPE_BY_RB_NAME = range(5, 7)

# Constant text for displaying
TEXT_BACK = '🔙 Back'
TEXT_END = '🔚 End'
TEXT_ARROUNDS_REPORT = '📃 The report of all arounds'
TEXT_COMMON_STAT = '📊 The common statistics'
TEXT_NEW_STAT = '⚡ By the new flats relative to old ones'
TEXT_OLD_STAT = '⌛ By the old flats'
TEXT_SOLD_STAT = '💵 By the sold flats relative to old ones'
TEXT_GEN_SUM = 'ℹ General summary'
TEXT_STAT_BY_FLAT = '🔢 The stats by number of rooms'
TEXT_STAT_BY_RB = '🏘 The stats by residential complex'
TEXT_EACH_RB_ALL = '🏘 By all residential complexes'
TEXT_EACH_FLAT_TYPE_ALL = '🔢 By all numbers of rooms'


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [
        [TEXT_ARROUNDS_REPORT],
        data_presenter.get_arounds_names(),
        [TEXT_END]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard,
                                 input_field_placeholder='Chose around to see stat data...')

    update.message.reply_text(
        text='Use the keyboard and enjoy!',
        reply_markup=markup)

    return CHOOSING_AROUND


def arounds_cons_report(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        data_presenter.get_consolidation_arounds_report()
    )


def around_choice(update: Update, context: CallbackContext) -> int:
    # Setting arround in data_presenter
    data_presenter.set_current_around(update.message.text)

    update.message.reply_text(
        text=f'The around"{update.message.text}" has been chosen!',
        reply_markup=ReplyKeyboardMarkup([
            [TEXT_COMMON_STAT],
            [TEXT_NEW_STAT],
            [TEXT_OLD_STAT],
            [TEXT_SOLD_STAT],
            [TEXT_BACK]
        ], input_field_placeholder='Chose menu item...')
    )
    return CHOOSING_MAIN_MENU_ITEM


def back_from_around_main_menu(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [
        [TEXT_ARROUNDS_REPORT],
        data_presenter.get_arounds_names(),
        [TEXT_END]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard,
                                 input_field_placeholder='Chose around to see stat data...')

    update.message.reply_text(
        text='Chose menu item...',
        reply_markup=markup)

    return CHOOSING_AROUND


def around_cons_report(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        data_presenter.get_full_cons_report()
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def main_menu_item_choice(update: Update, context: CallbackContext) -> int:
    if update.message.text == TEXT_COMMON_STAT:
        stat_type = 'summary_stat'
    elif update.message.text == TEXT_NEW_STAT:
        stat_type = 'new_stat'
    elif update.message.text == TEXT_OLD_STAT:
        stat_type = 'old_stat'
    elif update.message.text == TEXT_SOLD_STAT:
        stat_type = 'sell_stat'
    else:
        update.message.reply_text(text='Unexpected input value')

    data_presenter.set_main_stat_type(stat_type)

    update.message.reply_text(
        text=data_presenter.get_cut_cons_report(),
        reply_markup=ReplyKeyboardMarkup([
            [TEXT_GEN_SUM],
            [TEXT_STAT_BY_FLAT, TEXT_STAT_BY_RB],
            [TEXT_BACK],
        ], input_field_placeholder='Chose menu item...')
    )

    return CHOOSING_STAT_GROUP


def back_from_main_menu_item(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        text='Chose menu item...',
        reply_markup=ReplyKeyboardMarkup([
            [TEXT_COMMON_STAT],
            [TEXT_NEW_STAT],
            [TEXT_OLD_STAT],
            [TEXT_SOLD_STAT],
            [TEXT_BACK]
        ], input_field_placeholder='Chose menu item...')
    )
    return CHOOSING_MAIN_MENU_ITEM


def count_flats_all_text(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        data_presenter.get_count_flats_all_text()
    )


def stat_by_flat_choise(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        text=data_presenter.get_count_flats_all_text(),
        reply_markup=ReplyKeyboardMarkup([
            [TEXT_EACH_FLAT_TYPE_ALL],
            data_presenter.get_flat_types(),
            [TEXT_BACK],
        ], input_field_placeholder='Chose menu item...')
    )

    return CHOOSING_FLAT_TYPE


def each_rb_all_text(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        data_presenter.get_each_rb_all_text()
    )


def stat_by_rb_choise(update: Update, context: CallbackContext) -> int:
    keyboard = []
    keyboard.append([TEXT_EACH_RB_ALL])
    for rb_name in data_presenter.get_rb_names():
        keyboard.append([rb_name])
    keyboard.append([TEXT_BACK])

    update.message.reply_text(
        text=data_presenter.get_each_rb_all_text(),
        reply_markup=ReplyKeyboardMarkup(keyboard, input_field_placeholder='Chose menu item...')
    )

    return CHOOSING_RB_NAME


def back_from_stat_by_chosen_group(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        text='Chose menu item...',
        reply_markup=ReplyKeyboardMarkup([
            [TEXT_GEN_SUM],
            [TEXT_STAT_BY_FLAT, TEXT_STAT_BY_RB],
            [TEXT_BACK],
        ], input_field_placeholder='Chose menu item...')
    )

    return CHOOSING_STAT_GROUP


def flat_type_choice(update: Update, context: CallbackContext) -> int:
    data_presenter.set_flat_type(update.message.text)

    keyboard = []
    keyboard.append([TEXT_EACH_RB_ALL])
    for rb_name in data_presenter.get_rb_names_by_selected_flat_type():
        keyboard.append([rb_name])
    keyboard.append([TEXT_BACK])

    update.message.reply_text(
        text=data_presenter.get_selected_flat_type_data(),
        reply_markup=ReplyKeyboardMarkup(keyboard, input_field_placeholder='Chose menu item...')
    )

    return CHOOSING_RB_NAME_BY_FLAT_TYPE


def each_rb_data_by_flat_type(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(data_presenter.get_each_rb_data_by_flat_type())


def rb_data_by_flat_type_choice(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        data_presenter.get_rb_data_by_flat_type(update.message.text)
    )


def flat_type_data_by_rb_name_choice(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        data_presenter.get_flat_type_data_by_rb_name(update.message.text)
    )


def back_from_rb_name_by_flat_type(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        text='Chose menu item...',
        reply_markup=ReplyKeyboardMarkup([
            [TEXT_EACH_FLAT_TYPE_ALL],
            data_presenter.get_flat_types(),
            [TEXT_BACK],
        ], input_field_placeholder='Chose menu item...')
    )

    return CHOOSING_FLAT_TYPE


def back_from_flat_type_by_rb_name(update: Update, context: CallbackContext) -> int:
    keyboard = []
    keyboard.append([TEXT_EACH_RB_ALL])
    for rb_name in data_presenter.get_rb_names():
        keyboard.append([rb_name])
    keyboard.append([TEXT_BACK])

    update.message.reply_text(
        text='Chose menu item...',
        reply_markup=ReplyKeyboardMarkup(keyboard, input_field_placeholder='Chose menu item...')
    )

    return CHOOSING_RB_NAME


def rb_name_choice(update: Update, context: CallbackContext) -> int:
    # update.message.reply_text(update.message.text)
    data_presenter.set_rb_name(update.message.text)

    keyboard = []
    keyboard.append([TEXT_EACH_RB_ALL])
    for rb_name in data_presenter.get_flat_types_by_selected_rb_name():
        keyboard.append([rb_name])
    keyboard.append([TEXT_BACK])

    update.message.reply_text(
        text=data_presenter.get_selected_rb_name_data(),
        reply_markup=ReplyKeyboardMarkup(keyboard, input_field_placeholder='Chose menu item...')
    )

    return CHOOSING_FLAT_TYPE_BY_RB_NAME


def each_flat_type_data_by_rb_name(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(data_presenter.get_each_flat_type_by_rb_name())


def end(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        '👋', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


if __name__ == '__main__':
    logger.info('RUN')

    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(CHAT_CONFIG['token'])

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_AROUND: [
                MessageHandler(
                    Filters.regex(f"^({'|'.join(data_presenter.get_arounds_names())})$"), around_choice
                ),
                MessageHandler(Filters.regex(f'^{TEXT_ARROUNDS_REPORT}$'), arounds_cons_report),
            ],
            CHOOSING_MAIN_MENU_ITEM: [
                MessageHandler(
                    Filters.regex(f'^({TEXT_COMMON_STAT}|{TEXT_NEW_STAT}|{TEXT_OLD_STAT}|{TEXT_SOLD_STAT})$'),
                    main_menu_item_choice),
                MessageHandler(Filters.regex(f'^{TEXT_BACK}$'), back_from_around_main_menu),
            ],
            CHOOSING_STAT_GROUP: [
                MessageHandler(Filters.regex(f'^{TEXT_GEN_SUM}$'), around_cons_report),
                MessageHandler(Filters.regex(f'^{TEXT_STAT_BY_FLAT}$'), stat_by_flat_choise),
                MessageHandler(Filters.regex(f'^{TEXT_STAT_BY_RB}$'), stat_by_rb_choise),
                MessageHandler(Filters.regex(f'^{TEXT_BACK}$'), back_from_main_menu_item)
            ],
            CHOOSING_FLAT_TYPE: [
                MessageHandler(Filters.regex(f'^{TEXT_EACH_FLAT_TYPE_ALL}$'), count_flats_all_text),
                MessageHandler(
                    Filters.regex(f"^({'|'.join(data_presenter.get_all_using_flat_types())})$"), flat_type_choice
                ),
                MessageHandler(Filters.regex(f'^{TEXT_BACK}$'), back_from_stat_by_chosen_group)
            ],
            CHOOSING_RB_NAME: [
                MessageHandler(Filters.regex(f'^{TEXT_EACH_RB_ALL}$'), each_rb_all_text),
                MessageHandler(
                    Filters.regex(f"^({'|'.join(data_presenter.get_all_using_rb_names())})$"), rb_name_choice
                ),
                MessageHandler(Filters.regex(f'^{TEXT_BACK}$'), back_from_stat_by_chosen_group)
            ],
            CHOOSING_RB_NAME_BY_FLAT_TYPE: [
                MessageHandler(Filters.regex(f'^{TEXT_EACH_RB_ALL}$'), each_rb_data_by_flat_type),
                MessageHandler(
                    Filters.regex(f"^({'|'.join(data_presenter.get_all_using_rb_names())})$"),
                    rb_data_by_flat_type_choice
                ),
                MessageHandler(Filters.regex(f'^{TEXT_BACK}$'), back_from_rb_name_by_flat_type)
            ],

            CHOOSING_FLAT_TYPE_BY_RB_NAME: [
                MessageHandler(Filters.regex(f'^{TEXT_EACH_FLAT_TYPE_ALL}$'), each_flat_type_data_by_rb_name),
                MessageHandler(
                    Filters.regex(f"^({'|'.join(data_presenter.get_all_using_flat_types())})$"),
                    flat_type_data_by_rb_name_choice
                ),
                MessageHandler(Filters.regex(f'^{TEXT_BACK}$'), back_from_flat_type_by_rb_name)
            ]

        },
        fallbacks=[MessageHandler(Filters.regex(f'^{TEXT_END}'), end)]
    )

    dispatcher.add_handler(conv_handler)

    dispatcher.add_handler(CommandHandler('help', help_command))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
