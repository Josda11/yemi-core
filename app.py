import streamlit as st
import ollama
from gtts import gTTS
import tempfile
import json
import re

# Configuration de la page
st.set_page_config(page_title="Yemi Core", page_icon="🌍", layout="centered")
st.title("🌍 Yemi Core — Apprends l'anglais avec l'IA")
st.markdown("Saisis une phrase ou un paragraphe en français pour générer une leçon complète.")

# Champ de saisie
texte_fr = st.text_area("✍️ Ton texte en français :", height=150)

if st.button("🚀 Générer la leçon"):
    if not texte_fr.strip():
        st.warning("Veuillez saisir un texte avant de continuer.")
    else:
        with st.spinner("L'IA analyse ton texte..."):

            # Prompt principal
            prompt = f"""
Tu es un professeur d'anglais expert. À partir du texte français suivant, tu dois :
1. Traduire le texte en anglais naturel et fluide.
2. Extraire 2 ou 3 règles de grammaire ou de vocabulaire clés issues de la traduction.
3. Générer un mini-QCM de 3 questions basé sur le contenu.

Texte français : "{texte_fr}"

Réponds UNIQUEMENT en JSON valide, sans explication, sans balises markdown, avec cette structure exacte :
{{
  "traduction": "...",
  "regles": [
    {{"titre": "...", "explication": "..."}},
    {{"titre": "...", "explication": "..."}}
  ],
  "quiz": [
    {{
      "question": "...",
      "options": ["A. ...", "B. ...", "C. ..."],
      "reponse": "A"
    }}
  ]
}}
"""

            try:
                # Appel à Ollama
                response = ollama.chat(
                    model="llama3",
                    messages=[{"role": "user", "content": prompt}]
                )
                raw = response["message"]["content"]

                # Nettoyage du JSON
                raw = re.sub(r"```json|```", "", raw).strip()
                data = json.loads(raw)

                traduction = data.get("traduction", "")
                regles = data.get("regles", [])
                quiz = data.get("quiz", [])

                # Affichage de la traduction
                st.subheader("📝 Traduction")
                st.success(traduction)

                # Génération audio
                st.subheader("🔊 Audio de la traduction")
                tts = gTTS(text=traduction, lang='en')
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                    tts.save(f.name)
                    st.audio(f.name, format="audio/mp3")

                # Affichage des règles
                st.subheader("📚 Règles de grammaire / Vocabulaire")
                for regle in regles:
                    with st.expander(f"📌 {regle['titre']}"):
                        st.write(regle["explication"])

                # Quiz
                st.subheader("🧠 Mini Quiz")
                if "quiz_reponses" not in st.session_state:
                    st.session_state.quiz_reponses = {}

                for i, q in enumerate(quiz):
                    st.markdown(f"**Question {i+1} : {q['question']}**")
                    choix = st.radio(
                        f"Choix {i+1}",
                        q["options"],
                        key=f"q{i}",
                        label_visibility="collapsed"
                    )
                    st.session_state.quiz_reponses[i] = choix

                if st.button("✅ Vérifier mes réponses"):
                    score = 0
                    for i, q in enumerate(quiz):
                        choix = st.session_state.quiz_reponses.get(i, "")
                        if choix.startswith(q["reponse"]):
                            st.success(f"Question {i+1} : ✅ Bonne réponse !")
                            score += 1
                        else:
                            st.error(f"Question {i+1} : ❌ Mauvaise réponse. La bonne réponse était : {q['reponse']}")
                    st.info(f"🎯 Score final : {score}/3")

            except json.JSONDecodeError:
                st.error("L'IA n'a pas retourné un format valide. Réessaie.")
            except Exception as e:
                st.error(f"Erreur : {str(e)}")