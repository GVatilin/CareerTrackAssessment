from .auth import api_router as auth_router
from .healh_check import api_router as healh_check_router
from .user import api_router as user_debag
from .settings import api_router as settings_router
from .google_auth import api_router as google_router
from .upload import api_router as upload_router
from .question import api_router as question_router
from .topic import api_router as topic_router
from .docs import api_router as docs_router


list_of_routes = [
    auth_router,
    healh_check_router,
    user_debag,
    settings_router,
    google_router,
    upload_router,
    question_router,
    topic_router,
    docs_router,
]

__all__ = [
    "list_of_routes",
]