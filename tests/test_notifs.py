
"""
tests/test_notifs.py — Mixtape

Tests for notifs logic.
"""

import pytest
from app import create_app, db
from models import Notification, User, Song, Playlist, playlist_entries
from services.notification_service import create_notification, add_to_playlist, rate_song, get_notifications, mark_as_read


@pytest.fixture
def app():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def seed_data(app):
    """
    An owner shares a song; a second user interacts with it (rates it / adds
    it to their playlist). Notifications should go to the owner.
    """
    with app.app_context():
        owner = User(username="owner", email="owner@example.com")
        actor = User(username="actor", email="actor@example.com")
        db.session.add_all([owner, actor])
        db.session.flush()

        song = Song(title="Midnight Drive", artist="The Wanderers", shared_by=owner.id)
        db.session.add(song)
        db.session.flush()

        playlist = Playlist(name="Road Trip", created_by=actor.id)
        db.session.add(playlist)

        db.session.commit()
        yield {"owner": owner, "rater": actor, "adder": actor, "song": song, "playlist": playlist}


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