import os
import sys
import datetime
import copy
import requests
import json
from logging import getLogger, StreamHandler, DEBUG
import todoist
from exlist import ExList

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

def completedYesterday(item):
    completed_datetime = datetime.datetime.strptime(item['completed_date'], '%Y-%m-%dT%H:%M:%SZ')
    completed_datetime += datetime.timedelta(hours=9)
    now = datetime.datetime.now()
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    logger.debug('now:')
    logger.debug(now)
    logger.debug('completed:')
    logger.debug(completed_datetime)
    if yesterday < completed_datetime and completed_datetime < now:
        return True
    else:
        return False

def makeText(items):
    texts = ['・' + item['content'] for item in items if item is not None]
    today = datetime.datetime.now().strftime('%m/%d')
    if len(texts) == 0:
        return "No task completed on " + today + "\n"
    return 'On ' + today + ', you have completed these tasks!!\n' + '\n'.join(texts)

def sendSlackMessage(message):
    webhookurl = os.getenv("SLACK_URL","")
    try:
        requests.post(webhookurl, data = json.dumps({
        'text': message, # 投稿するテキスト
        'username': u'todoist-summary', # 投稿のユーザー名
        'link_names': 1, # メンションを有効にする
        }))
    except requests.exceptions.MissingSchema:
        sys.exit(1)


def main():
    key = os.getenv("TODOIST_TOKEN")
    if key is None:
        print("Environment Variable named $TODOIST_TOKEN doesn't exist!")
        sys.exit()

    api = todoist.TodoistAPI(key,'https://todoist.com',None,None)
    api.sync()
    items = ExList(api.completed.get_all()['items'])\
            .filter(completedYesterday)
    message = makeText(items)
    sendSlackMessage(message)

def exe(event, context):
    main()

if __name__ == '__main__':
    main()
