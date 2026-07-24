"""
MongoDB-based session backend for persistent cross-server sessions.
"""

from django.contrib.sessions.backends.db import SessionStore as DBSessionStore
from django.contrib.sessions.models import Session
from django.utils.timezone import now
import json
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class MongoSessionStore(DBSessionStore):
    """
    MongoDB-backed session store using Django's default Session model.
    Sessions are persisted to the database and shared across all servers.
    """

    def load(self):
        """Load session data from database."""
        try:
            s = Session.objects.get(session_key=self.session_key, expire_date__gt=now())
            return s.get_decoded()
        except Session.DoesNotExist:
            self.create()
            return {}

    def save(self, must_create=False):
        """Save session data to database."""
        if not self.session_key:
            self.create()

        session_data = self.get_encoded()
        expires = now() + timedelta(seconds=self.get_expiry_age())

        if must_create:
            try:
                Session.objects.create(
                    session_key=self.session_key,
                    session_data=session_data,
                    expire_date=expires
                )
            except Exception as e:
                logger.error(f"Error creating session: {e}")
                self.cycle_key()
        else:
            try:
                Session.objects.filter(session_key=self.session_key).update(
                    session_data=session_data,
                    expire_date=expires
                )
            except Exception as e:
                logger.error(f"Error updating session: {e}")

    def exists(self, session_key):
        """Check if session exists and is not expired."""
        try:
            Session.objects.get(session_key=session_key, expire_date__gt=now())
            return True
        except Session.DoesNotExist:
            return False

    def delete(self, session_key=None):
        """Delete session from database."""
        if session_key is None:
            session_key = self.session_key

        try:
            Session.objects.filter(session_key=session_key).delete()
        except Exception as e:
            logger.error(f"Error deleting session: {e}")

    @classmethod
    def clear_expired(cls):
        """Clear expired sessions from database."""
        Session.objects.filter(expire_date__lt=now()).delete()
