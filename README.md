# 🌍 AI-Powered Travel Planner

An intelligent, customizable travel itinerary generator that uses LLMs to create detailed, personalized travel plans based on user preferences like budget, destination, interests, mobility, dietary needs, and more.

---

## ✨ Features

- Collects and refines user travel preferences through a friendly interface
- Handles both **structured inputs** (forms) and **flexible free-text descriptions**
- Uses **Hugging Face Falcon 7B Instruct** model to generate detailed travel itineraries
- Supports:
  - Budget interpretation (e.g., "moderate", "$2000")
  - Flexible date parsing (e.g., "next summer")
  - Personalized suggestions (e.g., hidden gems, cultural highlights)
- Mobile, dietary, and accommodation preference handling
- Hosted with Gradio on Hugging Face Spaces

---

## 🚀 Live Demo

👉 [Try it on Hugging Face Spaces](https://huggingface.co/spaces/Rafsanhassan/Ai-travel-planner)

> Replace the URL above with your actual Hugging Face Space link once deployed.

---

## 🛠 Tech Stack

- **Python 3.10+**
- **Gradio** for interactive web UI
- **Hugging Face Transformers API** (Falcon-7B-Instruct)
- **Prompt engineering & chaining**
- `requests`, `datetime`, `re` for utility operations

---

## 📦 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/ai-travel-planner.git
cd ai-travel-planner
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Hugging Face API Key
Set your Hugging Face API key in your environment:

**Linux/macOS:**
```bash
export HUGGINGFACE_API_TOKEN='your_api_key_here'
```

**Windows (PowerShell):**
```powershell
$env:HUGGINGFACE_API_TOKEN = "your_api_key_here"
```

---

## 🧠 How It Works

1. Users input trip details (or describe them in natural language)
2. The system extracts/refines preferences (dates, destination, interests, etc.)
3. A dynamic travel prompt is generated and sent to Falcon 7B via Hugging Face Inference API
4. The generated itinerary is displayed in a structured, readable format

---

## 📂 Folder Structure

```
📦 ai-travel-planner
├── travel_planner.py      # Main logic and AI pipeline
├── app.py                 # Gradio interface entrypoint
├── requirements.txt       # Python dependencies
└── README.md              # You're here!
```

---

## ☁️ Deployment on Hugging Face Spaces

1. Push the code to a public GitHub repo
2. Create a new **Gradio Space** at [huggingface.co/spaces](https://huggingface.co/spaces)
3. Link your GitHub repo or upload the files directly
4. Go to **Settings > Secrets**, and add your API key as:
   - `HUGGINGFACE_API_TOKEN = your_api_key`
5. Hugging Face Spaces will automatically launch your Gradio app

---

## 📸 Screenshots

*(Add a few screenshots of the app interface if you'd like)*

---

## 🤝 Acknowledgments

- Hugging Face for the Falcon model and API
- Gradio for the awesome web interface toolkit

---

## 📫 Contact

Feel free to reach out if you have any questions!

- GitHub: [@your_username](https://github.com/your_username)
- Email: your.email@example.com
```

---

Let me know if you’d like this customized with your **actual GitHub repo name**, **username**, or **Hugging Face space name** and I’ll fill those in for you!
