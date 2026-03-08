import praw as pp
import pandas as pd

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
for submission in reddit.subreddit("soccer").new(limit=3):
    top_level_comments = list(submission.comments)
    all_comments = submission.comments.list()
    print("[\nsubmission info:\n" +
          " |upvotes     : " + str(submission.score) + "\n" + 
          " |upvote ratio: " + str(submission.upvote_ratio) + "\n" +
          " |author      : " + str(submission.author.name) + "\n" +
          " |author flair: " + str(submission.author_flair_text) + "\n" +
          " |subreddit   : " + str(submission.subreddit.display_name) + "\n" +
          " |title       : " + submission.title + "\n]")
"""

# send the collected data into a csv, can use for classification in the classification.ipynb file
dfRows = []
for sub in subreddits:
    for submission in reddit.subreddit(sub).new(limit=20):
        tempRow = {
            "author": str(submission.author),
            "author_flair": submission.author_flair_text,
            "title": submission.title,
            "post_id": submission.id,
            "upvotes": submission.score,
            "upvote_ratio": submission.upvote_ratio,
            "num_comments": submission.num_comments,
            "subreddit" : submission.subreddit.display_name
        }
        dfRows.append(tempRow)

df = pd.DataFrame(dfRows)
print(df)

df.to_csv("reddit-scrape-data/temp.csv", index = False)
