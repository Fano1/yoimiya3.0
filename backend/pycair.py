# backend.py
from PyCharacterAI import get_client
from PyCharacterAI.exceptions import SessionClosedError
import os
from dotenv import load_dotenv

load_dotenv()

character_id = os.getenv("CHARACTER_ID")
token = os.getenv("CHARACTER_TOKEN")
chat_id = os.getenv("CHAT_ID_NEW")

client = None

async def init_client():
    global client
    if client is None:
        client = await get_client(token=token)
        me = await client.account.fetch_me()
        print(f"Authenticated as @{me.username}")
    return client

async def run_cai_async(message: str) -> str:
    try:
        cli = await init_client()
        # chat, greeting_message = await client.chat.create_chat(character_id)
        # print(f"{greeting_message.author_name}: {greeting_message.get_primary_candidate().text}")

        response = await cli.chat.send_message(character_id, chat_id, message)
        return f"[{response.author_name}]: {response.get_primary_candidate().text}"
    except SessionClosedError:
        return "Session closed. Please restart the backend."
    except Exception as e:
        return f"Error: {str(e)}"

async def close_session():
    await client.close_session()

