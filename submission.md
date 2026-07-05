# Detailed Overview of Mixtape Starter
## AI usage
### AI Assistance Instance #1
Task: Generate an initial architecture diagram and API flow for the submission and appeal endpoints.

Output Used: ASCII diagrams illustrating the POST /submit and POST /appeal workflows.

Your Revisions: Updated the diagrams to match the final implementation, including the Groq classifier, stylometric heuristics, confidence scoring, transparency labels. 

### AI Assistance Instance #2
Task: Generate function to create logging SQLite 

Output Used: Python code generated for basic logging CRUD. 

Your Revisions: Modified some of the SQL statements to improve column naming, and added a delete logs for easier testing.
## Codebase Map
```
ai201-project5-mixtape-starter/
├── app.py                      # Flask app factory and DB setup
├── models.py                   # SQLAlchemy models for all entities
├── routes/
│   ├── songs.py                # Song sharing, search, and rating routes
│   ├── playlists.py            # Playlist creation and song management
│   ├── users.py                # User profiles, streaks, notifications
│   └── feed.py                 # Friends listening now, activity feed
├── services/
│   ├── streak_service.py       # Listening streak logic
│   ├── feed_service.py         # Friends listening now feed logic
│   ├── search_service.py       # Song search logic
│   ├── notification_service.py # Notification creation and retrieval
│   └── playlist_service.py     # Playlist retrieval logic
├── tests/
│   ├── test_streaks.py
│   ├── test_search.py
│   └── test_playlists.py
├── seed_data.py                # Populates DB with test data
├── requirements.txt
└── .gitignore
```
### **`models.py`**
---

It defines the SQLAlchemy data model for the Mixtape app.

Core entities include:

- User: stores account info, streak data, friendships, playlists, ratings, and notifications.
- Song: represents shared music with metadata and tags.
- ListeningEvent: records when a user listens to a song.
- Rating: stores a user’s score for a song, with a uniqueness constraint so one user can rate a song once.
- Playlist: holds a collection of songs and who created it.
- Notification: stores alerts for users.
- Tag: represents song tags.

It also defines association tables for:
- friendships between users
- song tags


### **`/services`** files
---
| File name | Description | Example Functionality |
| -- | -- | -- |
| streak_service.py | Tracks and updates a user's listening streak based on recent listening activity. | Increment a streak after consecutive days of listening or reset it after a skipped day. |
| feed_service.py | Builds the friends listening feed and general activity feed from recent listening events. | Show which friends listened recently and what song they played. |
| search_service.py | Searches songs by title or artist and returns matching results. | Find all songs related to a query like "Adele". |
| notification_service.py | Creates and retrieves notifications for social actions such as playlist additions and song ratings. | Notify a song sharer when someone adds their song to a playlist. |
| playlist_service.py | Creates playlists and returns the songs in a playlist in the correct order. | Retrieve all songs in a playlist, including the last one added. |

---

### **`/routes`** files
---
| File name | Description | Example Functionality |
| -- | -- | -- |
| songs.py | Handles song-related endpoints for searching, viewing details, rating, and listening events. | Search songs by query, view a specific song, or record that a user listened to a song. |
| playlists.py | Handles playlist endpoints for creating playlists, viewing playlist details, listing songs, and adding songs. | Create a new playlist or add a song to an existing one. |
| users.py | Handles user profile and notification-related endpoints, including streaks and read/unread notifications. | Get a user's profile, view their streak, or mark a notification as read. |
| feed.py | Handles feed endpoints for showing friends who are listening now and recent activity. | View a user's friends listening feed or general activity feed. |

### Dataflow for Song Search

User searches for a song through the following get request `GET /songs/search?q=adele` in `routes/songs.py ` calls `search_songs(query)`. This  function assembles a query that looks for a song title or artist with a (case-insensitive partial) match in the Songs/Song Tags outerjoined table. It returns the songs that match in a dictionary. 

### Data Flow for Read Notification
A user marks a notification as read by making a POST request `POST /users/notifications/{notification_id}/read` in `users.py`, which calls mark_as_read(notification_id). This function retrieves the notification from the database by ID, sets its read field to True, and commits the change to the database.

Pattern I noticed: every route delegates immediately to a service function. The routes do input parsing and response formatting; all business logic lives in `services/`.

## Bug Fixes Analysis
<!-- what inputs, what sequence of actions, or what data condition triggered the behavior. This is part of your root cause analysis entry -->
## Issue #1: My listening streak keeps resetting
**1. Issue Reproduction**
The issue of a streak resetting is illustrated in the `test_streak_increments_on_sunday(app, user)` function in `tests/test_streaks.py`. The input with the data of comparsion to increase the streak on Sunday produces this incorrect behavior. Anytime the GET endpoint is run for a user's streak this behavior is observed. 
```python
def test_streak_increments_on_sunday(app, user):
    """
    Listening on Saturday and then Sunday should increment the streak.
    """
    with app.app_context():
        u = db.session.get(User, user.id)
        saturday = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)  # weekday() == 5
        sunday = datetime(2024, 6, 16, 12, 0, 0, tzinfo=timezone.utc)    # weekday() == 6

        update_listening_streak(u, saturday)
        assert u.listening_streak == 1

        update_listening_streak(u, sunday)
        assert u.listening_streak == 2  # Should increment, not reset

```

**2. How the root cause was found**
<!-- Which files did you look at? What was your navigation path? What moment made you confident you'd found the right place — not just a suspicious area, but the specific cause? -->
*Navigation path*: In `routes/users.py` the `streak(user_id)` function, took me to  `get_streak(user_id: str)` in `services/streak_service.py`. Here, I analyzed the function to check how streaks were updated. 

*Correct spot*: I read through the docstring at the top of them method, and identified the path relating to the issue was "If more than one day has passed: streak resets to 1" since the issue directly mentions resetting as the man issue. This meant that some condition that over a day has passed was incorrectly being met. Somewhere were the listening_streak was set to 1 was the exact location of the issue. 

**3. The root cause**
<!-- In plain English, explain exactly what was wrong. Not "there was a bug in the streak logic" — explain the specific condition, comparison, or missing step that caused the problem. -->
The following condition was the issue
```python
if days_since_last == 0:
        return
    ## specifically today.weekday() 
    elif days_since_last == 1 and today.weekday() != 6:
        user.listening_streak += 1
    else:
        user.listening_streak = 1
```
This was a logic error because today.weekday() on Sunday was 6. Thus, no matter if the streak was maintained or now, on Sunday the streak would always be reset. 

**4. Fix and Side-effect Check**
 <!-- What did you change and why does that change fix the root cause? What related functionality did you check afterward to confirm you didn't break anything? -->
 To fix this issue, I removed the `today.weekday() != 6` from the elif statement. This fails in line with the expected behavior of python's `.weekday()` method where the day of the week has mon=0 and sunday=6 which doesn't matter to the streak calculation here. 

 To ensure functionality elsewhere was not broken, I wrote another test to ensure that sunday -> monday streaks were incremented appropriately. Below is the test
``` python
def test_streak_increments_on_monday(app, user):
    """
    Listening on Sunday and then Monday should increment the streak.
    """
    with app.app_context():
        u = db.session.get(User, user.id)
        sunday = datetime(2024, 6, 16, 12, 0, 0, tzinfo=timezone.utc)  # weekday() == 6
        monday = datetime(2024, 6, 17, 12, 0, 0, tzinfo=timezone.utc)  # weekday() == 7

        update_listening_streak(u, sunday)
        assert u.listening_streak == 1

        update_listening_streak(u, monday)
        assert u.listening_streak == 2  # Should increment, not reset
```
All 5 including the newly added test above passed. 

## Issue #3: The same song keeps showing up twice in search
**1. Issue Reproduction**
<!-- What steps did you take to confirm the bug exists before touching any code? What inputs, sequence of actions, or data condition triggered the behavior? -->
Initially, when I ran the search tests all of them passed. I looked through seed_data.py to see how the songs were added. I also examined the search functions (especially ` search_songs(query: str)` in `service/search_service.py`). The issue was produced by querying both tables Song, and the tag_id column from Song_tags. The following test from the given test suite now fails

```python
def test_search_no_duplicates_multi_tag_song(app, seed_songs):
    """
    A song with multiple tags should appear exactly once in search results.
    """
    with app.app_context():
        results = search_songs("Crown Heights")
        matching = [r for r in results if r["title"] == "Crown Heights Anthem"]
        assert len(matching) == 1  # Should be 1, bug causes it to be 3
```

**2. How the root cause was found**
<!-- Which files did you look at? What was your navigation path? What moment made you confident you'd found the right place — not just a suspicious area, but the specific cause? -->
*Navigation Path*: I started with `search()` in `routes/songs.py` which calls `def search_songs(query: str) -> list[dict]` in `service/search_service.py`. 

*Correct Spot*: I examined the method and realized the culprit here was how the queries of the 2 tables (Song and Tags) was handled. Duplicate enteries meant that the search with % was corrected, but somehow multiple rows were being pulled when joining the tables in the query. 

**3. The root cause**
<!-- In plain English, explain exactly what was wrong. Not "there was a bug in the streak logic" — explain the specific condition, comparison, or missing step that caused the problem. -->
The rootcause is the outerjoin which leads to the raw SQL query to produce a row for each tag instead of just 1 row per song id. Outerjoin in SQL leads to duplicate rows being pulled.

**4. Fix and side-effect check**
 <!-- What did you change and why does that change fix the root cause? What related functionality did you check afterward to confirm you didn't break anything? -->
 I simplified the query by only searching through the Song table. The tags aren't useful for the search, so a query without them would be more effecient. The fix is below:

```python
results = (
        db.session.query(Song) # we only need to query Song
        ## removed the outerjoin here 
        .filter(
            db.or_(
                Song.title.ilike(f"%{query}%"),
                Song.artist.ilike(f"%{query}%"),
            )
        )
        .all()
    )

    return [song.to_dict() for song in results]
```

 To ensure overall functionality, I ran the test suite and all the tests did pass. 

---
## Issue #4: I got notified when a friend added my song to a playlist but not when they rated it
**1. Issue Reproduction**
<!-- What steps did you take to confirm the bug exists before touching any code? What inputs, sequence of actions, or data condition triggered the behavior? -->
I saw there were no tests for notifications. So, I created `tests/test_notify.py` with the following function. I inputed a new rating and then checked the notification table for a new entry. The mocked table was empty which demonstrates that no notification was fired. 

```python
def test_rate_song_notifies_song_sharer(app, seed_data):
    """
    Rating another user's song should notify the user who originally shared it.
    """
    with app.app_context():
        owner = seed_data["owner"]
        rater = seed_data["rater"]
        song = seed_data["song"]

        rate_song(
            user_id=rater.id,
            song_id=song.id,
            score=5,
        )

        notifications = Notification.query.filter_by(
            user_id=owner.id,
            notification_type="song_rated",
        ).all()

        assert len(notifications) == 1
        assert rater.username in notifications[0].body
        assert song.title in notifications[0].body
```

**2. How the root cause was found**
<!-- Which files did you look at? What was your navigation path? What moment made you confident you'd found the right place — not just a suspicious area, but the specific cause? -->
*Navigation*: I started in `routes/songs.py` with the `def rate(song_id)` function. This traced to a function called `def rate_song(user_id: str, song_id: str, score: int) -> Rating:` in `services/notification_service.py`. 

*Correct Spot*: I also looked at the structure of add_to_playlist since it follows a similar pattern of intial checks like verifying the originator of the song and the issuing a notification to the recommender. I noticed that this was missing in the rating function. 


**3. The root cause**
<!-- In plain English, explain exactly what was wrong. Not "there was a bug in the streak logic" — explain the specific condition, comparison, or missing step that caused the problem. -->
The issue is that the check of the originator of the song and create_notification was simply never called in the rating function. The logic closely resembles the steps in adding a song to a playlist, and was simply missed here. 

**4. Your fix and side-effect check**
 <!-- What did you change and why does that change fix the root cause? What related functionality did you check afterward to confirm you didn't break anything? -->
 I added the following block to the function
 ```python
if song.shared_by != user_id:
    create_notification(
        user_id=song.shared_by,
        notification_type="song_rated",
        body=f"{rater.username} rated your song '{song.title}' {score}/5.",
    )
```
This fixed the issue by creating the notification if the rating was unique and successful. I then ran my test file again, and this time the test did pass. To check the other functionality, I simulated adding a playlist as well. 

## Git Log ---online 
