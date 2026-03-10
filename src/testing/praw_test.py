import praw as pp
from praw.models import MoreComments as mc 
import pandas as pd
import time as tt
import winsound as ws

# im using the 'test' app in the reddit account
# can find the apps by going to reddit.com/prefs/apps 
# reddit made a new policy that only allows one OAuth key or app per account, so te 4021-30 account can only have 1 app

# current app is an 'installed app' type, should ask denis if can delete and create a script app instead
reddit = pp.Reddit( client_id = "s0Epgs8jsHkNKzsFGCnw-w",
                    client_secret = None,
                    redirect_uri="http://localhost:8080",
                    user_agent = "python:school_project:v1.0.0 (by u/4021-30)")

subreddits = [
    # main subreddits
    "soccer",
    "premierleague",
    "football",
    "theother14",

    # big clubs
    "reddevils",    # man u
    "LiverpoolFC",
    "gunners",      # arsenal
    "chelseafc",
    "MCFC",         # man city
    "coys",         # spurs
    
    # others
    "FantasyPL",
    "Championship",
    
    # diversity subreddits
    "realmadrid",
    "Barca",
    "fcbayern",
    "psg",
    "ACMilan",
]

"""
# test that it's working, get the 3 latest posts and their comments in r/soccer
for submission in reddit.subreddit("soccer").hot(limit=5):
    top_level_comments = list(submission.comments)
    allcomments = []

    for c in submission.comments:
        print(type(c))
        if (type(c) == mc):
            print("MORE COMMENT FOUND")
            continue
        allcomments.append(c.body)

    print("[\nsubmission info:\n" +
          " |upvotes     : " + str(submission.score) + "\n" + 
          " |upvote ratio: " + str(submission.upvote_ratio) + "\n" +
          " |author      : " + str(submission.author.name) + "\n" +
          " |author flair: " + str(submission.author_flair_text) + "\n" +
          " |subreddit   : " + str(submission.subreddit.display_name) + "\n" +
          " |title       : " + submission.title + "\n]")
    print("comments:\n")
    print(allcomments)
"""

startTime = tt.time()
# send the collected data into a csv, can use for classification in the classification.ipynb file
dfRows = []
commentCount = 0
postCount = 0
for sub in subreddits:
    postCount = 0
    for submission in reddit.subreddit(sub).new(limit=300):
        postCount += 1
        commentList = []
        print("r/{} post {}, total comments: {}".format(sub, postCount, commentCount))
        for c in submission.comments:
            commentCount += 1
            if (type(c) == mc):
                continue

            if (c.distinguished == "moderator"):
                print("skipping mod comment")
                commentCount -= 1
                continue

            commentList.append(c.body)

        tempRow = {
            "author"        : str(submission.author),
            "author_flair"  : submission.author_flair_text,
            "title"         : submission.title,
            "content"       : submission.selftext,
            "post_id"       : submission.id,
            "date"          : submission.created_utc,
            "upvotes"       : submission.score,
            "upvote_ratio"  : submission.upvote_ratio,
            "num_comments"  : submission.num_comments,
            "comments"      : commentList,
            "subreddit"     : submission.subreddit.display_name
        }
        dfRows.append(tempRow)

endTime = tt.time()
df = pd.DataFrame(dfRows)
ws.Beep(1000, 500)
print("found {} rows in {} seconds".format(len(df), round(endTime-startTime, 3)))

df.to_csv("reddit-scrape-data/data.csv", index = False)
