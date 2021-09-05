import re
from pyrogram.types.user_and_chats.chat_permissions import ChatPermissions
from schema.serial import serializeDict, serializeList
from pyrogram import Client,filters
from pyrogram.types import Message
from config.tg import api_hash,api_id,bot_token
from config.db import collection
from functions import users
import time

app = Client(
    'rg_bot',
    api_id = api_id,
    api_hash = api_hash,
    bot_token = bot_token
)

flooders = {}

#Reset flood count if user id doesnt matches with current user
async def reset(chat_id,user_id):
    for user in flooders[chat_id]:
        if user != user_id:
            flooders[chat_id][user] = 0

@app.on_message(filters.group
    & ~filters.service
    & ~filters.me
    & ~filters.private
    & ~filters.channel
    & ~filters.bot
    & ~filters.edited,
    group=1)
async def flood_watch(_,message:Message):
    GROUP_ADMIN = {}
    chat_id = message.chat.id
    user_id =  message.from_user.id
    mention = message.from_user.mention
    try:
        GROUP_ADMIN = await users.get_chat_admin_id(_,message)
        if user_id not in GROUP_ADMIN:
            try:
                #Initialize the dict if it's not already initialized
                if chat_id not in flooders:
                    flooders[chat_id] = {}
                if user_id not in flooders[chat_id]:
                    flooders[chat_id][user_id] = 0
            except Exception as e:
                await message.reply_text(f'Error Encountered : {e}')
            try:
                
                #Increase Flood Count On Continuous Message
                flooders[chat_id][user_id] +=1
                await message.reply_text(f'{mention} has flood count of {flooders[chat_id][user_id]}')
                if flooders[chat_id][user_id] > 10:
                    await app.restrict_chat_member(chat_id,user_id,ChatPermissions(can_send_messages=False),int(time.time()+100))
                    await message.reply_text(f'Hold Your Horses {mention}')
                    flooders[chat_id][user_id] = 0
            except Exception as e:
                flooders[chat_id][user_id] = 1
                await message.reply_text(f'Error Encountered : {e} \nFlood Reset For ID : {user_id}')
        #Reset - Line 18
        await reset(chat_id,user_id)
    except Exception as e:
        print(e)


regex_increase_karma = r"^([+]+|thnx|thx|tnx|ty|thank you|thanx|thanks|pro|cool|good|👍)"
regex_decrease_karma = r"^([-]+|👎)"

async def update_rank(mention,user_id,rank_name,message:Message):
            updated = collection.update_one(
                {'tg_id':user_id},
                {
                    '$set':{
                        'role':rank_name
                    }
                }
            )
            if updated.modified_count == 1:
                role = serializeDict(collection.find_one({
                    'tg_id':user_id
                }))
                role = role['role']
                await message.reply_text(f'🎉{mention} just got promoted as {role} 🎉')


@app.on_message(filters.group
    & filters.incoming
    & filters.reply
    & filters.regex(regex_increase_karma,re.IGNORECASE)
    & ~filters.bot
    & ~filters.via_bot
    & ~filters.bot
    & ~filters.edited,
    group=2) 
async def karma(_,message:Message):
    if message.reply_to_message.from_user.id == message.from_user.id:
        return
    if not message.reply_to_message.from_user:
        return
    if not message.from_user:
        return
    chat_id = message.chat.id
    user_id = message.reply_to_message.from_user.id
    user_mention = message.reply_to_message.from_user.mention
    user = collection.find_one_and_update(
        {'tg_id':user_id},
        {'$set':{
            'name': message.reply_to_message.from_user.first_name,
            'role': 'Trainee',
        },
          '$inc':{
              'karma':1
          }
        },upsert=True
    )
    if user:
        user = serializeDict(user)
        karma = user['karma']
        await message.reply_text(f'Karma Incremented Of {user_mention} \nCurrent Karma : {karma}')
        if karma == 10:
            await update_rank(user_mention,user_id,'Adventurer',message)
        if karma == 20:
            await update_rank(user_mention,user_id,'Daredevil',message)
        if karma == 30:
            await update_rank(user_mention,user_id,'Veteran',message)
        if karma == 40:
            await update_rank(user_mention,user_id,'Champion',message)
        if karma == 50:
            await update_rank(user_mention,user_id,'Champion Deluxe',message)
        if karma == 60:
            await update_rank(user_mention,user_id,'Guildmaster',message)
        

@app.on_message(filters.command('rankings',prefixes=['/','.']))
async def get_top_rankings(_,message:Message):
    ranks = serializeList(collection.find().sort('karma',-1).limit(10))
    # if len(ranks) < 10:
    #     await message.reply_text('Rankings')
    # else:
    msg = f'__--**RANKINGS**--__\n'
    for i in range(len(ranks)):
        msg += f'''• **{ranks[i]['role']}** - {ranks[i]['name']} - __{ranks[i]['karma']} Karma__\n'''
    await message.reply_text(msg,parse_mode="markdown")
    print(ranks)

app.run()