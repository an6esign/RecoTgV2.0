_user_sessions: dict[int, dict] = {}

def save_session(telegram_user_id: int, session_data: dict):
    _user_sessions[telegram_user_id] = session_data

def get_session(telegram_user_id: int) -> dict | None:
    return _user_sessions.get(telegram_user_id)