import asyncio
import os

from aiogram import Router, types
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message
from pydantic import json

from parsing import get_group_schedule, get_group_id

user_router = Router(name=__name__)

