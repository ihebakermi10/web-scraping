# shared.py
import asyncio
import datetime
import json
import os
import uuid
import aiofiles

users_lock = asyncio.Lock()
db_lock = asyncio.Lock()

global_from_number = None
global_to_number = None
global_call_id = None

DATABASE_FILENAME = "Database.json"
USERS_FILENAME = "Uses.json"

async def load_database():
    if not os.path.exists(DATABASE_FILENAME):
        async with aiofiles.open(DATABASE_FILENAME, "w") as f:
            await f.write(json.dumps({"users": {}}))
        return {"users": {}}
    async with aiofiles.open(DATABASE_FILENAME, "r") as f:
        content = await f.read()
    return json.loads(content) if content.strip() else {"users": {}}

async def save_database(db):
    async with aiofiles.open(DATABASE_FILENAME, "w") as f:
        await f.write(json.dumps(db, indent=4))

async def load_users():
    if not os.path.exists(USERS_FILENAME):
        async with aiofiles.open(USERS_FILENAME, "w") as f:
            await f.write(json.dumps({"users": {}}))
        return {"users": {}}
    async with aiofiles.open(USERS_FILENAME, "r") as f:
        content = await f.read()
    return json.loads(content) if content.strip() else {"users": {}}

async def save_users(users):
    async with aiofiles.open(USERS_FILENAME, "w") as f:
        await f.write(json.dumps(users, indent=4))
