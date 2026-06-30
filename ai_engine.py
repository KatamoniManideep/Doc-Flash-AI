import os
import re
from typing import List,Literal
from pydantic import BaseModel,Field
from google import genai
from google.genai import types

from dotenv import load_dotenv
load_dotenv()

client = genai.Client()


class Flashcard(BaseModel):
    card_type: Literal["Basic", "Cloze"] = Field(
        ..., 
        description="Use 'Basic' for Q&A format. Use 'Cloze' for fill-in-the-blank text syntax like: 'The key keyword in Python used to handle exceptions is {{c1::try}}.'"
    )
    front: str = Field(..., description="The question or the sentence containing the Cloze hidden text deletion bracket.")
    back: str = Field(
        ..., 
        description=(
            "The exact answer text. For 'Basic' cards, this is the answer to the question. "
            "For 'Cloze' cards, provide the exact word(s) that were wrapped inside the {{c1::...}} brackets "
            "so the user can see the hidden answer when they flip the card in the preview UI."
        )
    )
    source_quote: str = Field(..., description="The exact reference sentence or phrase copied directly from the input text used to ground this card.")
 

class FlashcardDeck(BaseModel):
    deck_name: str = Field(..., description="A short name for the topic.")
    cards: List[Flashcard] = Field(
        ..., 
        description=(
            "A strictly curated list of distinct, unique flashcards. "
            "CRITICAL LIMIT: Generate at most 1-2 highly important cards per paragraph. "
            "If the input text block is extremely short (under 4 sentences), generate MAXIMUM 1 or 2 cards total. "
            "Do not create repetitive questions, minor phrasing variants, or split a single sentence into multiple cards."
        )
    )

def split_markdown_by_headers(text:str)-> List[str]:
    
    tokens = re.split(r'(^#{1,2}\s+.*$)', text, flags=re.MULTILINE)

    chunks=[]
    current_chunk=""

    for token in tokens:
        if not token.strip():
            continue
        if token.strip().startswith("#"):
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk=token
        else:
            current_chunk+="\n"+token

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def extract_flashcards_from_chunk(chunk_text: str) -> List[Flashcard]:

    system_instruction = (
        "You are an elite academic instructor specializing in active recall pedagogy. "
        "Analyze the provided text fragment. Extract core factual rules, architectural concepts, "
        "or code syntaxes into high-quality flashcards. Prioritize atomic concepts (one fact per card). "
        "Every single card must be strictly grounded—extract the exact 'source_quote' from the text."
    )

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Extract flashcards from this text:\n\n{chunk_text}",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=FlashcardDeck,
                temperature=0.2,
            ),
        )

        structured_data = getattr(response, "parsed", None)
        if isinstance(structured_data, FlashcardDeck):
            return structured_data.cards
        if isinstance(structured_data, list):
            return structured_data
        return []
    
    except Exception as e:
        print(f"Failed processing chunk due to API or Validation variance: {e}")
        return []

if __name__ == "__main__":
    print("Initializing AI Pipeline...")
    
    sample_markdown_input= """
# Python Advanced Memory Management

## Understanding Garbage Collection
Python uses reference counting as its primary mechanism for memory management. When an object's reference count drops to zero, it is instantly deallocated. However, reference counting alone cannot detect reference cycles. To solve this, Python implements a cyclic garbage collector using the `gc` module which periodically searches for isolated container objects.

## Core Variable Reference Assignment
When you assign a variable in Python like `a = [1, 2]`, you are not creating a box named 'a' containing data. Instead, you are creating a pointer reference named 'a' that points to an object in the heap memory containing the list structure.
    """

    fragments = split_markdown_by_headers(sample_markdown_input)
    print(f"Successfully sliced text input into {len(fragments)} structural blocks.")

    master_extracted_cards = []

    for i, fragment in enumerate(fragments, start=1):
        print(f"Processing Block {i}/{len(fragments)} through Gemini...")
        cards = extract_flashcards_from_chunk(fragment)
        print(f"Extracted {len(cards)} valid flashcards from Block {i}.")
        master_extracted_cards.extend(cards)
        
    print("\n === MASTER EXTRACTED CARDS SUMMARY ===")
    for idx, card in enumerate(master_extracted_cards, start=1):
        print(f"\n[Card #{idx}] Type: {card.card_type}")
        print(f"  Front: {card.front}")
        print(f"  Back : {card.back}")
        print(f"  Quote: \"{card.source_quote}\"")