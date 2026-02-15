import praw as pp

# im using the 'test' app in the reddit account
# can find the apps by going to reddit.com/prefs/apps 
# reddit made a new policy that only allows one OAuth key or app per account, so te 4021-30 account can only have 1 app

# current app is an 'installed app' type, should ask denis if can delete and create a script app instead
reddit = pp.Reddit( client_id = "",
                    client_secret = "",
                    user_agent = "")

# test that it's working, get the 10 latest posts and their comments in r/soccer
for submission in reddit.subreddit("soccer").new(limit=10):
    top_level_comments = list(submission.comments)
    all_comments = submission.comments.list()
    print(submission.title)

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

