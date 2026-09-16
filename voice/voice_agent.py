import sys
from pathlib import Path
import json

from dotenv import load_dotenv
from openai import OpenAI

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from voice.speech_input import listen
from voice.speech_output import speak
from tools.file_tool import create_file


# -----------------------------
# SETUP
# -----------------------------

load_dotenv()

client = OpenAI()


# -----------------------------
# TOOLS
# -----------------------------

tools = [
    {
        "type": "function",
        "name": "create_file",
        "description": "Create a text file inside the outputs folder.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the text file."
                },
                "content": {
                    "type": "string",
                    "description": "The content to put inside the file."
                }
            },
            "required": ["filename", "content"],
            "additionalProperties": False
        },
        "strict": True
    }
]


# -----------------------------
# START AGENT
# -----------------------------

print("🤖 Voice AI Automation Agent")
print("----------------------------")
print("Say 'exit' to stop.\n")


while True:

    # 🎤 Listen
    user_input = listen()

    if not user_input:
        continue

    print("🗣️ You:", user_input)

    # Stop command
    if user_input.lower() == "exit":
        speak("Goodbye buddy.")
        break


    # -----------------------------
    # SEND TO AI
    # -----------------------------

    input_items = [
        {
            "role": "user",
            "content": user_input
        }
    ]


    while True:

        response = client.responses.create(
            model="gpt-5.6-luna",
            tools=tools,
            input=input_items
        )


        # Save AI response
        input_items.extend(response.output)


        # -----------------------------
        # CHECK FOR TOOL CALLS
        # -----------------------------

        tool_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]


        # -----------------------------
        # NORMAL AI RESPONSE
        # -----------------------------

        if not tool_calls:

            speak(response.output_text)
            break


        # -----------------------------
        # EXECUTE TOOLS
        # -----------------------------

        for tool_call in tool_calls:

            print(f"🔧 Using tool: {tool_call.name}")


            if tool_call.name == "create_file":

                arguments = json.loads(tool_call.arguments)

                filename = arguments["filename"]
                content = arguments["content"]


                try:

                    result = create_file(
                        filename,
                        content
                    )

                except Exception as error:

                    result = f"Tool error: {error}"


                print("📁", result)


                # Send tool result back to AI
                input_items.append(
                    {
                        "type": "function_call_output",
                        "call_id": tool_call.call_id,
                        "output": result
                    }
                )