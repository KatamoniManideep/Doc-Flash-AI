import streamlit as st
import os
from ai_engine import split_markdown_by_headers, extract_flashcards_from_chunk
import genanki
from pypdf import PdfReader

st.set_page_config(page_title="DocFlash AI", page_icon="", layout="wide")

st.markdown("""
<style>
    /* Minimalist Card Shell Styling */
    .flashcard-canvas {
        background-color: #0f172a;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 40px;
        color: #f8fafc;
        min-height: 260px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        margin-bottom: 24px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    .flashcard-back {
        background-color: #020617;
        border-color: #8b5cf6;
    }
    .card-main-text {
        font-size: 1.35rem;
        font-weight: 500;
        line-height: 1.6;
        max-width: 90%;
    }
    .answer-highlight {
        color: #c084fc;
        font-weight: 600;
    }
    .citation-badge {
        margin-top: 24px;
        font-size: 0.85rem;
        color: #64748b;
        background-color: #1e293b;
        padding: 6px 12px;
        border-radius: 20px;
        border: 1px solid #334155;
    }
</style>
""", unsafe_allow_html=True)


def extract_text_from_file(uploaded_file) -> str:
    """Reads uploaded document objects and normalizes them into standard raw string text."""
    filename = uploaded_file.name
    if filename.endswith('.pdf'):
        reader = PdfReader(uploaded_file)
        text_content = ""
        for page in reader.pages:
            text_content += page.extract_text() + "\n"
        return text_content
    else:
        
        return uploaded_file.read().decode("utf-8")

def deduplicate_cards(cards):
    """Return cards in original order with duplicates removed."""
    unique_cards = []
    seen = set()

    for card in cards:
        card_tuple = (
            getattr(card, "front", None),
            getattr(card, "back", None),
            getattr(card, "source_quote", None),
        )
        if card_tuple not in seen:
            seen.add(card_tuple)
            unique_cards.append(card)

    return unique_cards

if "generated_cards" not in st.session_state:
    st.session_state.generated_cards = []
if "current_card_index" not in st.session_state:
    st.session_state.current_card_index = 0
if "is_card_flipped" not in st.session_state:
    st.session_state.is_card_flipped = False


st.title("DocFlash AI")
st.write("---")

left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    st.subheader("Ingestion Sources")
    
    uploaded_files = st.file_uploader(
        "Attach reference documents or text notes:",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True
    )
    
    raw_text_input = st.text_area(
        "Or paste manual notes/markdown text directly here:",
        height=180,
        placeholder="# Subject Title..."
    )
    
    aggregated_source_text = raw_text_input + "\n"
    if uploaded_files:
        for f in uploaded_files:
            aggregated_source_text += extract_text_from_file(f) + "\n"
            
    char_count = len(aggregated_source_text.strip())
    MAX_CHAR_LIMIT = 15000 
    
    if char_count > MAX_CHAR_LIMIT:
        st.error(f" Limit Exceeded! Current payload size: {char_count}/{MAX_CHAR_LIMIT} characters. Please shorten inputs.")
        generate_clicked = st.button("Generate Flash cards", disabled=True, use_container_width=True)
    else:
        st.caption(f"Payload density status: {char_count} / {MAX_CHAR_LIMIT} total character count capacity.")
        generate_clicked = st.button("Generate Flash cards", disabled=(char_count == 0), use_container_width=True)

    if generate_clicked:
        with st.spinner("Compiling structural sources and extracting atomic concepts..."):
            fragments = split_markdown_by_headers(aggregated_source_text)
            
            raw_deck = []
            for chunk in fragments:
                if chunk.strip():
                    extracted = extract_flashcards_from_chunk(chunk)
                    raw_deck.extend(extracted)
                    
            sanitized_deck = deduplicate_cards(raw_deck)
            
            st.session_state.generated_cards = sanitized_deck
            st.session_state.current_card_index = 0
            st.session_state.is_card_flipped = False
            st.success(f"Successfully compiled {len(sanitized_deck)} minimalist study cards!")


with right_col:
    st.subheader("Flashcards")
    
    if not st.session_state.generated_cards:
        st.info("No active cards loaded. Attach files or insert reference text strings on the left to activate your deck.")
    else:
        total_cards = len(st.session_state.generated_cards)
        current_idx = st.session_state.current_card_index
        active_card = st.session_state.generated_cards[current_idx]
        
        st.write(f"Card {current_idx + 1} of {total_cards}")
        
        if not st.session_state.is_card_flipped:
            st.markdown(f"""
            <div class="flashcard-canvas">
                <div class="card-main-text">{active_card.front}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            answer_text = active_card.back if active_card.back else "[Cloze Insertion State]"
            st.markdown(f"""
            <div class="flashcard-canvas flashcard-back">
                <div class="card-main-text">Answer: <span class="answer-highlight">{answer_text}</span></div>
                <div class="citation-badge">📍 Grounded Context: "{active_card.source_quote}"</div>
            </div>
            """, unsafe_allow_html=True)
            
        if st.button("Flip Card", use_container_width=True):
            st.session_state.is_card_flipped = not st.session_state.is_card_flipped
            st.rerun()
            
        st.write("")
        
        arrow_left_col, center_gap, arrow_right_col = st.columns([1, 2, 1])
        
        with arrow_left_col:
            prev_disabled = (current_idx == 0)
            if st.button("<- Previous", disabled=prev_disabled, use_container_width=True):
                st.session_state.current_card_index -= 1
                st.session_state.is_card_flipped = False # Auto reset flip look back to question state
                st.rerun()
                
        with arrow_right_col:
            next_disabled = (current_idx == total_cards - 1)
            if st.button("Next ->", disabled=next_disabled, use_container_width=True):
                st.session_state.current_card_index += 1
                st.session_state.is_card_flipped = False
                st.rerun()
                
        st.write("---")
        
        st.subheader("Export Distribution")
        if st.button("Compile and Package Deck (.apkg)", use_container_width=True):
            MODEL_ID = 1607342921
            DECK_ID = 2059348210
            
            anki_model = genanki.Model(
                MODEL_ID, 'DocFlash Minimalist Model',
                fields=[{'name': 'Question'}, {'name': 'Answer'}, {'name': 'Source'}],
                templates=[{'name': 'Card 1', 'qfmt': '<div style="color:#38bdf8; font-size:1.2rem; text-align:center;">{{Question}}</div>', 
                            'afmt': '{{FrontSide}}<hr><div style="color:#c084fc; font-size:1.1rem; text-align:center;">{{Answer}}</div><br><small style="color:#64748b;">Source: {{Source}}</small>'}]
            )
            
            export_deck = genanki.Deck(DECK_ID, 'DocFlash AI :: Active Recall Deck')
            for c in st.session_state.generated_cards:
                note = genanki.Note(model=anki_model, fields=[c.front, c.back if c.back else "", c.source_quote])
                export_deck.add_note(note)
                
            output_filepath = "export_deck.apkg"
            genanki.Package(export_deck).write_to_file(output_filepath)
            
            with open(output_filepath, "rb") as file:
                st.download_button(
                    label=" Download Native Anki Package File",
                    data=file,
                    file_name="docflash_study_deck.apkg",
                    mime="application/octet-stream",
                    use_container_width=True
                )