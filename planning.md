# TakeMeter Planning

## Community

I chose UCF student housing and campus life discussions from public Reddit communities such as r/ucf and r/UCFstudenthousing. This community is a good fit because students regularly post advice, complaints, personal housing experiences, parking opinions, dining opinions, and short reactions. The discourse varies from useful guidance to emotional venting, which makes it appropriate for a text classification task.

## Labels

### practical_advice
A comment gives actionable guidance, steps, recommendations, or warnings that another student could use.

Examples:
- "If you live off campus, check whether the apartment has a UCF shuttle before signing."
- "Apply for housing early because options get limited later."

### personal_experience
A comment mainly describes the writer’s own experience without giving a clear recommendation.

Examples:
- "I lived at Knights Circle last year and the location was convenient."
- "My roommate situation was fine, but the walls were thin."

### complaint_or_warning
A comment expresses a negative opinion, frustration, or warning about a place, rule, service, or situation.

Examples:
- "Do not wait until July to find housing because everything gets expensive."
- "Parking is awful during the first few weeks of class."

### low_info_reaction
A short emotional reaction, joke, agreement, sarcasm, or low-detail reply that does not add useful information.

Examples:
- "That place is cooked."
- "Real lol."


## Hard Edge Cases

The hardest boundary is between `personal_experience` and `practical_advice`.

Decision rule:
If the comment mainly tells what happened to the writer, label it `personal_experience`. If it tells another student what to do, avoid, check, or consider, label it `practical_advice`.

Example:
"I lived there last year and maintenance was slow, so check recent reviews before signing."

This includes personal experience, but the main purpose is advice. I will label it `practical_advice`.


## Data Collection Plan

I will collect at least 200 public Reddit comments from r/ucf and r/UCFstudenthousing. I will focus on threads about housing, off-campus apartments, parking, dining, roommates, and freshman advice.

Target distribution:
- practical_advice: 50 examples
- personal_experience: 50 examples
- complaint_or_warning: 50 examples
- low_info_reaction: 50 examples

If one label is underrepresented, I will search for more threads likely to contain that label. For example, freshman advice threads should contain more `practical_advice`, apartment review threads should contain more `personal_experience`, and parking complaint threads should contain more `complaint_or_warning` and `low_info_reaction`.

## Evaluation Metrics

I will report overall accuracy for both the Groq zero-shot baseline and the fine-tuned DistilBERT model. I will also report per-class precision, recall, and F1 because accuracy alone can hide poor performance on minority labels.

The most important metric will be per-class F1 because the model should not only perform well overall; it should also recognize each discourse type.

## Definition of Success

A successful classifier should:
- Beat the Groq zero-shot baseline on the same test set, or be close while being cheaper and locally runnable.
- Achieve at least 70% overall accuracy.
- Achieve at least 0.60 F1 for each label.
- Show understandable failure patterns rather than random errors.

For a real community tool, I would consider it good enough as a first-pass classifier if it can reliably separate useful comments from low-information reactions.

## AI Tool Plan

### Label Stress Testing
I will ask an AI tool to generate borderline examples between:
- practical_advice and personal_experience
- personal_experience and complaint_or_warning
- complaint_or_warning and low_info_reaction

I will use those examples to tighten my decision rules before labeling all 200 examples.

### Annotation Assistance
I may use an LLM to pre-label small batches of examples, but I will manually review every label. If I use this workflow, I will disclose it in the README.

### Failure Analysis
After fine-tuning, I will paste the wrong predictions into an AI tool and ask it to identify patterns. I will verify the patterns myself before including them in the README.


