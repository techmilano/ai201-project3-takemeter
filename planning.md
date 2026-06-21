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


