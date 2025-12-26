import asyncio
from pyrogram import Client
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.types import Update
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio, MediumQualityVideo
from pytgcalls.types.stream import StreamAudioEnded
from pytgcalls.exceptions import NoActiveGroupCall

from config import API_ID, API_HASH, SESSION
from tools.queue import pop_queue, clear_queue
from tools.database import remove_active_chat, add_active_chat


class Call(PyTgCalls):
    def __init__(self):
        self.userbot = Client(
            name="MusicAssistant",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=SESSION,
        )
        super().__init__(self.userbot)

    async def start(self):
        print("🔵 Starting PyTgCalls Client...")
        await self.userbot.start()
        await super().start()
        print("✅ PyTgCalls Started!")

    async def join_call(self, chat_id, file_path, video=False):
        if video:
            stream = AudioVideoPiped(
                file_path,
                audio_parameters=HighQualityAudio(),
                video_parameters=MediumQualityVideo(),
            )
        else:
            stream = AudioPiped(
                file_path,
                audio_parameters=HighQualityAudio(),
            )

        await self.join_group_call(
            int(chat_id),
            stream,
            stream_type=StreamType().pulse_stream,
        )
        await add_active_chat(chat_id)

    async def change_song(self, chat_id, file_path, video=False):
        if video:
            stream = AudioVideoPiped(
                file_path,
                audio_parameters=HighQualityAudio(),
                video_parameters=MediumQualityVideo(),
            )
        else:
            stream = AudioPiped(
                file_path,
                audio_parameters=HighQualityAudio(),
            )

        await super().change_stream(int(chat_id), stream)

    async def stop_stream(self, chat_id):
        try:
            await self.leave_group_call(int(chat_id))
        except NoActiveGroupCall:
            pass
        await remove_active_chat(chat_id)
        await clear_queue(chat_id)

    async def pause(self, chat_id):
        await super().pause_stream(int(chat_id))

    async def resume(self, chat_id):
        await super().resume_stream(int(chat_id))


# Instance
MUSIC_CALL = Call()


# --- STREAM END HANDLER ---
@MUSIC_CALL.on_stream_end()
async def stream_end_handler(client, update: Update):
    if not isinstance(update, StreamAudioEnded):
        return

    chat_id = update.chat_id
    print(f"🔄 Stream Ended in {chat_id}")

    next_song = await pop_queue(chat_id)

    if next_song:
        try:
            await MUSIC_CALL.change_song(chat_id, next_song["file"])
        except Exception as e:
            print("❌ Next song error:", e)
            await MUSIC_CALL.stop_stream(chat_id)
    else:
        print("🛑 Queue empty, leaving VC")
        await MUSIC_CALL.stop_stream(chat_id)
