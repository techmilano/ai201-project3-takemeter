"""
TakeMeter: UCF Student Housing & Campus Life Discourse Classifier — Gradio app.

Bonus Option 2 (deployed interface): accepts a new UCF post, runs it through the
fine-tuned DistilBERT classifier, and displays the predicted label and confidence.

Run locally:
    pip install -r requirements.txt
    # place the fine-tuned model (saved from the notebook) in ./takemeter_model
    python app.py

The same interface is also included as cells in
`ai201_project3_takemeter_starter_clean.ipynb` so it can be launched directly in Colab.
"""
import gradio as gr
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_DIR = "./takemeter_model"

tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
model.eval()

# Read labels from the model config (set during fine-tuning) so this stays in sync
# with the notebook's LABEL_MAP. Falls back to the project taxonomy if absent.
if model.config.id2label and len(model.config.id2label) == model.config.num_labels:
    LABELS = [model.config.id2label[i] for i in range(model.config.num_labels)]
else:
    LABELS = [
        "practical_advice",
        "personal_experience",
        "complaint_or_warning",
        "low_info_reaction",
    ]


def classify_post(text):
    if not text or not text.strip():
        return {}, "Please enter a post."

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=256,
    )

    with torch.no_grad():
        logits = model(**inputs).logits
        probs = torch.softmax(logits, dim=-1)[0]

    confidences = {LABELS[i]: float(probs[i]) for i in range(len(LABELS))}
    pred_id = int(torch.argmax(probs))
    summary = f"Predicted label: {LABELS[pred_id]}  (confidence {float(probs[pred_id]):.2%})"
    return confidences, summary


demo = gr.Interface(
    fn=classify_post,
    inputs=gr.Textbox(
        lines=5,
        label="UCF post or comment",
        placeholder="Paste a UCF housing or campus life post here...",
    ),
    outputs=[
        gr.Label(num_top_classes=len(LABELS), label="Confidence by label"),
        gr.Textbox(label="Prediction"),
    ],
    title="TakeMeter: UCF Discourse Classifier",
    description=(
        "Classifies UCF housing and campus life posts into practical_advice, "
        "personal_experience, complaint_or_warning, or low_info_reaction."
    ),
    examples=[
        ["If you are looking off campus, tour the apartment first and ask about shuttle access before signing."],
        ["I lived at Knights Circle last year. The location was convenient, but maintenance took a while to respond."],
        ["Parking at UCF is cooked lol."],
        ["Watch out for utility caps that are set artificially low so you always owe extra."],
    ],
)

if __name__ == "__main__":
    demo.launch()
