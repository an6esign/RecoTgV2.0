# ВРЕМЕННО, не персистентно, пропадёт при рестарте контейнера.
_user_sessions: dict[int, dict] = {}

def save_session(telegram_user_id: int, session_data: dict):
    """Сохранить токены и инфу о юзере после регистрации."""
    _user_sessions[telegram_user_id] = session_data

def get_session(telegram_user_id: int) -> dict | None:
    """Получить сохранённую сессию юзера."""
    return _user_sessions.get(telegram_user_id)