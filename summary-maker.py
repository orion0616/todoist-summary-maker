import os
import sys
import datetime
import requests
import json

def completed_yesterday(item):
    completed_datetime = datetime.datetime.strptime(item['completed_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
    completed_datetime += datetime.timedelta(hours=9)
    now = datetime.datetime.now()
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    if yesterday < completed_datetime and completed_datetime < now:
        return True
    else:
        return False

def get_minutes(title):
    minutes = 0
    splitted = title.split(" ")
    for element in splitted:
        if element[0] != "@":
            continue
        if "2時間" in element:
            minutes += 120
        if "1時間" in element:
            minutes += 60
        if "30分" in element:
            minutes += 30
        if "15分" in element:
            minutes += 15
    return minutes

def summarize(items):
    minutes =0
    for item in items:
        if not completed_yesterday(item):
            continue
        minutes += get_minutes(item['content'])
    hours = minutes//60
    minutes -= hours*60
    return "Total time : " + str(hours) + " h " + str(minutes) + " m"

def makeText(projects, items):
    texts = []
    for item in items:
        if not completed_yesterday(item):
            continue
        message = " - "
        project_name = projects[item["project_id"]]["name"]
        if project_name is not None:
            message += '(' + project_name + ') '
        message += item['content']
        texts.append(message)
    today = datetime.datetime.now().strftime('%m/%d')
    if len(texts) == 0:
        return "No task completed on " + today + "\n"
    return 'On ' + today + ', you have completed these tasks!!\n' + '\n'.join(texts) + "\n\n" + summarize(items)

def sendSlackMessage(message):
    webhookurl = os.getenv("SLACK_URL","")
    try:
        r = requests.post(webhookurl, data = json.dumps({
        'text': message,
        'username': u'todoist-summary',
        'link_names': 1,
        }))

    except requests.exceptions.MissingSchema:
        sys.exit(1)


def main():
    token = os.getenv("TODOIST_TOKEN")
    if token is None:
        print("Environment Variable named $TODOIST_TOKEN doesn't exist!")
        sys.exit()

    url = "https://api.todoist.com/sync/v9/completed/get_all"
    headers = { "Authorization" : "Bearer {}".format(token) }
    data = {"limit" : 100}

    res = requests.get(url, headers = headers, params = data).json()
    items = res["items"]
    projects = res["projects"]
    message = makeText(projects, items)
    sendSlackMessage(message)

def exe(event, context):
    main()

if __name__ == '__main__':
    main()
