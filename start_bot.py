
CLIENT_ID = None
CLIENT_SECRET = None
USER_AGENT = None
REDDIT_USERNAME = None
REDDIT_PASSWORD = None

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT,
    username = REDDIT_USERNAME,
    password=REDDIT_PASSWORD
)

import time
import datetime
import random
import sys
import os
import traceback
import praw


from readwrite_bot import reddit

def hasBotCommentedOnPost(submission):
    for top_comment in submission.comments:
        if hasattr(top_comment,"author"):
            if top_comment.author.name == reddit.user.me().name:
                return True
    return False

def hasBotCommentedOnComment(comment):
    for second_comment in comment.replies:
        if hasattr(second_comment,"author"):
            if second_comment.author.name == reddit.user.me().name:
                return True
    return False

def hasCommentLimitReached(submission):
    comment_count = 0
    for top_comment in submission.comments:
        for second_comment in top_comment.replies:
            if hasattr(second_comment,"author"):
                if second_comment.author.name == reddit.user.me().name:
                    comment_count += 1
                    if comment_count >= COMMENT_LIMIT:
                        return True
    return False

def isMentionComment(comment):
    comment_txt = comment.body
    mention_words = ["uraharabot", "urahara bot"]
    return any([word in comment_txt.lower() for word in mention_words])


def postImage():
    account_username = reddit.user.me().name
    for submission in reddit.redditor(account_username).submissions.new(limit = 5):
        if True:
            date = datetime.datetime.fromtimestamp(submission.created_utc)
            dif = datetime.datetime.utcnow() - date
            if dif < datetime.timedelta(seconds=POST_FREQUENCY):
                return

            post_title = "Daily Dose of Urahara"
            random_image = "./urahara_art/" + random.choice([filename for filename in os.listdir("./urahara_art") if filename.lower().endswith("jpg") or filename.lower().endswith("png")])
            reddit.subreddit(SUBREDDIT_NAME).submit_image(post_title, random_image, flair_id = "a9a69882-6e92-11ec-8100-ce1e12c4bd6a")
            os.remove(random_image)
            printInfo("Image Post Made, File Removed: " + random_image)
            return


def monitorPosts():
    printInfo("Bot monitoring...")
    subreddit = reddit.subreddit(SUBREDDIT_NAME)
    visited = dict()
    update_frequency = 3600
    last_update = time.perf_counter()
    start_time = time.perf_counter()


    run_bot = True
    while run_bot:
        if len(visited) > 100:
            visited = dict()

        for submission in subreddit.new(limit = NO_SUBMISSIONS):
            submission.comments.replace_more(limit=None)
            dividor = "-------------------------------"
            post_title = submission.title
            for key_word in KEY_WORDS:
                if key_word in post_title.lower() and submission.id not in visited and submission.author.name != reddit.user.me().name:
                    if not hasBotCommentedOnPost(submission):
                        try:
                            response = returnResponse()
                            submission.reply(response)
                            addID(submission.id,visited)

                            printInfo("=======================================================")
                            printInfo("TITLE: {}".format(post_title) + "\n" + dividor)
                            printInfo("RESPONSE: {}".format(response) + "\n" + dividor)
                            printInfo("=======================================================")
                            time.sleep(WAIT_TIME)

                        except praw.exceptions.APIException as e:
                            printInfo("API Exception, bot resuming in {} secs...".format(WAIT_TIME))
                            time.sleep(WAIT_TIME)

                        except:
                            printInfo("Unexpected Exception, bot resuming in {} secs...".format(WAIT_TIME))
                            traceback.print_exc()
                            time.sleep(WAIT_TIME);

            for top_comment in submission.comments:
                comment_txt = top_comment.body
                if (not isMentionComment(top_comment) and hasCommentLimitReached(submission)):
                    continue
                #time.sleep(2)
                for key_word in KEY_WORDS:
                    if key_word in comment_txt.lower() and top_comment.id not in visited and top_comment.author.name != reddit.user.me().name:
                        if not hasBotCommentedOnComment(top_comment):
                            try:
                                response = returnResponse()
                                top_comment.reply(response)
                                addID(top_comment.id,visited)

                                printInfo("=======================================================")
                                printInfo("COMMENT: {}".format(comment_txt) + "\n" + dividor)
                                printInfo("RESPONSE: {}".format(response) + "\n" + dividor)
                                printInfo("=======================================================")
                                time.sleep(WAIT_TIME)

                            except praw.exceptions.APIException as e:
                                printInfo("API Exception, bot resuming in {} secs...".format(WAIT_TIME))
                                time.sleep(WAIT_TIME)

                            except:
                                printInfo("Unexpected Exception, bot resuming in {} secs...".format(WAIT_TIME))
                                traceback.print_exc()
                                time.sleep(WAIT_TIME);
        try:
            postImage()
        except:
            traceback.print_exc()

        time_since_update = time.perf_counter() - last_update
        if time_since_update > update_frequency:
            minutes_elapsed = str(int(time_since_update // 60))
            seconds_elapsed = str(int(time_since_update % 60))
            if len(seconds_elapsed) == 1:
                seconds_elapsed = "0" + seconds_elapsed
            time_str = minutes_elapsed + ":" + seconds_elapsed

            printInfo("Routine Update:")
            printInfo("Comments made over the last {} minutes: {}".format(time_str,len(visited)))
            last_update = time.perf_counter()


        if RUN_TIME == -1:
            continue
        else:
            curr_time = time.perf_counter()
            time_elapsed = curr_time - start_time
            run_bot = time_elapsed < RUN_TIME



def printInfo(output_str):
    print(output_str)
    sys.stdout.flush()

def addID(id_item,id_dict):
    id_item = str(id_item)
    if id_item in id_dict:
        return
    id_dict[id_item] = 0

def getAllLines(filename):
    all_lines = []
    with open(filename,mode="r",encoding="utf-8") as read_file:
        lines = read_file.readlines()
        for line in lines:
            all_lines.append(line.rstrip())
        read_file.close()
    return all_lines

def returnResponse():
    dividor = "=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n\n"
    bot_tag = "*beep boop, I'm a bot*"

    choice = random.randint(1,2)
    if choice <= 1:
        rand_index = random.randint(0,len(ALL_QUOTES)-1)
        rand_quote = ALL_QUOTES[rand_index]
        response = 'Urahara Quote No.{}: \n\n{}"{}" - Kisuke Urahara\n\n{}'.format(rand_index+1,dividor,rand_quote,bot_tag)
    else:
        rand_index = random.randint(0,len(ALL_FACTS)-1)
        rand_fact = ALL_FACTS[rand_index]
        response = 'Urahara Fact No.{}: \n\n{}{}\n\n{}'.format(rand_index+1,dividor,rand_fact,bot_tag)
    return response


QUOTES_FILENAME = "urahara_quotes.txt"
FACTS_FILENAME = "urahara_facts.txt"
ALL_QUOTES = getAllLines(QUOTES_FILENAME)
ALL_FACTS =  getAllLines(FACTS_FILENAME)


RUN_TIME = -1
SUBREDDIT_NAME = "bleach"
KEY_WORDS = ["urahara","kisuke"]
NO_SUBMISSIONS = 15
COMMENT_LIMIT = 5
POST_FREQUENCY = 3600 * 24
WAIT_TIME = 10

if __name__ == "__main__":
    ls = reddit.subreddit("test").flair.templates
    print(ls)
    """for submission in reddit.redditor("uraharaBot").submissions.new(limit = 5):
        if submission.title == "The incalculable schemer":
            print(isinstance(submission.link_flair_template_id,str))
            print(submission.link_flair_template_id)
            import pprint
            pprint.pprint(vars(submission))"""
    monitorPosts()