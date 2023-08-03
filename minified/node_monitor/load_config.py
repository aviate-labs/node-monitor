import os
from dotenv import load_dotenv

load_dotenv()


##############################################
## Secrets

gmailUsername    = os.environ.get('gmailUsername'  )
gmailPassword    = os.environ.get('gmailPassword'  )
discordBotToken  = os.environ.get('discordBotToken')  # Not implemented
slackBotToken    = os.environ.get('slackBotToken'  )



##############################################
## Default Config
## TODO: Give this an override that node providers can tune

defaultConfig = {
    'NotifyByEmail'             : True,
    'NotifyBySlack'             : False,
    'NotifyByTelegramChannel'   : False,
    'NotifyByTelegramChat'      : False,
}
