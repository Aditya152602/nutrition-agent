# 🌿 AI Nutrition Agent — IBM Watsonx.ai + Granite

**Full-stack AI nutrition web app** built with Python Flask + IBM Watsonx.ai (Granite models).
Personalized Indian meal plans, BMI calculator, nutrition analyzer, family profiles, dark mode UI.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask)
![IBM Watsonx](https://img.shields.io/badge/IBM-Watsonx.ai-1F70C1?logo=ibm)
![Granite](https://img.shields.io/badge/Model-Granite_3.8B-0F62FE)

---

## ✨ Features

| Feature | Description |
|---|---|
| 💬 AI Chat | Real-time nutrition Q&A with Granite AI |
| 🍱 Meal Planner | 7-day personalized Indian meal plans |
| 📊 Dashboard | Macro charts, nutrient tracker, weekly trends |
| ⚖️ BMI Calculator | South Asian thresholds, calorie recommendations |
| 👨‍👩‍👧 Family Profiles | Per-member AI personalization |
| 🔬 Nutrition Analyzer | Analyze any Indian/global meal |
| 🌿 Daily Tips | AI-powered nutrition tips |
| 🌙 Dark Mode | Full dark/light theme toggle |
| 📱 Responsive | Mobile-first Bootstrap 5 design |

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone <your-repo-url>
cd nutrition-agent
pip install -r requirements.txt
```

### 2. Configure IBM Watsonx.ai

```bash
cp .env.example .env
```

Edit `.env` and fill in your IBM credentials (see [IBM Setup](#ibm-cloud-setup) below):

```env
IBM_API_KEY=your_ibm_cloud_api_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-3-8b-instruct
FLASK_SECRET_KEY=any_random_32char_string
```

### 3. Run

```bash
python app.py
```

Open → `http://localhost:5000`

---

## 🔐 IBM Cloud Setup

### Step 1 — Create IBM Cloud Account
1. Go to [https://cloud.ibm.com](https://cloud.ibm.com)
2. Register for a free account (IBM offers free tier)

### Step 2 — Get API Key
1. IBM Cloud Console → **Manage** → **Access (IAM)**
2. Left sidebar → **API Keys**
3. Click **Create an IBM Cloud API key**
4. Copy and save — shown only once!
5. Paste into `.env` as `IBM_API_KEY`

### Step 3 — Create Watsonx.ai Project
1. Go to [https://dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com)
2. **New Project** → **Create an empty project**
3. Give it a name (e.g., "NutritionAgent")
4. **Manage** tab → **General** → copy **Project ID**
5. Paste into `.env` as `WATSONX_PROJECT_ID`

### Step 4 — Get Service URL
Pick your nearest region:

| Region | URL |
|---|---|
| US South (Dallas) | `https://us-south.ml.cloud.ibm.com` |
| EU Germany (Frankfurt) | `https://eu-de.ml.cloud.ibm.com` |
| UK South (London) | `https://eu-gb.ml.cloud.ibm.com` |
| Asia Pacific (Sydney) | `https://au-syd.ml.cloud.ibm.com` |
| Tokyo | `https://jp-tok.ml.cloud.ibm.com` |

Paste into `.env` as `WATSONX_URL`

### Step 5 — Choose Granite Model

| Model ID | Speed | Quality | Best For |
|---|---|---|---|
| `ibm/granite-3-8b-instruct` | ⚡ Fast | ★★★★ | Recommended default |
| `ibm/granite-13b-instruct-v2` | 🐢 Slower | ★★★★★ | More detailed plans |
| `ibm/granite-3-2b-instruct` | ⚡⚡ Fastest | ★★★ | Low-latency needs |

---

## 🎛️ Customizing the Agent

All customization lives in `AGENT_INSTRUCTIONS` dict at the top of `app.py`.

### Change Persona Name
```python
"persona_name": "DietBot",   # Change from "NutriBot"
"persona_role": "Ayurvedic Nutrition Expert",
```

### Change Tone
```python
"tone": "formal, clinical, precise",  # Options: friendly | formal | motivational | clinical
```

### Add Specializations
```python
"specializations": [
    "Keto diet for Indians",     # Add new
    "Renal diet planning",       # Add new
    # ... existing items
],
```

### Adjust Indian Food Preferences
```python
"indian_food_preferences": {
    "staple_foods": ["Your custom list..."],
    "regional_cuisines": ["Focus on specific regions..."],
    "include_fasting_options": True,   # For Navratri, Ekadashi etc.
}
```

### Add Safety Rules
```python
"safety_rules": [
    "ALWAYS mention that supplements need doctor approval",
    # Add your custom rules...
]
```

### Change Calorie Defaults
```python
"meal_planning": {
    "calorie_ranges": {
        "weight_loss": "1000-1200 kcal/day",  # Stricter
        "maintenance": "1600-1800 kcal/day",
    }
}
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Main web UI |
| `GET` | `/api/health` | Status + config check |
| `POST` | `/api/chat` | Chat with Granite AI |
| `POST` | `/api/meal-plan` | Generate meal plan |
| `POST` | `/api/nutrition-analysis` | Analyze food nutrition |
| `POST` | `/api/bmi` | Calculate BMI + calories |
| `GET` | `/api/family-profiles` | List family profiles |
| `POST` | `/api/family-profile` | Add/update profile |
| `DELETE` | `/api/family-profile/<id>` | Delete profile |
| `GET` | `/api/quick-tips` | Get daily nutrition tips |
| `GET` | `/api/agent-config` | View agent configuration |

### Chat Request Example
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Give me a high protein vegetarian breakfast",
    "session_id": "user123",
    "profile": {
      "name": "Priya",
      "age": "28",
      "goal": "Weight loss",
      "diet_type": "Vegetarian"
    }
  }'
```

### BMI Request Example
```bash
curl -X POST http://localhost:5000/api/bmi \
  -H "Content-Type: application/json" \
  -d '{"weight": 65, "height": 165, "age": 28, "gender": "female"}'
```

---

## 🐳 Docker Deployment

```bash
# Build
docker build -t nutribot .

# Run (pass env vars)
docker run -p 5000:5000 \
  -e IBM_API_KEY=your_key \
  -e WATSONX_PROJECT_ID=your_project_id \
  -e WATSONX_URL=https://us-south.ml.cloud.ibm.com \
  nutribot
```

---

## ☁️ IBM Code Engine Deployment

```bash
# Install IBM Cloud CLI + Code Engine plugin
ibmcloud plugin install code-engine

# Login & target region
ibmcloud login --apikey $IBM_API_KEY
ibmcloud ce project select --name nutrition-agent

# Deploy
ibmcloud ce application create \
  --name nutribot \
  --image icr.io/your-namespace/nutribot:latest \
  --env IBM_API_KEY=$IBM_API_KEY \
  --env WATSONX_PROJECT_ID=$WATSONX_PROJECT_ID \
  --env WATSONX_URL=https://us-south.ml.cloud.ibm.com \
  --port 5000
```

---

## 🌐 Heroku Deployment

```bash
# Install Heroku CLI, then:
heroku create your-nutribot-app
heroku config:set IBM_API_KEY=your_key
heroku config:set WATSONX_PROJECT_ID=your_project_id
heroku config:set WATSONX_URL=https://us-south.ml.cloud.ibm.com
heroku config:set FLASK_SECRET_KEY=your_secret
git push heroku main
```

---

## 📁 Project Structure

```
nutrition-agent/
├── app.py                  ← Backend + AGENT_INSTRUCTIONS
├── .env.example            ← Config template (copy → .env)
├── .env                    ← Your secrets (never commit!)
├── requirements.txt        ← Python dependencies
├── Procfile                ← Heroku/Code Engine process
├── Dockerfile              ← Container build
├── README.md               ← This file
└── templates/
    └── index.html          ← Complete SPA frontend
```

---

## 🔒 Security Notes

- Never commit `.env` to Git — add it to `.gitignore`
- Rotate IBM API keys periodically from IBM Cloud Console
- Use `FLASK_DEBUG=false` in production
- For production, use gunicorn: `gunicorn app:app -w 4 -b 0.0.0.0:5000`

```bash
# Add to .gitignore
echo ".env" >> .gitignore
```

---

## 📦 Requirements

```
Python 3.10+
ibm-watsonx-ai==1.1.2
flask==3.0.3
flask-cors==4.0.1
python-dotenv==1.0.1
```

---

## 🤝 Built With

- **IBM Watsonx.ai** — Granite foundation models
- **Python Flask** — Lightweight web framework
- **Bootstrap 5** — Responsive UI components
- **Chart.js** — Nutrition data visualization
- **Marked.js** — Markdown rendering in chat

---

*Built for AICTE × Edunet × IBM SkillsBuild Emerging Technologies Internship*
