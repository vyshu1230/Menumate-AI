
import base64
import re

import ollama
import streamlit as st
import streamlit.components.v1 as components

# ==================================================
# SETTINGS
# ==================================================
MODEL = "qwen2.5:1.5b"

LANGUAGES = {
    "🇮🇳 Telugu": "Telugu",
    "🇮🇳 Hindi": "Hindi",
    "🇬🇧 English": "English",
    "🇮🇳 Tamil": "Tamil",
    "🇮🇳 Kannada": "Kannada",
    "🇮🇳 Malayalam": "Malayalam",
}

HERO_IMAGE = (
    "https://images.unsplash.com/photo-1546069901-ba9599a7e63c"
    "?auto=format&fit=crop&w=1200&q=85"
)

# ==================================================
# PAGE SETUP
# ==================================================
st.set_page_config(
    page_title="MenuMate AI | Smart Menu Translator",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================================================
# MODERN GREEN + CREAM DESIGN
# ==================================================
st.markdown(
    """
    <style>
    :root {
        --green: #286747;
        --dark-green: #194b35;
        --cream: #fbf8ef;
        --soft-green: #edf5e9;
        --text: #26352b;
    }

    .stApp {
        background: #fbf8ef;
        color: #26352b;
    }

    [data-testid="stHeader"] {
        background: rgba(251, 248, 239, 0.92);
    }

    [data-testid="stSidebar"] {
        background: #edf5e9;
        border-right: 1px solid #dce8d7;
    }

    h1, h2, h3, p, label, .stMarkdown {
        color: #26352b;
    }

    h1 {
        letter-spacing: -1.2px;
    }

    .brand-label {
        color: #286747;
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 4px;
    }

    .hero-subtitle {
        color: #637265;
        font-size: 16px;
        line-height: 1.7;
    }

    .feature-chip {
        display: inline-block;
        background: #e7f0e1;
        color: #286747;
        border-radius: 30px;
        padding: 7px 11px;
        margin: 3px 4px 3px 0;
        font-size: 12px;
        font-weight: 600;
    }

    .section-label {
        color: #286747;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    .dish-name {
        color: #194b35;
        font-size: 19px;
        font-weight: 750;
        line-height: 1.4;
    }

    .translation-label {
        color: #66816b;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    .translation-text {
        color: #26352b;
        font-size: 17px;
        line-height: 1.8;
        overflow-wrap: anywhere;
    }

    .stTextArea textarea,
    .stTextInput input {
        background: #ffffff !important;
        color: #26352b !important;
        border: 1px solid #d8e3d3 !important;
        border-radius: 10px !important;
    }

    div[data-baseweb="select"] > div {
        background: #ffffff !important;
        color: #26352b !important;
        border-color: #d8e3d3 !important;
    }

    div.stButton > button,
    div.stDownloadButton > button {
        background: #286747;
        color: white;
        border: 1px solid #286747;
        border-radius: 10px;
        min-height: 45px;
        font-weight: 650;
        transition: background 0.2s ease;
    }

    div.stButton > button:hover,
    div.stDownloadButton > button:hover {
        background: #194b35;
        color: white;
        border-color: #194b35;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff;
        border-color: #e2e9dc !important;
        border-radius: 15px !important;
    }

    [data-testid="stImage"] img {
        border-radius: 16px;
    }

    .footer-text {
        color: #718073;
        text-align: center;
        font-size: 12px;
        padding: 12px 0;
    }

    @media (max-width: 640px) {
        .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        h1 {
            font-size: 30px !important;
        }

        .dish-name {
            font-size: 17px;
        }

        .translation-text {
            font-size: 16px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==================================================
# HELPERS
# ==================================================
def parse_menu(text):
    """Read menu lines in Dish name | Description format."""
    items = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        if "|" in line:
            name, description = line.split("|", 1)
            name = name.strip()
            description = description.strip()
        else:
            name = line
            description = ""

        if name:
            items.append({
                "name": name,
                "description": description,
            })

    return items


def parse_ai_response(response, expected_count):
    """Extract numbered translations from the AI response."""
    lines = [
        line.strip()
        for line in response.splitlines()
        if line.strip()
    ]

    numbered = []

    for line in lines:
        match = re.match(r"^\s*(\d+)[.)\-:]\s*(.*)", line)

        if match:
            number = int(match.group(1))

            if 1 <= number <= expected_count:
                text = match.group(2).strip()

                if text:
                    numbered.append((number, text))

    translations = {}

    for number, text in numbered:
        translations[number] = text

    if len(translations) == expected_count:
        return [translations[i] for i in range(1, expected_count + 1)]

    # Fallback if the AI doesn't follow the requested numbering.
    if len(lines) == expected_count:
        cleaned = [
            re.sub(r"^\s*\d+[.)\-:]\s*", "", line).strip()
            for line in lines
        ]
        return cleaned

    return None


def copy_button(text):
    """Render a browser-side copy button."""
    encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")

    html = """
    <div style="font-family:Arial,sans-serif;">
      <button id="copy-menu"
        style="background:#286747;color:white;border:0;
        border-radius:9px;padding:12px 18px;font-size:14px;
        font-weight:600;cursor:pointer;width:100%;">
        📋 Copy all translations
      </button>
      <div id="copy-status"
        style="font-size:12px;color:#286747;margin-top:6px;"></div>
    </div>
    <script>
      const encodedText = "ENCODED_TEXT";
      const decodedText = decodeURIComponent(
        Array.from(atob(encodedText))
          .map(c => "%" + c.charCodeAt(0).toString(16).padStart(2,"0"))
          .join("")
      );

      document.getElementById("copy-menu").addEventListener("click", async () => {
        const status = document.getElementById("copy-status");

        try {
          await navigator.clipboard.writeText(decodedText);
          status.textContent = "Copied! You can now paste your menu.";
        } catch (error) {
          const area = document.createElement("textarea");
          area.value = decodedText;
          area.style.position = "fixed";
          area.style.left = "-9999px";
          document.body.appendChild(area);
          area.select();

          const success = document.execCommand("copy");
          area.remove();

          status.textContent = success
            ? "Copied! You can now paste your menu."
            : "Copy was blocked. Please use the download button.";
        }
      });
    </script>
    """.replace("ENCODED_TEXT", encoded)

    components.html(html, height=75)


# ==================================================
# SIDEBAR
# ==================================================
with st.sidebar:
    st.markdown("## 🍃 MenuMate AI")
    st.caption("Your multilingual menu companion")

    st.markdown("---")

    restaurant_name = st.text_input(
        "Restaurant name",
        value="My Restaurant",
        max_chars=60,
        help="Personalize the heading of your translated menu.",
    )

    st.markdown("### 🌍 Translation settings")

    language_label = st.selectbox(
        "Translate descriptions into",
        list(LANGUAGES.keys()),
        index=0,
    )

    target_language = LANGUAGES[language_label]

    st.markdown("---")
    st.markdown("### 🤖 Local AI")
    st.write("**Model:** Qwen2.5 1.5B")
    st.write("**Engine:** Ollama")
    st.write("**Processing:** Your computer")

    st.caption(
        "Review translated descriptions before publishing "
        "your restaurant menu."
    )

# ==================================================
# HEADER / HERO
# ==================================================
left, right = st.columns([1.35, 1], gap="large")

with left:
    st.markdown(
        '<div class="brand-label">🍃 SMART MENU TRANSLATOR</div>',
        unsafe_allow_html=True,
    )

    st.title("Every dish deserves to be understood.")

    st.markdown(
        '<div class="hero-subtitle">'
        'Make your restaurant menu easier for everyone to understand. '
        'Translate dish descriptions into regional languages with '
        'AI running locally on your computer.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <span class="feature-chip">🌍 Multilingual</span>
        <span class="feature-chip">🔒 Local AI</span>
        <span class="feature-chip">📱 Mobile-friendly</span>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.image(
        HERO_IMAGE,
        caption="Good food brings everyone together.",
        use_container_width=True,
    )

st.divider()

# ==================================================
# MENU INPUT
# ==================================================
st.markdown(
    '<div class="section-label">STEP 01 · YOUR MENU</div>',
    unsafe_allow_html=True,
)
st.header("Add your dishes")

st.write(
    "Enter one dish per line. Keep the dish name and description "
    "separated with a vertical bar (`|`)."
)

default_menu = (
    "Masala Dosa | Crispy rice crepe filled with spiced potato.\n"
    "Paneer Butter Masala | Paneer in creamy tomato gravy.\n"
    "Idli Sambar | Steamed rice cakes served with lentil stew."
)

menu_text = st.text_area(
    "Menu items",
    value=default_menu,
    height=175,
    placeholder=(
        "Biryani | Fragrant rice cooked with spices.\n"
        "Gulab Jamun | Sweet milk-solid balls in sugar syrup."
    ),
    label_visibility="collapsed",
)

st.caption(
    "Tip: Add up to 10 dishes at a time for a faster translation."
)

translate_clicked = st.button(
    f"🌍 Translate into {target_language}",
    use_container_width=True,
    type="primary",
)

# ==================================================
# TRANSLATION
# ==================================================
if translate_clicked:
    items = parse_menu(menu_text)

    if not items:
        st.warning("Please enter at least one menu item.")

    elif len(items) > 10:
        st.warning(
            "Please translate a maximum of 10 dishes at a time."
        )

    else:
        prompt_lines = []

        for index, item in enumerate(items, start=1):
            description = item["description"] or item["name"]
            prompt_lines.append(f"{index}. {description}")

        prompt = f"""
You are a careful professional restaurant menu translator.

Translate the following {len(items)} food descriptions into {target_language}.

Rules:
- Return exactly {len(items)} numbered lines.
- Use the same numbering from 1 to {len(items)}.
- Translate the description, not the original dish name.
- Keep each translation concise and natural.
- Preserve the original meaning and ingredients.
- Do not invent ingredients, prices, allergens, or dietary claims.
- If a dish name has no description, translate the name naturally.
- Do not include introductions, explanations, or extra lines.

Descriptions:
{chr(10).join(prompt_lines)}
"""

        try:
            with st.spinner(
                "🌿 Your AI chef is translating the menu..."
            ):
                response = ollama.chat(
                    model=MODEL,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    options={
                        "temperature": 0.1,
                        "num_predict": 220,
                    },
                )

            raw_translation = response["message"]["content"].strip()

            translations = parse_ai_response(
                raw_translation,
                len(items),
            )

            if translations:
                st.session_state["menu_results"] = [
                    {
                        "name": item["name"],
                        "description": translations[index],
                    }
                    for index, item in enumerate(items)
                ]

                st.session_state["menu_language"] = target_language
                st.session_state["restaurant_name"] = (
                    restaurant_name.strip() or "My Restaurant"
                )

            else:
                st.warning(
                    "The AI returned an unexpected format. "
                    "Please try translating again."
                )

        except Exception as error:
            st.error(
                "I couldn't connect to Ollama. Make sure Ollama "
                "is running and qwen2.5:1.5b is installed."
            )

            with st.expander("Technical details"):
                st.code(str(error))

# ==================================================
# TRANSLATION CARDS
# ==================================================
if st.session_state.get("menu_results"):
    results = st.session_state["menu_results"]
    result_language = st.session_state["menu_language"]
    result_restaurant = st.session_state["restaurant_name"]

    st.divider()

    st.markdown(
        '<div class="section-label">STEP 02 · YOUR TRANSLATION</div>',
        unsafe_allow_html=True,
    )

    st.title(f"🍽️ {result_restaurant}")
    st.subheader(f"Translated menu · {result_language}")

    st.write(
        f"{len(results)} dish"
        f"{'es' if len(results) != 1 else ''} translated for your guests."
    )

    for index, item in enumerate(results, start=1):
        with st.container(border=True):
            st.markdown(
                f'<div class="translation-label">DISH {index:02d}</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                f'<div class="dish-name">{item["name"]}</div>',
                unsafe_allow_html=True,
            )

            st.markdown("---")

            st.markdown(
                '<div class="translation-label">'
                f'TRANSLATION · {result_language.upper()}'
                '</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                f'<div class="translation-text">'
                f'{item["description"]}'
                '</div>',
                unsafe_allow_html=True,
            )

    full_translation = (
        f"{result_restaurant}\n"
        f"Translated menu: {result_language}\n"
        f"{'=' * 35}\n\n"
        + "\n\n".join(
            f"{index}. {item['name']}\n"
            f"{item['description']}"
            for index, item in enumerate(results, start=1)
        )
    )

    st.markdown("### Save or share your menu")

    copy_button(full_translation)

    st.download_button(
        label="⬇️ Download translated menu (.txt)",
        data=full_translation,
        file_name="menumate_translated_menu.txt",
        mime="text/plain",
        use_container_width=True,
    )

    st.caption(
        "Please verify translations, regional dish names, "
        "ingredients, and food-related details before printing "
        "or publishing your menu."
    )

# ==================================================
# FOOTER
# ==================================================
st.divider()

st.markdown(
    """
    <div class="footer-text">
        🍃 MenuMate AI · Made with Python, Streamlit and Ollama
        <br>
        Helping every guest feel at home, one menu at a time.
    </div>
    """,
    unsafe_allow_html=True,
)
