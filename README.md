# 🇮🇳 Samvidhan - The Constitution of India

An interactive and responsive multi-page website that simplifies the **Constitution of India** and its core values for everyone.
This project presents complex constitutional concepts in **easy language**, along with real-life examples, quizzes, case studies, and more.

---

## 🌐 Live Website

🔗 [Visit Website](PASTE_YOUR_LIVE_LINK_HERE)

---

## 🚀 Features

✨ **Multi-Page Website**

* Separate pages for all major constitutional topics

📘 **Core Values Explained**

* Sovereignty
* Secularism
* Socialism
* Democracy
* Republic
* Justice
* Liberty
* Equality
* Fraternity
* Dignity of Individual
* Unity & Integrity

⚖️ **Fundamental Rights & Duties**

* Explained in simple words
* Real-life relatable examples

🚔 **Crimes & Punishments**

* Awareness about common crimes
* Simple explanation of legal consequences

📑 **Real-Life Case Studies**

* Report-style case presentation
* Animated sections

📜 **Important Articles & Schedules**

* Key articles like 14, 19, 21 explained
* Easy breakdown of schedules

📞 **Emergency Helpline Page**

* Important Indian helpline numbers
* Click-to-call feature

🧠 **Interactive Quiz**

* Constitution-based MCQs
* Score tracking

🧾 **Freedom Fighters Section**

* Stories and contributions
* Role in independence & constitution

📝 **Survey System**

* User input (Name, Email, Phone)
* Opinion-based questions
* Audio response support

📊 **Survey Results Dashboard**

* Displays submitted responses
* Report-style format using localStorage

---

## 🎨 Tech Stack

* **HTML5**
* **Tailwind CSS (CDN)**
* **Vanilla JavaScript**

---

## 📱 Responsiveness

✔ Fully responsive
✔ Mobile-friendly
✔ Works on all screen sizes

---

## 🎯 Purpose of the Project

This project aims to:

* Make constitutional knowledge **accessible**
* Spread awareness about **rights & duties**
* Educate users in an **interactive way**
* Promote constitutional values among youth 🇮🇳

---

## 💡 Future Improvements

* Backend integration (Django / Node.js)
* Database storage for survey results
* User authentication
* More quizzes & gamification

---

## 🙌 Contribution

Feel free to fork this repo and improve it 🚀
Pull requests are welcome!

---

## 📜 License

This project is open-source and available under the MIT License.

---

## 👨‍💻 Author

**Laxmi Narayan Verma**

---

## 🧭 Frontend Structure

The site remains a root-level static HTML project so relative links continue to work with Live Server, GitHub Pages, and Netlify.

```text
templates/
├── base.html
├── components/
│   ├── navbar.html
│   ├── mobile_menu.html
│   ├── footer.html
│   └── preamble_nav.html
└── README.md

static/
├── css/
├── global.css       # Shared tokens, reset, focus states, tricolor, motion utilities
│   └── components.css # Shared navigation and constitutional-value components
└── js/
├── main.js          # Shared page initialization
├── navigation.js    # Active navigation and mobile-menu behavior
├── animations.js    # Shared IntersectionObserver animations
└── storage.js       # Safe localStorage adapter for future Django replacement
```

The constitutional-value pages use the shared CSS and JavaScript foundation from `static/`. Their page-specific content and expand/collapse behavior remain local to preserve the existing experience. The survey uses browser media APIs and Django form submission; recorded survey audio is stored in the database.

The existing frontend assets are also copied into `static/assets/` for Django static serving. The original `assets/` directory remains available to legacy root pages during migration.

The legacy HTML pages and their original assets are now grouped under `frontend/`. Django serves them through compatibility routes so existing `.html` links continue to work.

## Django + SQLite

The project now includes a Django application without authentication or user accounts. Survey submissions are saved as `SurveyResponse` rows in SQLite, and the response ID for the latest submission is stored in the current Django session.

### Setup

The local `.venv/` was created automatically and Django is pinned in `requirements.txt`. To reproduce the environment:

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe manage.py migrate
```

### Run

```powershell
.venv\Scripts\python.exe manage.py runserver
```

Open `http://127.0.0.1:8000/`. Users register and log in before opening the quiz or survey. The survey flow is:

```text
register/login -> protected quiz or survey
survey page -> Django POST -> SurveyResponse -> SQLite3 -> thank-you page -> home
```

The results view and audio playback endpoint are staff-only. Aggregate values are calculated with the Django ORM. All responses are available to authorized staff through Django Admin at `/admin/`; use `python manage.py createsuperuser` to create the portal owner account. Survey recordings are saved as binary data in SQLite, not uploaded to Cloudinary.

The original pages remain grouped in `frontend/` during migration. Django routes serve those pages for general content, while `/survey/` and `/results/` use the database-backed workflow. Quiz and survey routes require a user account; results remain restricted to staff. To configure Google sign-in, copy `.env.example` to `.env`, replace the placeholders with credentials from a Google OAuth client, and add `http://127.0.0.1:8000/accounts/google/callback/` to its authorized redirect URIs. Set `GOOGLE_REDIRECT_URI` to the deployed callback URL outside local development. The `.env` file is ignored by Git. The quiz uses Gemini to generate a fresh set when its page opens and to score submitted answers; set `GEMINI_API_KEY` in `.env` (and optionally `GEMINI_MODEL`) to enable it. Restart Django after changing `.env`. The API key stays on the server and is never sent to the browser.

---

⭐ If you like this project, don't forget to star the repository!
