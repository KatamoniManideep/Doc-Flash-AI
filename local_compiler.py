import genanki
import random


MODEL_ID = 1607342921
DECK_ID = 2059348210


notebook_lm_style_model = genanki.Model(
    MODEL_ID,
    'NotebookLM Minimalist Dark Model',
    fields=[
        {'name': 'Question'},
        {'name': 'Answer'},
        {'name': 'SourceCitation'},
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '''
                <div class="card front-card">
                    <div class="badge">QUESTION</div>
                    <div class="content">{{Question}}</div>
                </div>
            ''',
            'afmt': '''
                <div class="card front-card">
                    <div class="badge">QUESTION</div>
                    <div class="content">{{Question}}</div>
                </div>
                <hr id="answer">
                <div class="card back-card">
                    <div class="badge" style="background: #a855f7;">ANSWER</div>
                    <div class="content">{{Answer}}</div>
                    {{#SourceCitation}}
                        <div class="citation">📍 Grounded Source: <i>{{SourceCitation}}</i></div>
                    {{/SourceCitation}}
                </div>
            ''',
        },
    ],
    css='''
        .card {
            background-color: #1e293b;
            border: 1px solid #38bdf8;
            border-radius: 12px;
            padding: 24px;
            color: #f8fafc;
            font-family: Arial, sans-serif;
            text-align: left;
            margin-bottom: 10px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .back-card {
            border-color: #a855f7;
            background-color: #1e1b4b;
        }
        .badge {
            display: inline-block;
            background: #0284c7;
            color: white;
            font-size: 0.75rem;
            font-weight: bold;
            padding: 4px 8px;
            border-radius: 6px;
            margin-bottom: 12px;
            letter-spacing: 0.05em;
        }
        .content {
            font-size: 1.1rem;
            line-height: 1.5;
        }
        .citation {
            margin-top: 16px;
            font-size: 0.85rem;
            color: #94a3b8;
            border-top: 1px dashed #475569;
            padding-top: 8px;
        }
    '''
)


my_deck = genanki.Deck(DECK_ID, 'Python Performance :: Generated via AI Pipeline')

mock_extracted_cards = [
    {
        "front": "What is the primary benefit of cooperative multitasking in 'asyncio'?",
        "back": "It allows a single-threaded program to handle thousands of concurrent operations by yielding control during I/O wait times, preventing thread-context switching overhead.",
        "source": "Notes on Asyncio Fundamentals (Paragraph 3)"
    },
    {
        "front": "Why should you use 'Pydantic' schemas when working with Large Language Models?",
        "back": "Pydantic guarantees structural syntax alignment, forcing the LLM to yield output conforming precisely to predefined code models instead of unparsed conversational strings.",
        "source": "AI Validation Strategies Guide"
    }
]

print("Initializing flashcard compilation layer...")


for card_data in mock_extracted_cards:
    new_note = genanki.Note(
        model=notebook_lm_style_model,
        fields=[card_data["front"], card_data["back"], card_data["source"]]
    )
    my_deck.add_note(new_note)
    print(f"✅ Packaged note: '{card_data['front'][:40]}...'")

output_filename = "notebooklm_study_deck.apkg"
print(f"📦 Compiling collection database into native package format...")


genanki.Package(my_deck).write_to_file(output_filename)

print(f"🚀 Success! Local compilation engine output file generated: '{output_filename}'")