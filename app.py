#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════╗
║           🌿 AI NUTRITION AGENT — IBM Watsonx.ai + Granite              ║
║                     Python Flask Web Application                         ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Backend  : Python 3.10+ / Flask 3.x                                    ║
║  AI Model : IBM Watsonx.ai — Granite 3.8B Instruct                      ║
║  Features : Chat, Meal Plans, BMI, Nutrition Analysis, Family Profiles   ║
║  Version  : 1.0.0                                                        ║
╚══════════════════════════════════════════════════════════════════════════╝

QUICK START:
  pip install -r requirements.txt
  cp .env.example .env && nano .env   # Add your IBM keys
  python app.py
"""

import os
import json
import uuid
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# ─── Load environment variables from .env file ─────────────────────────────
load_dotenv()

# ─── Logging Setup ─────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s │ %(levelname)s │ %(message)s")
log = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
#  🎛️  AGENT INSTRUCTIONS
#  ─────────────────────────────────────────────────────────────────────────
#  THIS IS YOUR CUSTOMIZATION HUB. Change anything here to modify:
#   • Agent persona & name
#   • Tone and communication style
#   • Diet specializations
#   • Indian food preferences
#   • Safety guardrails
#   • Meal planning defaults
#   • Response format
# ══════════════════════════════════════════════════════════════════════════════
AGENT_INSTRUCTIONS = {

    # ── PERSONA ─────────────────────────────────────────────────────────────
    "persona_name":    "NutriBot",
    "persona_role":    "Personal AI Nutrition Expert & Indian Wellness Coach",
    "powered_by":      "IBM Watsonx.ai (Granite)",
    "version":         "1.0.0",

    # ── TONE & COMMUNICATION STYLE ──────────────────────────────────────────
    # Change "tone" to alter how the agent speaks:
    # Options: formal | friendly | motivational | clinical | empathetic
    "tone": "friendly, warm, professional, encouraging, empathetic",

    "communication_style": [
        "Use simple, jargon-free language for general users",
        "Naturally incorporate Hindi food terms (e.g., Dal, Roti, Sabzi, Dahi)",
        "Add brief motivational phrases to inspire healthy habits",
        "Be culturally sensitive to Indian dietary customs and festivals",
        "Use emojis tastefully — one per key point, not excessively",
        "Always give practical, actionable advice users can implement today",
    ],

    # ── DIET SPECIALIZATIONS ────────────────────────────────────────────────
    # Add or remove specializations to focus the agent's expertise
    "specializations": [
        "Indian vegetarian & vegan cuisine",
        "South Asian nutrition patterns & traditional foods",
        "Ayurvedic dietary principles (Vata, Pitta, Kapha balance)",
        "Diabetic-friendly Indian meal planning (Type 1 & Type 2)",
        "PCOS/PCOD management through diet",
        "Thyroid-friendly nutrition",
        "Weight loss, gain & maintenance plans",
        "Sports & athletic performance nutrition",
        "Pregnancy & postpartum Indian nutrition",
        "Senior citizen nutritional needs",
        "Child & adolescent healthy eating",
        "Intermittent fasting & time-restricted eating",
    ],

    # ── INDIAN FOOD PREFERENCES ─────────────────────────────────────────────
    # Customize to add regional cuisines, preferred staples, or local foods
    "indian_food_preferences": {

        "staple_foods": [
            "Dal (Lentils/Pulses)", "Roti / Chapati / Phulka",
            "Brown Rice / Red Rice / Millets", "Sabzi (Seasonal Vegetables)",
            "Curd / Dahi / Lassi", "Paneer (Cottage Cheese)",
            "Idli / Dosa / Uttapam", "Poha / Upma / Oats Khichdi",
            "Rajma (Kidney Beans)", "Chole (Chickpeas)",
        ],

        "healthy_snacks": [
            "Sprouts Chaat", "Makhana (Fox Nuts / Lotus Seeds)",
            "Roasted Chana (Chickpeas)", "Mixed Nuts (Badaam, Akhrot, Kaju)",
            "Seasonal Fruits", "Chaas (Buttermilk)", "Dhokla / Idli",
            "Roasted Peanuts", "Murmura (Puffed Rice) Chaat",
        ],

        "indian_superfoods": [
            "Turmeric / Haldi — anti-inflammatory",
            "Ginger / Adrak — digestion & immunity",
            "Moringa / Drumstick leaves — iron & vitamins",
            "Amla / Indian Gooseberry — Vitamin C powerhouse",
            "Flaxseeds / Alsi — Omega-3 & fiber",
            "Methi / Fenugreek — blood sugar control",
            "Curry leaves — hair & gut health",
            "Ashwagandha — stress & energy",
        ],

        "regional_cuisines": [
            "North Indian (Punjab, UP, Delhi, Haryana)",
            "South Indian (Tamil Nadu, Kerala, Karnataka, Andhra)",
            "Bengali (West Bengal, Odisha)",
            "Gujarati & Rajasthani (light, wholesome)",
            "Maharashtrian (balanced, diverse)",
            "Coastal & Goan (seafood-rich, coconut-based)",
            "Northeast Indian (fermented foods, rice-rich)",
        ],

        "healthy_cooking_methods": [
            "Steaming (best for nutrients)", "Pressure cooking",
            "Sautéing with minimal oil (Tadka)", "Slow cooking / Dum",
            "Fermenting (enhances probiotics)", "Grilling / Tandoor",
        ],

        # Set True to automatically include spice health benefits
        "include_spice_benefits": True,

        # Set True to give advice for festival foods (Navratri, Diwali, etc.)
        "include_festival_foods": True,

        # Set True to provide fasting alternatives (Ekadashi, Navratri fast, etc.)
        "include_fasting_options": True,

        # Prefer these millets when suggesting grains
        "preferred_millets": ["Bajra", "Jowar", "Ragi", "Foxtail Millet", "Kodo Millet"],
    },

    # ── SAFETY RULES ────────────────────────────────────────────────────────
    # These guardrails are non-negotiable — agent will always follow them
    "safety_rules": [
        "ALWAYS recommend consulting a Registered Dietitian or doctor for medical conditions",
        "NEVER diagnose diseases, disorders, or prescribe medications or supplements",
        "FLAG calorie plans below 1200 kcal/day with a bold health warning",
        "ALWAYS ask about food allergies and intolerances before meal planning",
        "REMIND pregnant and breastfeeding women to consult their OB-GYN first",
        "DO NOT provide specific supplement/medication dosages",
        "WARN users with diabetes about high-glycemic foods explicitly",
        "ALERT users with hypertension about high-sodium recipes",
        "EMPHASIZE moderation over extreme elimination diets",
        "INCLUDE mindful eating and mental health aspects when relevant",
        "NEVER promote unhealthy rapid weight loss (more than 1 kg/week)",
    ],

    # ── RESPONSE FORMAT ──────────────────────────────────────────────────────
    "response_format": {
        "use_emojis":               True,    # Set False for clinical/formal tone
        "use_bullet_points":        True,    # Structured lists for meal plans
        "include_calories":         True,    # Show kcal for foods mentioned
        "include_portions":         True,    # Indian portions (katori, roti count)
        "include_prep_tips":        True,    # Cooking tips & shortcuts
        "include_health_benefits":  True,    # Why this food is good
        "end_with_tip":             True,    # Close with a daily nutrition tip
        "max_tokens":               1024,    # Max response length
    },

    # ── MEAL PLANNING DEFAULTS ────────────────────────────────────────────────
    "meal_planning": {
        "meals_per_day":    5,    # Breakfast, Mid-morning, Lunch, Snack, Dinner
        "water_intake_ml":  2500, # Daily water target (ml)
        "calorie_ranges": {
            "weight_loss":  "1200–1500 kcal/day",
            "maintenance":  "1600–2000 kcal/day",
            "weight_gain":  "2200–2800 kcal/day",
            "athletic":     "2500–3500 kcal/day",
        },
        "include_water_reminders": True,
        "include_exercise_pairing": True,
    },

    # ── GREETING MESSAGE ─────────────────────────────────────────────────────
    # Shown as the first message when chat opens
    "greeting": """🌿 **Namaste! I'm NutriBot — your AI Nutrition Expert!**

I'm powered by **IBM Watsonx.ai (Granite)** and here to be your personal wellness companion.

**Here's what I can help you with:**
🥗 Personalized Indian nutrition plans & meal ideas
📊 Calorie counting & macro-nutrient analysis
🍱 Daily & weekly meal planning (veg / non-veg / vegan)
👨‍👩‍👧 Family diet recommendations for all age groups
💪 Weight management strategies
🌿 Ayurvedic food wisdom & superfood benefits
🎯 Goal-specific plans (diabetes, PCOS, thyroid, sports)

**To get started**, tell me:
- Your health goal (lose weight, gain muscle, manage diabetes, etc.)
- Your dietary preference (vegetarian, vegan, non-veg)
- Any health conditions or allergies

Or simply ask me anything about food and nutrition!

---
*⚠️ Disclaimer: I'm an AI assistant. Always consult a qualified healthcare professional before making significant dietary changes.*""",
}


# ══════════════════════════════════════════════════════════════════════════════
#  🚀 FLASK APPLICATION
# ══════════════════════════════════════════════════════════════════════════════
app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(32))

# In-memory stores (replace with a database for production)
family_profiles_store: dict = {}
chat_histories_store:  dict = {}


# ══════════════════════════════════════════════════════════════════════════════
#  🤖 IBM WATSONX.AI — GRANITE MODEL INTEGRATION
# ══════════════════════════════════════════════════════════════════════════════
def get_watsonx_model():
    """
    Initialize IBM Watsonx.ai Granite model.
    Reads credentials from .env file (IBM_API_KEY, WATSONX_PROJECT_ID, etc.)
    """
    try:
        from ibm_watsonx_ai import Credentials
        from ibm_watsonx_ai.foundation_models import ModelInference
        from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

        api_key    = os.getenv("IBM_API_KEY")
        project_id = os.getenv("WATSONX_PROJECT_ID")
        url        = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
        model_id   = os.getenv("WATSONX_MODEL_ID", "ibm/granite-3-8b-instruct")

        if not api_key or not project_id:
            raise ValueError("IBM_API_KEY or WATSONX_PROJECT_ID not set in .env file")

        credentials = Credentials(url=url, api_key=api_key)

        model = ModelInference(
            model_id=model_id,
            credentials=credentials,
            project_id=project_id,
            params={
                GenParams.MAX_NEW_TOKENS:     AGENT_INSTRUCTIONS["response_format"]["max_tokens"],
                GenParams.TEMPERATURE:        0.72,
                GenParams.TOP_P:              0.90,
                GenParams.TOP_K:              50,
                GenParams.REPETITION_PENALTY: 1.10,
            }
        )
        return model

    except ImportError:
        log.error("ibm-watsonx-ai not installed. Run: pip install ibm-watsonx-ai")
        return None
    except Exception as e:
        log.error(f"Watsonx initialization error: {e}")
        return None


def build_system_prompt(user_profile: dict = None) -> str:
    """
    Build the full system prompt from AGENT_INSTRUCTIONS.
    Optionally injects user profile for personalization.
    """
    ai = AGENT_INSTRUCTIONS
    fp = ai["indian_food_preferences"]

    specializations = "\n".join(f"  • {s}" for s in ai["specializations"])
    safety_rules    = "\n".join(f"  ⛔ {r}" for r in ai["safety_rules"])
    staples         = ", ".join(fp["staple_foods"][:8])
    snacks          = ", ".join(fp["healthy_snacks"][:6])
    superfoods      = "\n".join(f"  🌿 {s}" for s in fp["indian_superfoods"][:6])
    style           = "\n".join(f"  - {s}" for s in ai["communication_style"])

    profile_block = ""
    if user_profile:
        profile_block = f"""
━━━ ACTIVE USER PROFILE ━━━
  Name      : {user_profile.get('name', 'User')}
  Age       : {user_profile.get('age', 'Not specified')} years
  Gender    : {user_profile.get('gender', 'Not specified')}
  Weight    : {user_profile.get('weight', '?')} kg
  Height    : {user_profile.get('height', '?')} cm
  Goal      : {user_profile.get('goal', 'General wellness')}
  Diet Type : {user_profile.get('diet_type', 'Vegetarian')}
  Allergies : {user_profile.get('allergies', 'None')}
  Conditions: {user_profile.get('conditions', 'None')}
  Activity  : {user_profile.get('activity', 'Moderate')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Personalize ALL responses for this specific user's profile above.
"""

    return f"""You are {ai['persona_name']}, a {ai['persona_role']}.
Powered by IBM Watsonx.ai Granite. Version {ai['version']}.

TONE: {ai['tone']}

COMMUNICATION STYLE:
{style}

YOUR EXPERTISE:
{specializations}

INDIAN FOOD KNOWLEDGE:
  Staple Foods : {staples}
  Healthy Snacks: {snacks}
  Indian Superfoods:
{superfoods}

  Cooking Methods: {', '.join(fp['healthy_cooking_methods'][:4])}
  Regional Cuisines: {', '.join(fp['regional_cuisines'][:4])}

SAFETY RULES — ALWAYS FOLLOW:
{safety_rules}

RESPONSE FORMAT RULES:
  - Use emojis: {'Yes' if ai['response_format']['use_emojis'] else 'No'}
  - Include calorie counts for foods mentioned: Yes
  - Use Indian portion sizes (katori, roti, tablespoon): Yes
  - Include health benefits of recommended foods: Yes
  - End every response with a 💡 Nutrition Tip: Yes
  - Be encouraging and positive, never judgmental about food choices

{profile_block}
Always respond helpfully. If unsure, say so and recommend consulting a professional."""


def call_watsonx_ai(prompt: str, system_prompt: str) -> str:
    """
    Unified function to call IBM Watsonx.ai.
    Tries the Chat API first (Granite 3.x), falls back to text generation.
    """
    model = get_watsonx_model()

    if model is None:
        return (
            "⚠️ **Configuration Required**\n\n"
            "The IBM Watsonx.ai connection is not set up yet.\n\n"
            "**Steps to fix:**\n"
            "1. Copy `.env.example` to `.env`\n"
            "2. Add your `IBM_API_KEY` from IBM Cloud Console\n"
            "3. Add your `WATSONX_PROJECT_ID` from Watson Studio\n"
            "4. Restart the Flask server\n\n"
            "📖 See `README.md` for detailed setup instructions."
        )

    # ── Try Chat API (Granite 3.x instruction-tuned models) ──────────────
    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": prompt}
        ]
        result = model.chat(messages=messages)
        if result and "choices" in result:
            return result["choices"][0]["message"]["content"].strip()
    except AttributeError:
        pass  # Fall through to text generation
    except Exception as e:
        log.warning(f"Chat API failed, trying text generation: {e}")

    # ── Fallback: Text Generation API (older Granite models) ─────────────
    try:
        full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\n{AGENT_INSTRUCTIONS['persona_name']}:"
        result = model.generate_text(prompt=full_prompt)
        return result.strip() if result else "I could not generate a response. Please try again."
    except Exception as e:
        log.error(f"Watsonx text generation failed: {e}")
        return f"⚠️ Error communicating with IBM Watsonx.ai: {str(e)}\n\nPlease verify your credentials in `.env` file."


# ── Specialised AI Helper Functions ──────────────────────────────────────────

def chat_with_agent(message: str, history: list, profile: dict = None) -> str:
    """Chat endpoint logic — maintains conversation context."""
    system_prompt = build_system_prompt(profile)

    # Build recent conversation context (last 4 exchanges)
    context = ""
    for msg in history[-8:]:
        role  = "User" if msg["role"] == "user" else AGENT_INSTRUCTIONS["persona_name"]
        context += f"{role}: {msg['content']}\n"

    prompt = f"CONVERSATION HISTORY:\n{context}\n\nCurrent question: {message}"
    return call_watsonx_ai(prompt, system_prompt)


def generate_meal_plan_ai(profile: dict, duration: str = "weekly") -> str:
    """Generate a personalized Indian meal plan."""
    system_prompt = build_system_prompt(profile)
    ai = AGENT_INSTRUCTIONS

    cal_target = profile.get("calories", "1800")
    diet_type  = profile.get("diet_type", "Vegetarian")
    goal       = profile.get("goal", "Healthy lifestyle")

    prompt = f"""Generate a detailed {duration} Indian nutrition meal plan.

USER SPECIFICS:
- Name: {profile.get('name', 'User')}
- Age: {profile.get('age', '25')} years | Gender: {profile.get('gender', 'Not specified')}
- Weight: {profile.get('weight', '65')} kg | Height: {profile.get('height', '165')} cm
- Goal: {goal}
- Diet Type: {diet_type}
- Calorie Target: {cal_target} kcal/day
- Health Conditions: {profile.get('conditions', 'None')}
- Food Allergies: {profile.get('allergies', 'None')}
- Activity Level: {profile.get('activity', 'Moderate')}

PLAN REQUIREMENTS:
1. Structure: Breakfast → Mid-morning Snack → Lunch → Evening Snack → Dinner
2. Include Indian foods: Dal, Roti/Rice, Sabzi, Curd, Seasonal fruits
3. Specify exact portions (e.g., "2 rotis", "1 katori dal", "1 cup rice")
4. Include approximate calories per meal and daily total
5. Add quick preparation tips for each meal
6. Recommend daily water intake
7. Include one superfood tip per day
8. Keep variety across the {duration} (don't repeat same meals daily)

Format the plan clearly with meal sections and emoji headers."""

    return call_watsonx_ai(prompt, system_prompt)


def analyze_nutrition_ai(food_items: str) -> str:
    """Analyze nutritional content of a meal or food list."""
    system_prompt = build_system_prompt()

    prompt = f"""Perform a detailed nutritional analysis of this meal/food:

{food_items}

Provide a comprehensive breakdown:
🔥 **Total Calories** (approximate)
💪 **Protein** (grams) — sources and benefits
🌾 **Carbohydrates** (grams) — type (simple/complex)
🫒 **Healthy Fats** (grams) — quality assessment
🌿 **Dietary Fiber** (grams)
🧂 **Sodium** (mg) — note if high
🍊 **Key Vitamins** — top 3 present
⚙️ **Key Minerals** — top 3 present
✅ **Nutritional Highlights** — what this meal does well
⚠️ **Nutritional Gaps** — what's missing or excessive
💡 **Healthy Modifications** — 3 ways to improve this meal

Use clear formatting with emoji headers. Be specific with Indian food items."""

    return call_watsonx_ai(prompt, system_prompt)


def get_quick_nutrition_tip_ai() -> str:
    """Get a daily AI-powered nutrition tip."""
    import random
    topics = [
        "Indian spices with medicinal benefits",
        "best pre-workout Indian foods",
        "high-protein vegetarian Indian foods",
        "foods to improve digestion in Indian diet",
        "weight loss tips with Indian foods",
        "calcium-rich foods for Indian vegetarians",
        "iron-rich vegetarian Indian foods",
        "foods to manage blood sugar naturally",
    ]
    topic = random.choice(topics)
    system_prompt = build_system_prompt()
    prompt = f"Give ONE powerful, specific, actionable nutrition tip about: {topic}. Keep it under 80 words. Start with a relevant emoji."
    return call_watsonx_ai(prompt, system_prompt)


# ══════════════════════════════════════════════════════════════════════════════
#  📡 FLASK API ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    """Serve the main single-page application."""
    return render_template(
        "index.html",
        greeting=AGENT_INSTRUCTIONS["greeting"],
        agent_name=AGENT_INSTRUCTIONS["persona_name"],
    )


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check — also confirms Watsonx config status."""
    api_key    = os.getenv("IBM_API_KEY", "")
    project_id = os.getenv("WATSONX_PROJECT_ID", "")
    model_id   = os.getenv("WATSONX_MODEL_ID", "ibm/granite-3-8b-instruct")
    configured = bool(api_key and project_id and "your_" not in api_key)

    return jsonify({
        "status":      "healthy",
        "agent":       AGENT_INSTRUCTIONS["persona_name"],
        "model":       model_id,
        "configured":  configured,
        "timestamp":   datetime.now().isoformat(),
        "version":     AGENT_INSTRUCTIONS["version"],
    })


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Main chat endpoint.
    Accepts: { message, session_id, profile }
    Returns: { response, session_id, timestamp }
    """
    data       = request.get_json(silent=True) or {}
    message    = (data.get("message") or "").strip()
    session_id = data.get("session_id") or str(uuid.uuid4())
    profile    = data.get("profile") or None

    if not message:
        return jsonify({"error": "Message cannot be empty"}), 400

    # Initialise or retrieve chat history
    if session_id not in chat_histories_store:
        chat_histories_store[session_id] = []
    history = chat_histories_store[session_id]

    # Store user message
    history.append({"role": "user", "content": message, "ts": datetime.now().isoformat()})

    # Get AI response
    response = chat_with_agent(message, history, profile)

    # Store assistant response
    history.append({"role": "assistant", "content": response, "ts": datetime.now().isoformat()})

    # Keep history manageable (last 20 messages)
    if len(history) > 20:
        chat_histories_store[session_id] = history[-20:]

    return jsonify({
        "response":   response,
        "session_id": session_id,
        "timestamp":  datetime.now().isoformat(),
    })


@app.route("/api/meal-plan", methods=["POST"])
def meal_plan():
    """
    Generate a personalized meal plan.
    Accepts: { profile, duration }   duration = "daily" | "weekly"
    """
    data     = request.get_json(silent=True) or {}
    profile  = data.get("profile", {})
    duration = data.get("duration", "weekly")

    if not profile:
        return jsonify({"error": "Profile data is required"}), 400

    plan = generate_meal_plan_ai(profile, duration)

    return jsonify({
        "meal_plan":    plan,
        "duration":     duration,
        "generated_at": datetime.now().isoformat(),
        "profile_name": profile.get("name", "User"),
    })


@app.route("/api/nutrition-analysis", methods=["POST"])
def nutrition_analysis():
    """
    Analyze nutrition of provided food items.
    Accepts: { foods }
    """
    data  = request.get_json(silent=True) or {}
    foods = (data.get("foods") or "").strip()

    if not foods:
        return jsonify({"error": "Please provide food items to analyze"}), 400

    analysis = analyze_nutrition_ai(foods)

    return jsonify({
        "analysis":    analysis,
        "foods":       foods,
        "analyzed_at": datetime.now().isoformat(),
    })


@app.route("/api/bmi", methods=["POST"])
def calculate_bmi():
    """
    BMI calculator with Indian body composition context.
    Accepts: { weight_kg, height_cm, age, gender }
    """
    data = request.get_json(silent=True) or {}

    try:
        weight = float(data.get("weight", 0))
        height = float(data.get("height", 0))
        age    = int(data.get("age", 25))
        gender = data.get("gender", "female").lower()
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid input values"}), 400

    if weight <= 0 or height <= 0:
        return jsonify({"error": "Weight and height must be positive values"}), 400

    height_m = height / 100.0
    bmi = round(weight / (height_m ** 2), 1)

    # ── BMI Classification (Asian / Indian thresholds) ─────────────────────
    # WHO Asia-Pacific guidelines use lower cutoffs for South Asians
    if bmi < 18.5:
        category   = "Underweight"
        risk       = "Moderate Risk — May indicate nutritional deficiency"
        color      = "#3b82f6"
        advice     = "Focus on calorie-dense nutritious foods. Add nuts, dairy, legumes."
        emoji      = "📉"
    elif 18.5 <= bmi < 23.0:
        category   = "Normal Weight"
        risk       = "Low Risk — Healthy range for South Asians"
        color      = "#16a34a"
        advice     = "Maintain your current habits. Focus on balanced nutrition."
        emoji      = "✅"
    elif 23.0 <= bmi < 27.5:
        category   = "Overweight"
        risk       = "Moderate Risk — South Asian threshold (international: 25)"
        color      = "#f59e0b"
        advice     = "Reduce refined carbs, increase vegetables and physical activity."
        emoji      = "⚠️"
    else:
        category   = "Obese"
        risk       = "High Risk — Consult a doctor for personalized guidance"
        color      = "#ef4444"
        advice     = "Medical supervision recommended. Gradual lifestyle changes are key."
        emoji      = "🚨"

    # ── Ideal weight (BMI 18.5–23 for South Asians) ────────────────────────
    ideal_min = round(18.5 * (height_m ** 2), 1)
    ideal_max = round(23.0 * (height_m ** 2), 1)

    # ── BMR — Harris-Benedict Equation ─────────────────────────────────────
    if gender == "male":
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    bmr = round(bmr)

    return jsonify({
        "bmi":              bmi,
        "category":         category,
        "risk":             risk,
        "color":            color,
        "emoji":            emoji,
        "advice":           advice,
        "ideal_weight": {
            "min": ideal_min,
            "max": ideal_max,
        },
        "bmr": bmr,
        "daily_calories": {
            "sedentary":         round(bmr * 1.20),
            "lightly_active":    round(bmr * 1.375),
            "moderately_active": round(bmr * 1.550),
            "very_active":       round(bmr * 1.725),
            "extremely_active":  round(bmr * 1.900),
        },
        "note": "Asian/South Asian BMI thresholds applied (overweight: ≥23, obese: ≥27.5)",
    })


@app.route("/api/family-profiles", methods=["GET"])
def get_profiles():
    """Get all family profiles."""
    return jsonify(list(family_profiles_store.values()))


@app.route("/api/family-profile", methods=["POST"])
def upsert_profile():
    """Add or update a family member profile."""
    data       = request.get_json(silent=True) or {}
    profile_id = data.get("id") or str(uuid.uuid4())
    data["id"] = profile_id
    data["saved_at"] = datetime.now().isoformat()
    family_profiles_store[profile_id] = data
    return jsonify({"success": True, "profile": data})


@app.route("/api/family-profile/<profile_id>", methods=["DELETE"])
def delete_profile(profile_id: str):
    """Delete a family member profile."""
    if profile_id in family_profiles_store:
        del family_profiles_store[profile_id]
        return jsonify({"success": True})
    return jsonify({"error": "Profile not found"}), 404


@app.route("/api/quick-tips", methods=["GET"])
def quick_tips():
    """Return 3 daily nutrition tips (mix of static + optional AI tip)."""
    static_tips = [
        {"tip": "Drink a glass of water 30 min before each meal to improve digestion 💧", "cat": "Hydration"},
        {"tip": "Add methi (fenugreek) seeds to your dough — great for blood sugar control 🌿", "cat": "Indian Superfoods"},
        {"tip": "Swap white rice with millets (Bajra/Jowar) 2–3 times a week for better fiber 🌾", "cat": "Smart Swaps"},
        {"tip": "Include a handful of mixed nuts (Badaam, Akhrot) as your mid-morning snack 🥜", "cat": "Snacking"},
        {"tip": "Start your day with warm haldi doodh (turmeric milk) — anti-inflammatory magic 🧡", "cat": "Morning Ritual"},
        {"tip": "Eat the rainbow! Include 5 different colored vegetables daily for diverse nutrients 🌈", "cat": "Vegetables"},
        {"tip": "Have your last meal 2–3 hours before bedtime for better sleep and digestion 🌙", "cat": "Meal Timing"},
        {"tip": "Soak almonds overnight and eat them in the morning for better nutrient absorption 🌅", "cat": "Preparation Tips"},
        {"tip": "Replace sugar in chai with a pinch of cinnamon for a warming, blood-sugar-friendly drink 🍵", "cat": "Smart Swaps"},
        {"tip": "Include one cup of curd/dahi daily for gut health and calcium — your digestive system will thank you! 🥛", "cat": "Probiotics"},
        {"tip": "Chew each bite 20–25 times. Slow eating improves digestion and helps you eat less 🧘", "cat": "Mindful Eating"},
        {"tip": "Amla (Indian Gooseberry) has 20x more Vitamin C than oranges — try fresh amla chutney! 🫒", "cat": "Indian Superfoods"},
    ]
    import random
    selected = random.sample(static_tips, min(3, len(static_tips)))
    return jsonify(selected)


@app.route("/api/agent-config", methods=["GET"])
def agent_config():
    """Expose non-sensitive agent configuration (for frontend display)."""
    ai = AGENT_INSTRUCTIONS
    return jsonify({
        "persona_name":     ai["persona_name"],
        "persona_role":     ai["persona_role"],
        "powered_by":       ai["powered_by"],
        "tone":             ai["tone"],
        "specializations":  ai["specializations"][:5],
        "meal_planning":    ai["meal_planning"],
    })


# ══════════════════════════════════════════════════════════════════════════════
#  🏃 ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    port  = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    ai = AGENT_INSTRUCTIONS
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║          🌿 AI Nutrition Agent — Starting Up                    ║
╠══════════════════════════════════════════════════════════════════╣
║  Agent    : {ai['persona_name']:<51}║
║  Role     : {ai['persona_role'][:51]:<51}║
║  Model    : IBM Watsonx.ai — {os.getenv('WATSONX_MODEL_ID', 'ibm/granite-3-8b-instruct')[:21]:<30}║
║  Port     : http://localhost:{port:<34}║
║  Debug    : {str(debug):<51}║
╠══════════════════════════════════════════════════════════════════╣
║  ✅ Configured: IBM_API_KEY & WATSONX_PROJECT_ID in .env?       ║
║  📖 See README.md for IBM Cloud setup guide                     ║
╚══════════════════════════════════════════════════════════════════╝
""")

    app.run(host="0.0.0.0", port=port, debug=debug)
