# Page Scripts

Extract page-local JavaScript here as independent modules. Load only the module required by the current page after the shared scripts.

Recommended ownership:

- `home.js`
- `rights.js`
- `articles.js`
- `cases.js`
- `crimes.js`
- `freedom.js`
- `helpline.js`
- `quiz.js`
- `survey.js`
- `results.js`

Preserve the existing DOM IDs, inline event contracts, localStorage keys, EmailJS setup, MediaRecorder flow, Cloudinary upload, and case/quiz state while extracting code.