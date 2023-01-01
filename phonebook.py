from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import mytoken


lst_contacts = [["Иван", "+79993332244"],
                ["Петр", "+74442223311"], ["Алексей", "+74422231144"]]


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_split = update.message.text.split(" ")
    name = msg_split[1]
    phone_number = msg_split[2]
    lst_contacts.append([name, phone_number])
    print(lst_contacts)


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_split = update.message.text.split(" ")
    name = msg_split[1]
    for i in range(len(lst_contacts)):
        if name in lst_contacts[i]:
            lst_contacts.remove(lst_contacts[i])


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_split = update.message.text.split(" ")
    name = msg_split[1]
    for i in range(len(lst_contacts)):
        if name in lst_contacts[i]:
            await update.message.reply_text(" ".join(lst_contacts[i]))


async def print_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for i in range(len(lst_contacts)):
        await update.message.reply_text("\n ".join(lst_contacts[i]))


async def helpp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Добавить контакт - /add Имя, Номер\nУдалить контакт - /del Имя\nПоиск контакта - /search Имя\nВывод всех контактов - /print")

if __name__ == '__main__':
    app = ApplicationBuilder().token(mytoken.MYTOKEN).build()
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("del", delete))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CommandHandler("print", print_contacts))
    app.add_handler(CommandHandler("help", helpp))
    app.run_polling()
