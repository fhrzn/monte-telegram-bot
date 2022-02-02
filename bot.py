import os
import telegram
import logging
from telegram import Update, ParseMode
from telegram.ext import CallbackContext, Updater, CommandHandler
from tabulate import tabulate
from datetime import datetime

class Bot():
    def __init__(self) -> None:
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
        self.API_KEY = os.getenv('API_KEY')
        self.bot = telegram.Bot(token=self.API_KEY)
        self.updater = Updater(token=self.API_KEY, use_context=True)
        self.dispatcher = self.updater.dispatcher    
        self.dateformat = '%#d/%#m/%y'

    def _log_command(self, update):
        cmd = update.message.text.split(' ')[0]
        if cmd[0] == '/':
            logging.info('Received command: %s' % cmd)            
    
    def cmd_start(self, update: Update, context: CallbackContext):
        self._log_command(update)
        
        update.message.reply_text(
            "Hi! My name is Monte. I will help you record your income and outcome. Currently, I only have very limited features.\n"                        
        )
        update.message.reply_text(
            "To get started, just type /income or /outcome. See the example below:\n\n"
            "/outcome\n"
            "Coffee;999;MDR1\n\n"
            "Each word separated by ';' which represent value of columns BUY/RCV, PRC/AMT, and SRC/TRG."                        
        )
        update.message.reply_text(
            "Glossary:\n"
            "BUY: Outcome purpose\n"
            "RCV: Income source\n"
            "PRC: Outcome price\n"
            "AMT: Income amount\n"
            "SRC: Outcome source (bank card, e-money, etc.)\n"
            "TRG: Income target (bank card, e-money, etc.)"
        )

    def cmd_help(self, update: Update, context: CallbackContext):

        self._log_command(update)
        update.message.reply_text(
            "To get started, just type /income or /outcome. See the example below:\n\n"
            "/outcome\n"
            "Coffee;999;MDR1\n\n"
            "Each word separated by ';' which represent value of columns BUY/RCV, PRC/AMT, and SRC/TRG."                        
        )
        update.message.reply_text(
            "Glossary:\n"
            "BUY: Outcome purpose\n"
            "RCV: Income source\n"
            "PRC: Outcome price\n"
            "AMT: Income amount\n"
            "SRC: Outcome source (bank card, e-money, etc.)\n"
            "TRG: Income target (bank card, e-money, etc.)"
        )
    
    def cmd_income(self, update: Update, context: CallbackContext):

        self._log_command(update)
        
        # merge text
        raw_text = ' '.join(context.args)
        
        # error handling
        raw_text = raw_text[:-1] if raw_text[-1] == '/' else raw_text
        
        # get income from each line
        raw_income = raw_text.split('/')
        
        # transform to dictionary
        income = []
        
        for raw in raw_income:
            template = {}

            # split string by ';' separator
            sraw = raw.split(';')
            
            # insert each part of data
            template['DATE'] = datetime.now().strftime(self.dateformat)
            template['RCV'] = sraw[0]
            template['AMT'] = sraw[1]
            # template['CUR'] = sraw[2]     # Currency column, disabled for now            
            template['TRG'] = sraw[2]

            # insert to main list
            income.append(template)

        # TEMPORARY (need to integrate with Gsheet later)
        if 'income' in context.user_data:
            context.user_data['income'] += income
        else:
            context.user_data['income'] = income

        # send feedback response
        update.message.reply_text('Your income has been recorded.')

    def cmd_outcome(self, update: Update, context: CallbackContext):

        self._log_command(update)

        # merge text
        raw_text = ' '.join(context.args)

        # error handling
        raw_text = raw_text[:-1] if raw_text[-1] == '/' else raw_text
        
        # get outcome from each line
        raw_outcome = raw_text.split('/')
        
        # transform to list of dictionary
        outcome = []
        
        for raw in raw_outcome:            
            template = {}

            # split string by ';' separator
            sraw = raw.split(';')
            
            # insert each part of data
            template['DATE'] = datetime.now().strftime(self.dateformat)
            template['BUY'] = sraw[0]
            template['PRC'] = sraw[1]
            # template['CUR'] = sraw[2]     # Currency column, disabled for now
            template['SRC'] = sraw[2]
            

            # insert to main list
            outcome.append(template)

        # TEMPORARY (need to integrate with Gsheet later)
        if 'outcome' in context.user_data:
            context.user_data['outcome'] += outcome
        else:
            context.user_data['outcome'] = outcome        

        # send feedback response
        update.message.reply_text('Your outcome has been recorded.')

    def cmd_get_income(self, update: Update, context: CallbackContext):

        self._log_command(update)

        if 'income' in context.user_data and len(context.user_data['income']) > 0:
            income = context.user_data['income']
            
            # get table property
            header = list(income[0].keys())
            header = header[0] + header
            rows = [x.values() for x in income]            

            update.message.reply_text(f'```{tabulate(rows, header, tablefmt="pretty", stralign="left")}```', parse_mode=ParseMode.MARKDOWN_V2)
        else:
            logging.warn('Outcome record empty.')
            update.message.reply_text('Your income record is empty.')
    
    def cmd_get_outcome(self, update: Update, context: CallbackContext):

        self._log_command(update)

        if 'outcome' in context.user_data and len(context.user_data['outcome']) > 0:
            outcome = context.user_data['outcome']
            
            # get table property
            header = list(outcome[0].keys())            
            # header = header[:1] + header
            rows = [x.values() for x in outcome]            
            
            update.message.reply_text(f'```{tabulate(rows, header, tablefmt="pretty", stralign="left")}```', parse_mode=ParseMode.MARKDOWN_V2)            
        else:
            logging.warn('Outcome record empty.')
            update.message.reply_text('Your outcome record is empty.')

    def build(self):
        logging.info('Building bot...')
        start_handler = CommandHandler('start', self.cmd_start)        
        help_handler = CommandHandler('help', self.cmd_help)        
        income_handler = CommandHandler('income', self.cmd_income)
        outcome_handler = CommandHandler('outcome', self.cmd_outcome)        
        getincome_handler = CommandHandler('getincome', self.cmd_get_income)
        getoutcome_handler = CommandHandler('getoutcome', self.cmd_get_outcome)        
        
        logging.info('Adding dispatchers...')
        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(help_handler)
        self.dispatcher.add_handler(income_handler)
        self.dispatcher.add_handler(outcome_handler)        
        self.dispatcher.add_handler(getincome_handler)
        self.dispatcher.add_handler(getoutcome_handler)        

        logging.info('Build done!')

    def start(self):
        logging.info('Starting bot...')
        self.updater.start_polling()
        self.updater.idle()