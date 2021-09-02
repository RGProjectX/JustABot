from pyrogram import Client
from pyrogram.types import Message

async def get_chat_admin_id(app:Client ,message:Message):
    return [admin.user.id for admin in await app.get_chat_members(message.chat.id,filter='administrators')]