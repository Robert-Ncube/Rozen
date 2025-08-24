from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    noise_cancellation,
)
from livekit.plugins import google
from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from tools import get_weather, search_web, send_email

load_dotenv()

# 🧑‍🎩 Rozen the Assistant
class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            llm=google.beta.realtime.RealtimeModel(
                voice="Charon",  # You can switch to "Aoede" if you prefer
                temperature=0.8,
            ),
            tools=[
                get_weather,
                search_web,
                send_email
            ],
        )

    # 🧠 Auto-search logic: Rozen acts immediately if user asks to search or find something
    async def on_message(self, message, session):
        user_text = message.text.lower()

        # 🔍 Detect search intent
        if "search" in user_text or "find" in user_text:
            await session.send_text("Roger Boss. Initiating search now.")

            # 🛠️ Use the search_web tool with the full user message as query
            result = await search_web.invoke({"query": user_text})

            # 🗣️ Rozen responds with a classy one-liner
            await session.send_text(f"Check! I searched and found: {result}")
        else:
            # 🧾 Let Rozen respond normally if no search is requested
            await super().on_message(message, session)


# 🚪 Entry point for the agent session
async def entrypoint(ctx: agents.JobContext):
    session = AgentSession()

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            video_enabled=True,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()

    # 🎩 Rozen introduces himself with style
    await session.generate_reply(
        instructions=SESSION_INSTRUCTION,
    )


# 🏁 Run the agent
if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
