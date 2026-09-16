import sys
import json
import math
import threading

from dotenv import load_dotenv
from openai import OpenAI

from PySide6.QtCore import Qt, QTimer, QObject, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QFont
from PySide6.QtWidgets import QApplication, QWidget


from voice.speech_input import listen
from voice.speech_output import speak
from tools.file_tool import create_file


# ==============================
# SETUP
# ==============================

load_dotenv()

client = OpenAI()

MODEL = "gpt-5.6-luna"
# ==============================
# AI TOOL DEFINITION
# ==============================

TOOLS = [
    {
        "type": "function",
        "name": "create_file",
        "description": (
            "Create a text file inside the "
            "project's outputs folder."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": (
                        "A simple filename such as notes.txt."
                    )
                },
                "content": {
                    "type": "string",
                    "description": (
                        "The text content to write "
                        "into the file."
                    )
                }
            },
            "required": [
                "filename",
                "content"
            ],
            "additionalProperties": False
        },
        "strict": True
    }
]


# ==============================
# UI SIGNALS
# ==============================

class AgentSignals(QObject):

    status = Signal(str)
    message = Signal(str)
    # ==============================
# FUTURISTIC AGENT UI
# ==============================

class AgentUI(QWidget):

    def __init__(self, signals):

        super().__init__()

        self.signals = signals

        self.signals.status.connect(
            self.set_status
        )

        self.signals.message.connect(
            self.set_message
        )

        self.status_text = "SYSTEM READY"
        self.message_text = "Ready when you are..."

        self.angle = 0.0
        self.pulse = 0.0

        self.setWindowTitle(
            "AI Automation Agent"
        )

        self.setStyleSheet(
            "background: #020710;"
        )

        self.showFullScreen()

        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self.animate
        )

        self.timer.start(30)


    def set_status(self, text):

        self.status_text = text
        self.update()


    def set_message(self, text):

        self.message_text = text
        self.update()
    def animate(self):

        self.angle = (
            self.angle + 1.5
        ) % 360

        self.pulse += 0.08

        self.update()
        # ==============================
# UI HELPER: PANEL
# ==============================

    def panel(
        self,
        painter,
        x,
        y,
        width,
        height,
        title
    ):

        painter.setBrush(
            QColor(5, 20, 35, 205)
        )

        painter.setPen(
            QPen(
                QColor(0, 190, 255, 180),
                2
            )
        )

        painter.drawRoundedRect(
            x,
            y,
            width,
            height,
            15,
            15
        )

        painter.setPen(
            QColor(100, 220, 255)
        )

        painter.setFont(
            QFont(
                "Segoe UI",
                12,
                QFont.Bold
            )
        )

        painter.drawText(
            x + 16,
            y + 27,
            title
        )


# ==============================
# UI HELPER: TEXT
# ==============================

    def text(
        self,
        painter,
        x,
        y,
        value,
        size=10
    ):

        painter.setPen(
            QColor(190, 235, 255)
        )

        painter.setFont(
            QFont(
                "Segoe UI",
                size
            )
        )

        painter.drawText(
            x,
            y,
            value
        )
        # ==============================
# DRAW MAIN UI
# ==============================

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        width = self.width()
        height = self.height()

        # Background
        painter.fillRect(
            self.rect(),
            QColor(2, 7, 16)
        )

        # Background glow
        painter.setBrush(
            QColor(0, 70, 120, 35)
        )

        painter.setPen(
            Qt.NoPen
        )

        painter.drawEllipse(
            width // 2 - 520,
            height // 2 - 300,
            1040,
            600
        )

        # Grid
        painter.setPen(
            QPen(
                QColor(0, 130, 180, 28),
                1
            )
        )

        for x in range(0, width, 45):

            painter.drawLine(
                x,
                int(height * 0.67),
                x,
                height
            )

        for y in range(
            int(height * 0.67),
            height,
            32
        ):

            painter.drawLine(
                0,
                y,
                width,
                y
            )

        # Title
        painter.setPen(
            QColor(100, 225, 255)
        )

        painter.setFont(
            QFont(
                "Segoe UI",
                30,
                QFont.Bold
            )
        )

        painter.drawText(
            width // 2 - 125,
            62,
            "AI AGENT"
        )

        painter.setPen(
            QColor(150, 210, 235)
        )

        painter.setFont(
            QFont(
                "Segoe UI",
                11
            )
        )

        painter.drawText(
            width // 2 - 175,
            92,
            "THINK  •  PLAN  •  EXECUTE  •  AUTOMATE"
        )
        # ==============================
        # SYSTEM STATUS PANEL
        # ==============================

        self.panel(
            painter,
            24,
            30,
            255,
            178,
            "SYSTEM STATUS"
        )

        self.text(
            painter,
            42,
            70,
            "●  AI CORE        ONLINE"
        )

        self.text(
            painter,
            42,
            100,
            "●  MICROPHONE     READY"
        )

        self.text(
            painter,
            42,
            130,
            "●  TOOLS          LOADED"
        )

        self.text(
            painter,
            42,
            160,
            "●  AUTOMATION     ACTIVE"
        )


        # ==============================
        # LIVE ACTIVITY PANEL
        # ==============================

        self.panel(
            painter,
            24,
            228,
            255,
            188,
            "LIVE ACTIVITY"
        )

        self.text(
            painter,
            44,
            270,
            "○  Listening..."
        )

        self.text(
            painter,
            44,
            300,
            "○  Processing..."
        )

        self.text(
            painter,
            44,
            330,
            "○  Planning..."
        )

        self.text(
            painter,
            44,
            360,
            "○  Executing..."
        )

        self.text(
            painter,
            44,
            390,
            "○  Completed."
        )
        # ==============================
        # CAPABILITIES PANEL
        # ==============================

        self.panel(
            painter,
            width - 279,
            30,
            255,
            205,
            "CAPABILITIES"
        )

        self.text(
            painter,
            width - 258,
            70,
            "▣  File Management"
        )

        self.text(
            painter,
            width - 258,
            100,
            "◎  Web Automation"
        )

        self.text(
            painter,
            width - 258,
            130,
            "⌕  Research & Analysis"
        )

        self.text(
            painter,
            width - 258,
            160,
            "▣  App Control"
        )

        self.text(
            painter,
            width - 258,
            190,
            "⚙  Custom Workflows"
        )


        # ==============================
        # QUICK TOOLS PANEL
        # ==============================

        self.panel(
            painter,
            width - 279,
            255,
            255,
            165,
            "QUICK TOOLS"
        )

        self.text(
            painter,
            width - 255,
            300,
            "▣  Files"
        )

        self.text(
            painter,
            width - 135,
            300,
            "◎  Web"
        )

        self.text(
            painter,
            width - 255,
            335,
            "▣  Notes"
        )

        self.text(
            painter,
            width - 135,
            335,
            "⌕  Research"
        )

        self.text(
            painter,
            width - 255,
            370,
            "⚙  System"
        )

        self.text(
            painter,
            width - 135,
            370,
            "••• More"
        )
        # ==============================
        # CENTRAL AI CORE
        # ==============================

        cx = width // 2
        cy = height // 2 + 15

        # Circular energy rings
        for radius in range(
            220,
            80,
            -20
        ):

            alpha = max(
                18,
                92 - radius // 3
            )

            painter.setPen(
                QPen(
                    QColor(
                        0,
                        180,
                        255,
                        alpha
                    ),
                    2
                )
            )

            painter.setBrush(
                Qt.NoBrush
            )

            painter.drawEllipse(
                cx - radius,
                cy - radius,
                radius * 2,
                radius * 2
            )


        # Rotating holographic rings
        for index in range(4):

            painter.save()

            painter.translate(
                cx,
                cy
            )

            painter.rotate(
                self.angle + index * 45
            )

            painter.setPen(
                QPen(
                    QColor(
                        0,
                        210,
                        255,
                        170
                    ),
                    3
                )
            )

            painter.drawEllipse(
                -180,
                -52,
                360,
                104
            )

            painter.restore()


        # Pulsing core
        glow = int(
            120 +
            math.sin(self.pulse) * 40
        )

        painter.setBrush(
            QColor(
                0,
                180,
                255,
                glow
            )
        )

        painter.setPen(
            QPen(
                QColor(
                    100,
                    240,
                    255
                ),
                5
            )
        )

        painter.drawEllipse(
            cx - 72,
            cy - 72,
            144,
            144
        )


        # Inner core
        painter.setBrush(
            QColor(
                20,
                230,
                255
            )
        )

        painter.setPen(
            Qt.NoPen
        )

        painter.drawEllipse(
            cx - 26,
            cy - 26,
            52,
            52
        )


        # Current status
        painter.setPen(
            QColor(
                50,
                255,
                190
            )
        )

        painter.setFont(
            QFont(
                "Segoe UI",
                11,
                QFont.Bold
            )
        )

        painter.drawText(
            cx - 70,
            cy + 118,
            self.status_text
        )
        # ==============================
        # AI OUTPUT PANEL
        # ==============================

        self.panel(
            painter,
            cx - 300,
            height - 145,
            600,
            86,
            "AI OUTPUT"
        )

        output = self.message_text

        if len(output) > 80:
            output = (
                output[:77] +
                "..."
            )

        self.text(
            painter,
            cx - 275,
            height - 102,
            output,
            11
        )


        # ==============================
        # FOOTER
        # ==============================

        self.text(
            painter,
            24,
            height - 22,
            "AI AUTOMATION AGENT  v1.0"
        )

        self.text(
            painter,
            width - 305,
            height - 22,
            "VOICE • TOOLS • AUTOMATION"
        )

        painter.end()


    # ==============================
    # ESCAPE TO CLOSE
    # ==============================

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Escape:

            self.close()
            # ==============================
# AI AGENT LOOP
# ==============================

def run_agent(signals):

    print("\nAI Automation Agent")
    print("-------------------")
    print("Say 'exit' to close the agent.\n")

    while True:

        signals.status.emit(
            "LISTENING..."
        )

        user_input = listen()

        if not user_input:
            continue

        print(
            "You:",
            user_input
        )

        signals.message.emit(
            user_input
        )

        if (
            user_input
            .lower()
            .strip()
            == "exit"
        ):

            signals.status.emit(
                "SHUTTING DOWN..."
            )

            speak(
                "Goodbye."
            )

            return

        signals.status.emit(
            "THINKING..."
        )

        input_items = [
            {
                "role": "user",
                "content": user_input
            }
        ]

        while True:

            response = client.responses.create(
                model=MODEL,
                tools=TOOLS,
                input=input_items
            )

            input_items.extend(
                response.output
            )

            tool_calls = [
                item
                for item in response.output
                if item.type == "function_call"
            ]

            if not tool_calls:

                answer = (
                    response.output_text
                    .strip()
                )

                if answer:

                    print(
                        "AI:",
                        answer
                    )

                    signals.status.emit(
                        "SPEAKING..."
                    )

                    signals.message.emit(
                        answer
                    )

                    speak(
                        answer
                    )

                break

            signals.status.emit(
                "EXECUTING TOOL..."
            )

            for tool_call in tool_calls:

                print(
                    "Using tool:",
                    tool_call.name
                )

                if (
                    tool_call.name
                    == "create_file"
                ):

                    try:

                        arguments = json.loads(
                            tool_call.arguments
                        )

                        result = create_file(
                            arguments["filename"],
                            arguments["content"]
                        )

                    except Exception as error:

                        result = (
                            f"Tool error: {error}"
                        )

                    print(
                        "Tool:",
                        result
                    )

                    input_items.append(
                        {
                            "type":
                                "function_call_output",
                            "call_id":
                                tool_call.call_id,
                            "output":
                                result
                        }
                    )


# ==============================
# START APPLICATION
# ==============================

if __name__ == "__main__":

    app = QApplication(
        sys.argv
    )

    signals = AgentSignals()

    window = AgentUI(
        signals
    )

    window.show()

    agent_thread = threading.Thread(
        target=run_agent,
        args=(signals,),
        daemon=True
    )

    agent_thread.start()

    sys.exit(
        app.exec()
    )