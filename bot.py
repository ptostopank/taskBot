from telegram import Bot
from telegram import Update
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import KeyboardButton
from telegram import chat
from telegram.ext import CallbackQueryHandler
from telegram.ext import ConversationHandler
from telegram.ext import Updater
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler
from telegram.ext import RegexHandler
import dataBase
import buttons

from config import TG_TOKEN

TITLE, BODY = range(2)
TASK_NAME = range(1)
TASK_NAME_EDIT, NEW_TASK_NAME, NEW_TASK_BODY = range(3)
TASK_NAME_COMPLETED = range(1)


def doStart_handler(update: Update, context: CallbackContext):
    reply_markup = buttons.getBaseKeyboard()    
    update.message.reply_text(
        text = "Hello!\nI am a bot to save your tasks",
        reply_markup=reply_markup,
        )


#ADD NEW TASK
def addNewTask_handler(update: Update, context: CallbackContext):
    update.message.reply_text(
        text = "Enter task name",
        reply_markup = ReplyKeyboardRemove(),
    )
    return TITLE
def title_handler(update: Update, context: CallbackContext):
    context.user_data[TITLE] = update.message.text
    if dataBase.getTaskForAdd(str(getChatId(update=update, context=context)),context.user_data[TITLE]):
        update.message.reply_text(
            text='Enter task description',
            reply_markup=ReplyKeyboardRemove(),
        )
        return BODY
    else:
        update.message.reply_text(
            text = "You already have such a task",
            reply_markup = buttons.getBaseKeyboard(),
        )
        return ConversationHandler.END

def finish_handler(update: Update, context: CallbackContext):
    context.user_data[BODY] = update.message.text
    dataBase.addTask(str(getChatId(update=update,context=context)), context.user_data[TITLE], context.user_data[BODY])
    update.message.reply_text(
        text = "Task added!",
        reply_markup=buttons.getBaseKeyboard(),
    )
    return ConversationHandler.END
def cancel_handler(update: Update, context: CallbackContext):  
    update.message.reply_text('')
    return ConversationHandler.END



#DELETE TASK
def deleteTask_handler(update: Update, context: CallbackContext):
    if dataBase.noneTask(str(getChatId(update=update,context=context))):
        update.message.reply_text(
            text = "Enter the name of the task you want to delete",
            reply_markup = ReplyKeyboardRemove(),
        )
        return TASK_NAME
    else:
        update.message.reply_text(
            text = "You have no tasks yet",
            reply_markup = buttons.getBaseKeyboard(),
        )

def taskName_handler(update: Update, context: CallbackContext):
    context.user_data[TASK_NAME] = update.message.text
    if dataBase.getTask(str(getChatId(update=update, context=context)),context.user_data[TASK_NAME]):
        dataBase.deleteTask(str(getChatId(update=update, context=context)), context.user_data[TASK_NAME])
        update.message.reply_text(
            text='Task deleted',
            reply_markup=buttons.getBaseKeyboard(),
        )
        return ConversationHandler.END
    else:
        update.message.reply_text(
            text='You dont have such a task',
            reply_markup=buttons.getBaseKeyboard(),
        )
        return ConversationHandler.END    


#EDIT TASK
def editTask_handler(update: Update, context: CallbackContext):
    if dataBase.noneTask(str(getChatId(update=update,context=context))):
        update.message.reply_text(
            text = "Enter the name of the task you want to editing",
            reply_markup = ReplyKeyboardRemove(),
        )
        return TASK_NAME_EDIT
    else:
        update.message.reply_text(
            text = "You have no tasks yet",
            reply_markup = buttons.getBaseKeyboard(),
        )
        
def newTaskName_handler(update: Update, context: CallbackContext):
    context.user_data[TASK_NAME_EDIT] = update.message.text
    if dataBase.getTask(str(getChatId(update=update, context=context)),context.user_data[TASK_NAME_EDIT]):
        update.message.reply_text(
            text = "Enter a new task name",
            reply_markup = ReplyKeyboardRemove(),
        )
        return NEW_TASK_NAME
    else:
        update.message.reply_text(
            text='You dont have such a task',
            reply_markup=buttons.getBaseKeyboard(),
        )
        return ConversationHandler.END      

def newTaskBody_handler(update: Update, context: CallbackContext):
    context.user_data[NEW_TASK_NAME] = update.message.text
    update.message.reply_text(
        text = "Enter a new task description",
        reply_markup = ReplyKeyboardRemove(),
    )
    return NEW_TASK_BODY     

def finish_edit_handler(update: Update, context: CallbackContext):
    context.user_data[NEW_TASK_BODY] = update.message.text
    dataBase.deleteTask(str(getChatId(update=update,context=context)), context.user_data[TASK_NAME_EDIT])
    dataBase.addTask(str(getChatId(update=update,context=context)),context.user_data[NEW_TASK_NAME],context.user_data[NEW_TASK_BODY])
    update.message.reply_text(
        text = "Task edited!",
        reply_markup=buttons.getBaseKeyboard(),
    )
    return ConversationHandler.END



#VIEW ALL TASKS
def viewAllTasks(update: Update, context: CallbackContext):
    if dataBase.noneTask(str(getChatId(update=update,context=context))):
        text = dataBase.viewAllTasks(str(getChatId(update=update,context=context)))
        new_list1 = []
        for k,v in text.items():
            new_list1.append(k + ":  " + v)
        update.message.reply_text(
            text = '\n'.join(new_list1),
            reply_markup=buttons.getBaseKeyboard(),
        )
    else:
        update.message.reply_text(
            text = "You have no tasks yet",
            reply_markup = buttons.getBaseKeyboard(),
        )    
    

#MARK TASK COMPLETED
def markTaskCompleted_handler(update: Update, context: CallbackContext):
    if dataBase.noneTask(str(getChatId(update=update,context=context))):
        update.message.reply_text(
            text = "Enter the name of the task you want to completed",
            reply_markup = ReplyKeyboardRemove(),
        )
        return TASK_NAME
    else:
        update.message.reply_text(
            text = "You have no tasks yet",
            reply_markup = buttons.getBaseKeyboard(),
        )      
def finishMark_handler(update: Update, context: CallbackContext):
    context.user_data[TASK_NAME_COMPLETED] = update.message.text
    if dataBase.getTask(str(getChatId(update=update, context=context)),context.user_data[TASK_NAME_COMPLETED]):
        if '✅' in dataBase.getBodyTask(str(getChatId(update=update,context=context)),context.user_data[TASK_NAME_COMPLETED]):
            update.message.reply_text(
            text='This task has already been completed!',
            reply_markup=buttons.getBaseKeyboard(),
        )
        else:
            textBody = (dataBase.getBodyTask(str(getChatId(update=update,context=context)),context.user_data[TASK_NAME_COMPLETED])+'✅')
            dataBase.setBodyTask(str(getChatId(update=update,context=context)),context.user_data[TASK_NAME_COMPLETED], textBody)
            update.message.reply_text(
                text='Task complet!',
                reply_markup=buttons.getBaseKeyboard(),
            )
        return ConversationHandler.END
    else:
        update.message.reply_text(
            text='You dont have such a task',
            reply_markup=buttons.getBaseKeyboard(),
        )
        return ConversationHandler.END  



def getChatId(update: Update, context: CallbackContext):
    text = update.message.chat_id
    return text
 

def messageHandler(update: Update, context: CallbackContext):
    reply_markup = buttons.getBaseKeyboard()
    text = update.message.text
    if text == buttons.button_viewAllTasks:
        return viewAllTasks(update=update, context=context)
    else:    
        update.message.reply_text(
            text = "I do not know such a command",
            reply_markup=reply_markup,
            )
   
    

def main():
    print("Start")
    updater = Updater(
        token=TG_TOKEN,
        use_context=True,
    )


    ud = updater.dispatcher

    addNewTask = ConversationHandler(
        entry_points=[MessageHandler(filters=Filters.text(buttons.button_newTask), callback=addNewTask_handler)],
        states={TITLE: [MessageHandler(Filters.text, title_handler, pass_user_data=True),],BODY: [MessageHandler(Filters.text, finish_handler, pass_user_data=True),],},
        fallbacks=[CommandHandler('cancel', cancel_handler),],
    )

    deleteTask = ConversationHandler(
        entry_points=[MessageHandler(filters=Filters.text(buttons.button_deleteTask), callback=deleteTask_handler)],
        states={TASK_NAME: [MessageHandler(Filters.text, taskName_handler, pass_user_data=True),],},
        fallbacks=[CommandHandler('cancel', cancel_handler),],
    )

    editTask = ConversationHandler(
        entry_points=[MessageHandler(filters=Filters.text(buttons.button_editTask), callback=editTask_handler)],
        states={TASK_NAME_EDIT: [MessageHandler(Filters.text, newTaskName_handler, pass_user_data=True),],NEW_TASK_NAME: [MessageHandler(Filters.text, newTaskBody_handler, pass_user_data=True),],NEW_TASK_BODY:[MessageHandler(Filters.text, finish_edit_handler, pass_user_data=True)]},
        fallbacks=[CommandHandler('cancel', cancel_handler),],
    )

    markTask = ConversationHandler(
        entry_points=[MessageHandler(filters=Filters.text(buttons.button_markTaskCompleted), callback=markTaskCompleted_handler)],
        states={TASK_NAME_COMPLETED: [MessageHandler(Filters.text, finishMark_handler, pass_user_data=True),],},
        fallbacks=[CommandHandler('cancel', cancel_handler),],
    )
    

    
    ud.add_handler(editTask)
    ud.add_handler(deleteTask)
    ud.add_handler(addNewTask)
    ud.add_handler(markTask)
    ud.add_handler(CommandHandler("start", callback=doStart_handler))
    ud.add_handler(MessageHandler(filters=Filters.text, callback=messageHandler))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()