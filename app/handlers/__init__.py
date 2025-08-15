from aiogram import Router

from config import ENV
from handlers.cmd_handlers import cmd_router
from handlers.dialogs_handlers import dialog_router
from handlers.last_handlers import last_router
from handlers.test_handlers import test_router
from handlers.voice_handlers import voice_router

main_router = Router()

if ENV == 'dev':
    main_router.include_routers(test_router)

main_router.include_routers(cmd_router, dialog_router, voice_router, last_router)

__all__ = [
    'main_router',
]
