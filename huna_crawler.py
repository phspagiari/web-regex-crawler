import os
from datetime import datetime
import difflib
import StringIO
import re
from time import sleep

import requests
from twx.botapi import TelegramBot

BOT_API_TOKEN=os.getenv('BOT_API_TOKEN')
CYCLE_TIME=60
CHAT_ID=-185049465
LASTFILENAME_LOG='filename.log'
DATA={
    'hunahpus':{
        'url': "http://www.hunahpusday.com",
        'regexs': [
            'data-slb-asset="[0-9]+"',
            'SLB.View.assets, {"[0-9]+"',
            'Object Caching [0-9]+/[0-9]+ objects using disk',
            'Served from: hunahpusday.com @ (.*) by W3 Total Cache -->',
        ],
        'facebook_urls': [],
        'twitter_urls': []
    }
}


def telegram_bot(url, regexs):
    bot = TelegramBot(BOT_API_TOKEN)
    bot.update_bot_info().wait()
    print(bot.username)
    bot.send_message(CHAT_ID, "[%s] Bot Starting" % str(datetime.now())).wait()
    while (True):
        diff = diff_html(url, regexs)
        if diff:
            for diff_message in diff:
                ticket = ["Ticket", "ticket"]
                print diff_message
                for t in ticket:
                    print t
                    if t in diff_message:
                        bot.send_message(CHAT_ID, "TICKET WORD APPEARED IN A DIFF!!1111").wait()
                        sleep(2)
                        bot.send_message(CHAT_ID, "TICKET WORD APPEARED IN A DIFF!!1111").wait()
                bot.send_message(CHAT_ID, "Last updates:\n %s" % diff_message).wait()
        else:
            print("LOG: No diff")
        sleep(CYCLE_TIME)


def content_cleaner(content, regexs):
    for regex in regexs:
        content = re.sub(regex, '', content)
    return content


def download_html(url, regexs, write=False):
    request = requests.get(url)
    if request.status_code == 200:
        content = content_cleaner(content=request.content, regexs=regexs)
        if write:
            now = str(datetime.now())
            now = now.replace(" ", "_").replace(":", "-").split(".")[0]
            filename = "content_%s.html" % now
            write_to_file(filename, content)
            write_to_file(LASTFILENAME_LOG, filename)
        return content
    else:
        print("Something went wrong accessing the URL. Status Code: %s" % request.status_code)
        return "Error"


def write_to_file(file, data):
    with open(file, "w") as fp:
        fp.write(data)


def diff_html(url, regexs):
    try:
        with open(LASTFILENAME_LOG, "r") as fp:
            last_filename = fp.read()
    except IOError:
            print("First time running, creating a new file")
            download_html(url=url, regexs=regexs, write=True)
            with open(LASTFILENAME_LOG, "r") as fp:
                last_filename = fp.read()     
    try:
        with open(last_filename, "r") as fp:
            old_content = fp.read()
    except IOError:
            return "ERROR: FileNotFound %s" % last_filename

    new_content = download_html(url=url, regexs=regexs, write=False)
    new_content_buf = StringIO.StringIO(new_content)
    old_content_buf = StringIO.StringIO(old_content)
    diff = difflib.ndiff(new_content_buf.readlines(), old_content_buf.readlines())
    differences = []
    for line in diff:
        if line.startswith("-"):
            differences.append("Removed: %s" % line)
        elif line.startswith("+"):
            differences.append("Added: %s" % line)

    # GENERATE THE FILE FOR THE NEXT COMPARISON
    os.remove(last_filename)
    download_html(url=url, regexs=regexs, write=True)
    return differences


if __name__ == '__main__':
    telegram_bot(url=DATA['hunahpus']['url'], regexs=DATA['hunahpus']['regexs'])
