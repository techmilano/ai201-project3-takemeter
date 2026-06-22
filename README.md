# TakeMeter: UCF Student Housing & Campus Life Discourse Classifier

## Project Overview

TakeMeter is a fine-tuned text classifier that evaluates the type and quality of discourse in UCF student housing and campus life discussions. The project focuses on short public posts and comments that students might encounter when researching housing, parking, dining, roommates, and off-campus apartment experiences.

The goal was to define a clear label taxonomy, collect and annotate a small real-world dataset, fine-tune a transformer model, compare that model against a zero-shot Groq baseline, and analyze where the classifier succeeds or fails.

## Community Choice

I chose UCF student housing and campus life discussions as the community for this project. The examples are based on public-style Reddit discussion patterns from communities such as `r/ucf` and `r/UCFstudenthousing`, where students regularly ask questions and share opinions about housing, parking, roommates, apartments, dining, and campus life.

This community is a good fit for a classification task because the discourse contains several different kinds of comments. Some comments give practical advice, some describe personal experiences, some complain or warn about problems, and others are short low-information reactions. These distinctions matter because students searching for help often need to separate useful guidance from venting, anecdotes, or jokes.

## Label Taxonomy

The classifier uses four mutually exclusive labels.

### `practical_advice`

A post gives actionable guidance, steps, recommendations, or warnings that another student could use.

Examples:

- "If you are looking off campus, tour the apartment first and ask about shuttle access before signing."
- "Apply early because the better housing options usually fill up fast."

### `personal_experience`

A post mainly describes the writer's own experience without giving a clear recommendation.

Examples:

- "I lived at Knights Circle last year. The location was convenient, but maintenance took a while to respond."
- "My roommate situation was fine, but the walls were thin and I could hear people in the hallway."

### `complaint_or_warning`

A post expresses a negative opinion, frustration, criticism, or warning about a place, rule, service, or situation.

Examples:

- "Do not wait until July to find housing because everything gets expensive and the decent places fill up fast."
- "Parking during the first few weeks is terrible and you should expect to waste time looking for a spot."

### `low_info_reaction`

A post is a short emotional reaction, joke, agreement, sarcasm, or low-detail reply that does not add useful information.

Examples:

- "Parking at UCF is cooked lol."
- "Real."

## Edge Case Rules

The hardest boundary was between `practical_advice` and `complaint_or_warning`.

Some comments warn students about a risk but are worded like advice. For example:

> Watch out for utility caps that are set artificially low so you always owe extra.

This comment tells the reader to "watch out," which sounds like practical advice. However, the main purpose is to warn about a negative housing practice. I labeled this kind of comment as `complaint_or_warning` when the warning or criticism was the dominant purpose.

Another difficult boundary was between `personal_experience` and `practical_advice`. If a post mainly describes what happened to the writer, I labeled it `personal_experience`. If the post uses that experience to tell another student what to do, check, avoid, or consider, I labeled it `practical_advice`.

## Dataset

### Data Source

The dataset contains UCF student housing and campus life style posts/comments. The content focuses on common student discussion topics such as:

- On-campus housing
- Off-campus apartments
- Parking
- Roommates
- Dining
- Freshman and transfer student advice
- General campus life experiences

The final dataset used for training was:

```text
data/takemeter_ucf_labeled.csv
```

I selected the cleaner v1 dataset because it had a balanced distribution across all four labels and no label typos.

### Dataset Format

The CSV contains these columns:

| Column | Description |
|---|---|
| `text` | The post or comment text |
| `label` | The manually assigned label |
| `source` | The source or source category |
| `notes` | Optional labeling notes or edge-case comments |

### Label Distribution

The final dataset contains 220 labeled examples.

| Label | Count | Approx. Percentage |
|---|---:|---:|
| `practical_advice` | 58 | 26.4% |
| `personal_experience` | 56 | 25.5% |
| `complaint_or_warning` | 56 | 25.5% |
| `low_info_reaction` | 50 | 22.7% |
| **Total** | **220** | **100%** |

This distribution is balanced enough for the assignment because no single label dominates the dataset.

### Train / Validation / Test Split

The starter Colab notebook split the single labeled CSV automatically into train, validation, and test sets using a 70% / 15% / 15% split.

The locked test set contained 33 examples.

## Difficult Labeling Examples

### Difficult Example 1

Text:

> Watch out for utility caps that are set artificially low so you always owe extra.

Possible labels:

- `practical_advice`
- `complaint_or_warning`

Final label:

```text
complaint_or_warning
```

Reason:

The phrase "watch out" sounds like advice, but the main purpose is to warn about a negative housing practice. I treated the warning as the dominant intent.

### Difficult Example 2

Text:

> I lived there last year and maintenance was slow, so check recent reviews before signing.

Possible labels:

- `personal_experience`
- `practical_advice`

Final label:

```text
practical_advice
```

Reason:

The comment starts with personal experience, but it gives a clear action to the reader: check recent reviews before signing.

### Difficult Example 3

Text:

> Parking is awful, but if you get there before 9 you can usually find a spot.

Possible labels:

- `complaint_or_warning`
- `practical_advice`

Final label:

```text
practical_advice
```

Reason:

Although the comment includes a complaint, the useful part is the actionable recommendation about arrival time. I labeled it as advice.

## Fine-Tuning Approach

### Base Model

The fine-tuned model used:

```text
distilbert-base-uncased
```

This model was selected because it is small, fast to fine-tune in Google Colab, and appropriate for a small text classification dataset.

### Training Setup

The project was trained in Google Colab using the starter TakeMeter notebook. The notebook used HuggingFace `transformers`, `datasets`, and `scikit-learn`.

The model was configured for four output labels:

```python
label_map = {
    "practical_advice": 0,
    "personal_experience": 1,
    "complaint_or_warning": 2,
    "low_info_reaction": 3
}
```

### Hyperparameter Decision and Change

The first fine-tuning run used the starter notebook defaults:

| Setting | Initial Value |
|---|---:|
| Epochs | 3 |
| Learning rate | 2e-5 |
| Batch size | 16 |

That initial run completed successfully, but validation accuracy only reached about 0.52. The model appeared undertrained because the dataset was small and the default run produced only a limited number of update steps.

I then reran Section 3 with:

| Setting | Updated Value |
|---|---:|
| Epochs | 8 |
| Learning rate | 2e-5 |
| Batch size | 8 |

I kept the learning rate at `2e-5` to avoid overly aggressive updates, increased the number of epochs to give the model more passes through the data, and reduced batch size to 8 to increase the number of training update steps.

The updated run improved validation accuracy to about 0.94 by epochs 7 and 8.

### Training Output Summary

| Epoch | Training Loss | Validation Loss | Validation Accuracy |
|---:|---:|---:|---:|
| 1 | 1.331654 | 1.293573 | 0.515152 |
| 2 | 1.169417 | 1.076839 | 0.787879 |
| 3 | 0.845373 | 0.763431 | 0.878788 |
| 4 | 0.467200 | 0.451648 | 0.878788 |
| 5 | 0.222983 | 0.288867 | 0.909091 |
| 6 | 0.114671 | 0.207699 | 0.909091 |
| 7 | 0.069370 | 0.169288 | 0.939394 |
| 8 | 0.062691 | 0.170872 | 0.939394 |

## Baseline Approach

The baseline used Groq's `llama-3.3-70b-versatile` as a zero-shot classifier. The prompt included the four label definitions and instructed the model to respond with only one valid label name.

The baseline was run on the same locked test set as the fine-tuned model.

### Groq Baseline Prompt

```text
You are classifying posts and comments from UCF student housing and campus life discussions.
Assign each post to exactly one of the following categories.

practical_advice: The post gives actionable guidance, steps, recommendations, or warnings that another student could use.
Example: "If you are looking off campus, tour the apartment first and ask about shuttle access before signing."

personal_experience: The post mainly describes the writer's own experience without giving a clear recommendation.
Example: "I lived at Knights Circle last year. The location was convenient, but maintenance took a while to respond."

complaint_or_warning: The post expresses a negative opinion, frustration, criticism, or warning about a place, rule, service, or situation.
Example: "Do not wait until July to find housing because everything gets expensive and the decent places fill up fast."

low_info_reaction: The post is a short emotional reaction, joke, agreement, sarcasm, or low-detail reply that does not add useful information.
Example: "Parking at UCF is cooked lol."

Decision rules:
- If a post gives another student something to do, check, avoid, or consider, choose practical_advice.
- If a post mainly tells what happened to the writer, choose personal_experience.
- If a post mainly complains, criticizes, or warns about a bad situation, choose complaint_or_warning.
- If a post is short, joking, emotional, sarcastic, or low-detail, choose low_info_reaction.
- Choose the single best label even if more than one label seems possible.

Respond with ONLY the label name.
Do not explain your reasoning.
Do not include punctuation.

Valid labels:
practical_advice
personal_experience
complaint_or_warning
low_info_reaction
```

## Evaluation Results

### Overall Accuracy

| Model | Accuracy | Test Set Size |
|---|---:|---:|
| Groq zero-shot baseline | 0.9091 | 33 |
| Fine-tuned DistilBERT | 0.9697 | 33 |

The fine-tuned model improved over the Groq baseline by:

```text
0.0606
```

or about 6.1 percentage points.

### Baseline Per-Class Metrics

| Label | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| `practical_advice` | 0.90 | 1.00 | 0.95 | 9 |
| `personal_experience` | 1.00 | 0.88 | 0.93 | 8 |
| `complaint_or_warning` | 0.80 | 0.89 | 0.84 | 9 |
| `low_info_reaction` | 1.00 | 0.86 | 0.92 | 7 |
| **Accuracy** |  |  | **0.91** | **33** |
| **Macro avg** | 0.93 | 0.91 | 0.91 | 33 |
| **Weighted avg** | 0.92 | 0.91 | 0.91 | 33 |

### Fine-Tuned Model Per-Class Metrics

| Label | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| `practical_advice` | 0.90 | 1.00 | 0.95 | 9 |
| `personal_experience` | 1.00 | 1.00 | 1.00 | 8 |
| `complaint_or_warning` | 1.00 | 0.89 | 0.94 | 9 |
| `low_info_reaction` | 1.00 | 1.00 | 1.00 | 7 |
| **Accuracy** |  |  | **0.97** | **33** |
| **Macro avg** | 0.97 | 0.97 | 0.97 | 33 |
| **Weighted avg** | 0.97 | 0.97 | 0.97 | 33 |

### Fine-Tuned Confusion Matrix

Rows are true labels. Columns are predicted labels.

| True \ Predicted | `practical_advice` | `personal_experience` | `complaint_or_warning` | `low_info_reaction` |
|---|---:|---:|---:|---:|
| `practical_advice` | 9 | 0 | 0 | 0 |
| `personal_experience` | 0 | 8 | 0 | 0 |
| `complaint_or_warning` | 1 | 0 | 8 | 0 |
| `low_info_reaction` | 0 | 0 | 0 | 7 |

The committed confusion matrix image is also included in the repository:

```text
confusion_matrix.png
```

## Wrong Prediction Analysis

The fine-tuned model made 1 wrong prediction out of 33 test examples.

### Wrong Prediction 1

Text:

> Watch out for utility caps that are set artificially low so you always owe extra.

True label:

```text
complaint_or_warning
```

Predicted label:

```text
practical_advice
```

Confidence:

```text
0.79
```

Analysis:

This is a difficult example because it contains both warning language and advice language. The phrase "Watch out for" tells another student what to pay attention to, which makes it look like `practical_advice`. However, the main purpose of the comment is to warn students about a negative housing practice where utility caps are set low enough that students may owe extra money.

This failure shows that the hardest remaining boundary is between `complaint_or_warning` and `practical_advice`. The model learned the broader label patterns very well, but it still struggled with a warning that was phrased as a useful recommendation.

To improve this boundary, I would add more examples where warnings are phrased as advice, such as comments beginning with "watch out," "be careful," or "make sure you check."

## Sample Classifications

The following examples show how the fine-tuned classifier can be used on new posts. Confidence values should be read as model confidence, not as a guarantee that the label is correct.

| Example Text | Predicted Label | Confidence | Notes |
|---|---|---:|---|
| "If you are looking off campus, tour the apartment first and ask about shuttle access before signing." | `practical_advice` | 0.98 | Correct because the comment gives clear action steps. |
| "I lived at Knights Circle last year. The location was convenient, but maintenance took a while to respond." | `personal_experience` | 0.97 | Correct because the comment describes the writer's own experience. |
| "Do not wait until July to find housing because everything gets expensive and the decent places fill up fast." | `complaint_or_warning` | 0.96 | Correct because the main purpose is warning students about a negative outcome. |
| "Parking at UCF is cooked lol." | `low_info_reaction` | 0.99 | Correct because the comment is short, emotional, and low-detail. |
| "Watch out for utility caps that are set artificially low so you always owe extra." | `practical_advice` | 0.79 | Incorrect; the true label was `complaint_or_warning`. |

## Reflection: What the Model Learned vs. What I Intended

I intended the model to learn the purpose of a post: whether it gives advice, shares experience, warns or complains, or adds little information. Overall, the fine-tuned model learned this distinction well. The high performance on `personal_experience` and `low_info_reaction` suggests that the model learned clear surface patterns for personal storytelling and short emotional reactions.

The model also learned `practical_advice` well, but the one wrong prediction shows that it may rely heavily on action-oriented phrases such as "watch out" or "check." In that case, the model treated a warning as advice because the wording sounded useful to the reader.

This reveals a gap between the intended label definition and the model's learned boundary. I wanted `complaint_or_warning` to capture risk-focused comments, even when they are phrased as advice. The model mostly learned the distinction, but the error suggests it still needs more boundary examples where warnings and advice overlap.

## Spec Reflection

The planning spec helped guide the project by forcing me to define the labels and edge-case rules before training the model. This made the annotation process more consistent and made the wrong prediction easier to interpret because I already knew that `practical_advice` vs. `complaint_or_warning` was a difficult boundary.

The implementation diverged from the original training plan because the starter notebook's default 3-epoch fine-tuning run undertrained the model. After seeing validation accuracy stay around 0.52, I changed the training setup to 8 epochs and batch size 8. This change gave the model more training update steps and improved validation accuracy to about 0.94, with final test accuracy of 0.9697.

## AI Usage

I used AI assistance in several specific ways during the project.

First, I used AI assistance to compare two generated dataset versions and decide which one was better for Colab. The AI analysis recommended using `takemeter_ucf_labeled_v1.csv` because it had a balanced label distribution, no missing values, no duplicate text, and no label typo. I accepted this recommendation and used v1 for training.

Second, I used AI assistance to write and refine the Groq system prompt. The prompt included the four label definitions, examples, decision rules, and a strict instruction to return only the label name. I used this prompt for the zero-shot Groq baseline.

Third, I used AI assistance to interpret the first fine-tuning run. The first run completed successfully, but validation accuracy was low. The AI feedback suggested the model was undertrained because the dataset was small and only 30 training steps were run. I changed the training setup to 8 epochs and batch size 8, while keeping the learning rate at 2e-5.

Fourth, I used AI assistance to analyze the final wrong prediction. The analysis helped identify that the model confused `complaint_or_warning` with `practical_advice` when a warning was phrased as something the reader should do.

All AI-generated suggestions were reviewed before being included in the final project documentation.

## Files in This Repository

```text
.
├── README.md
├── planning.md
├── ai201_project3_takemeter_starter_clean.ipynb
├── data/
│   └── takemeter_ucf_labeled.csv
├── prompts/
│   └── groq_baseline_prompt.md
├── results/
│   ├── evaluation_results.json
│   └── confusion_matrix.png
└── sample_outputs/
    └── sample_classifications.md
```

## Stretch Feature: Gradio Interface in Colab

I implemented the deployed interface stretch feature inside the Colab notebook instead of a separate `app.py` file. The original Colab runtime reset before I could export the `takemeter_model/` folder locally, so I added the interface directly to the notebook.

The notebook includes a bonus section that:

1. Installs Gradio.
2. Saves the fine-tuned model and tokenizer to `./takemeter_model` after Section 3.
3. Launches a Gradio interface that accepts a new UCF housing or campus life post.
4. Displays the predicted label and confidence scores for all four labels.

To run the interface:

1. Open `ai201_project3_takemeter_starter_clean.ipynb` in Colab.
2. Upload `data/takemeter_ucf_labeled.csv`.
3. Run Sections 1–4 to load data, tokenize, fine-tune, and evaluate the model.
4. Run the bonus Gradio cells at the bottom of the notebook.
5. Use the temporary Gradio link generated by `demo.launch(share=True)`.

This satisfies the interface stretch feature because the notebook accepts a new post, runs it through the fine-tuned classifier, and displays the predicted label and confidence.

## How to Run

1. Open the TakeMeter starter Colab notebook.
2. Set the runtime to T4 GPU.
3. Upload `data/takemeter_ucf_labeled.csv`.
4. Set the label map to:

```python
label_map = {
    "practical_advice": 0,
    "personal_experience": 1,
    "complaint_or_warning": 2,
    "low_info_reaction": 3
}
```

5. Add the Groq API key in Colab Secrets as:

```text
GROQ_API_KEY
```

6. Run the baseline section using the prompt in `prompts/groq_baseline_prompt.md`.
7. Fine-tune `distilbert-base-uncased`.
8. Evaluate the fine-tuned model.
9. Export and commit:

```text
evaluation_results.json
confusion_matrix.png
```

## Demo Video

The demo video shows:

- The repository files
- The label taxonomy
- The labeled dataset
- Groq baseline results
- Fine-tuned model results
- Several sample classifications with labels and confidence
- One correct prediction explanation
- One incorrect prediction explanation
- A brief walkthrough of the evaluation report
