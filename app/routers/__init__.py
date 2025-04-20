from .search import router as search_router
from .products import router as products_router
from .alerts import router as alerts_router
from .users import router as users_router

__all__ = [
    'search_router',
    'products_router',
    'alerts_router',
    'users_router',
]
