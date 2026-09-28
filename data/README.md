# Frontend Data Boundary

This directory documents data that can later move from static JavaScript into Django models and template context. No duplicate runtime data is created here yet, so the current site keeps one source of truth.

Suggested future files:

- `quiz-data.js`
- `crimes-data.js`
- `cases-data.js`
- `freedom-fighters-data.js`
- `constitution-values.js`

Potential Django model counterparts are `QuizQuestion`, `Crime`, `Case`, `FreedomFighter`, `ConstitutionalValue`, `Article`, `Helpline`, and `SurveyResponse`.