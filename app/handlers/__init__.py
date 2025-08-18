from aiogram import Router

from config import ENV
from handlers.cmd_handlers import cmd_router
from handlers.dialogs_handlers import dialog_router
from handlers.last_handlers import last_router
from handlers.photo_handlers import photo_router
from handlers.quiz_handlers import quiz_router
from handlers.random_fact_handlers import random_fact_router
from handlers.resume_handlers import resume_router
from handlers.sovet_handlers import sovet_router
from handlers.talk_handlers import talk_router
from handlers.test_handlers import test_router
from handlers.trans_handlers import trans_router
from handlers.voice_handlers import voice_router

main_router = Router()

if ENV == 'dev':
    main_router.include_routers(test_router)

main_router.include_routers(
    cmd_router,
    dialog_router,
    quiz_router,
    photo_router,
    random_fact_router,
    resume_router,
    sovet_router,
    talk_router,
    trans_router,
    voice_router,
    last_router
)

__all__ = [
    'main_router',
]
