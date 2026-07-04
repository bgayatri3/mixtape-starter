# Detailed Overview of Mixtape Starter
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

```python

```
**2. How the root cause was found**
<!-- Which files did you look at? What was your navigation path? What moment made you confident you'd found the right place — not just a suspicious area, but the specific cause? -->


**3. The root cause**
<!-- In plain English, explain exactly what was wrong. Not "there was a bug in the streak logic" — explain the specific condition, comparison, or missing step that caused the problem. -->
The specific condition was 24 hours before at any time else than midnight. For example. 24 hours before 7/4 at 7PM would also include 7/3 at 8PM which is the day before. Thus, the cut_off was not properly counted. 

**4. Your fix and side-effect check**
 <!-- What did you change and why does that change fix the root cause? What related functionality did you check afterward to confirm you didn't break anything? -->

## Issue #x: xxxxx
**1. Issue Reproduction**
<!-- What steps did you take to confirm the bug exists before touching any code? What inputs, sequence of actions, or data condition triggered the behavior? -->

**2. How the root cause was found**
<!-- Which files did you look at? What was your navigation path? What moment made you confident you'd found the right place — not just a suspicious area, but the specific cause? -->

**3. The root cause**
<!-- In plain English, explain exactly what was wrong. Not "there was a bug in the streak logic" — explain the specific condition, comparison, or missing step that caused the problem. -->

**4. Your fix and side-effect check**
 <!-- What did you change and why does that change fix the root cause? What related functionality did you check afterward to confirm you didn't break anything? -->

---
## Issue #x: xxxxx
**1. Issue Reproduction**
<!-- What steps did you take to confirm the bug exists before touching any code? What inputs, sequence of actions, or data condition triggered the behavior? -->

**2. How the root cause was found**
<!-- Which files did you look at? What was your navigation path? What moment made you confident you'd found the right place — not just a suspicious area, but the specific cause? -->

**3. The root cause**
<!-- In plain English, explain exactly what was wrong. Not "there was a bug in the streak logic" — explain the specific condition, comparison, or missing step that caused the problem. -->

**4. Your fix and side-effect check**
 <!-- What did you change and why does that change fix the root cause? What related functionality did you check afterward to confirm you didn't break anything? -->