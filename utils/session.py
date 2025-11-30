# utils/session.py

class Session:
    current_user = None

    @classmethod
    def set_user(cls, user_data):
        """
        user_data should be a dictionary matching the DB row:
        { 'user_id': 1, 'username': '...', 'role': 'Student', ... }
        """
        cls.current_user = user_data

    @classmethod
    def get_user(cls):
        return cls.current_user

    @classmethod
    def clear(cls):
        cls.current_user = None