# MenuMate AI ??

A multilingual restaurant menu translator powered by locally running AI.

## Features
- Translate menu descriptions into Telugu, Hindi, English, Tamil, Kannada and Malayalam.
- Run AI locally using Ollama and Qwen2.5:1.5B.
- Display translations in individual menu cards.
- Copy and download translated menus.
- Customize the restaurant name.
- Modern, mobile-friendly Streamlit interface.

## Technology
- Python
- Streamlit
- Ollama
- Qwen2.5:1.5B

## Run Locally

1. Install Python and [Ollama](https://ollama.com).
2. Download the model:

   ```bash
   ollama pull qwen2.5:1.5b

   ```

3. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Start the application:

   ```bash
   python -m streamlit run app.py
   ```

5. Open the local URL shown in the terminal.

## Disclaimer
Review AI-generated translations, dish names, ingredients and allergen information before publishing a restaurant menu.

## License
License to be selected.
