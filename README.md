YASH AI is a smart, voice-controlled desktop assistant that combines Deep Learning, Speech Recognition, System Automation, and LLM-based knowledge retrieval.
The assistant listens to user commands, identifies intent using a trained neural network, executes actions on the system, and uses the Gemini API when dynamic knowledge is required.

⭐ Key Capabilities
🎙️ Voice Interaction

Real-time speech recognition using SpeechRecognition

Natural text-to-speech responses using pyttsx3

Noise adjustment and detailed voice exception handling

🤖 AI Intent Recognition

Custom-trained neural network using:

Tokenizer

Label Encoder

Keras Sequential model

Predicts intents with improved confidence using a refined architecture (32-dim embedding + dual 64-unit dense layers)

🔗 LLM Integration (Gemini API)

Used when:

Confidence score < 0.55

Intent predicted as general_query

The assistant will:

Automatically fallback to Gemini

Retrieve a real-time answer

Speak the response

🖥️ System Automation

YASH AI can:

Open and close Windows applications
(Notepad, Calculator, Camera, Paint, Chrome, Firefox)

Adjust system brightness

Adjust system volume

Launch websites (YouTube, Facebook, Google, LinkedIn, etc.)

🧠 Knowledge Logic

The assistant follows a hybrid route:

Direct Command Handling

Deep Learning Intent Model

LLM (Gemini) Fallback

Graceful error handling

🪟 Greeting & Context Awareness

On startup, YASH AI:

Detects current time

Detects current day

Greets the user with time-aware phrase

Introduces itself as “your personal assistant"
