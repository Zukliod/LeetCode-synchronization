# 🚀 Automated Developer Portfolio & Resume Synchronization Pipeline

> **"Build once, automate forever."** — An automated system designed to keep your GitHub, LeetCode stats, LinkedIn presence, Markdown resume (`resume.md`), compiled PDF resumes, and live portfolio website (`index.html`) automatically synchronized with zero manual hassle.

---

## 💡 Why This Project Exists (The Origin Story)

As a 4th-year Computer Science engineering student facing placement season, our **Training & Placement (T&P)** office strongly advised us to keep all our developer profiles—GitHub, LinkedIn, LeetCode, and personal portfolios—consistently active, updated, and interactive for recruiters. 

However, I constantly faced the same struggle many students face:
- Building new engineering projects and solving DSA problems regularly, but **forgetting or delaying updating my resume**.
- Manually rewriting Markdown/Word files and recompiling PDFs every time a new project was finished.
- Forgetting to post updates on LinkedIn or update live portfolio website project sections.

Instead of spending hours on manual profile maintenance during placement prep, I built this automated CI/CD pipeline. Now, whenever I push code or tag a project on GitHub, the system automatically scores my work, updates my resume, compiles fresh ATS-friendly PDFs, fetches live LeetCode stats, and keeps my portfolio site recruiter-ready with zero manual effort!

---

## 📌 Core Features

- **3-Tier Smart Project Curator:** Dynamically ranks your top repositories on your resume and website using tech stack depth, date decay (recency), deployed links, and explicit topic tags.
- **`portfolio` Opt-In Tag:** Tag any repository on GitHub with `portfolio` to instantly promote it to your featured projects list.
- **Automatic Practice Filtering:** Automatically filters out LeetCode sync repos, DSA practice folders, tutorials, and configuration files.
- **Live LeetCode Stats Sync:** Real-time problem-solving metrics (Easy, Medium, Hard, and Contest Ratings) rendered directly on the portfolio dashboard.
- **Dynamic PDF Compilation:** Converts `resume.md` to styled ATS-friendly PDFs (`FullStack` and `Backend` variants) via `wkhtmltopdf`.
- **Cache-Busting Integration:** Download links automatically append dynamic timestamps (`?v=timestamp`) so recruiters always download the freshest PDF without browser caching issues.
- **GitHub Actions Automation:** Runs automatically on schedule or push.

---

## 🔑 Required API Keys & Tokens Guide

To run this automation pipeline for your own profiles, you need to acquire and configure a few access tokens and credentials.

### 1. GitHub Personal Access Token (`GH_TOKEN` or `GITHUB_TOKEN`)
* **Purpose:** Allows GitHub Actions to push updated `resume.md` files and compiled `.pdf` files back to your repository.
* **How to get it:**
  1. Go to **GitHub Settings** > **Developer Settings** > **Personal Access Tokens** > **Tokens (classic)**.
  2. Click **Generate new token (classic)**.
  3. Give it a name (e.g., `Automation-Pipeline-Token`).
  4. Select scopes: Check **`repo`** (Full control of private/public repositories) and **`workflow`**.
  5. Click **Generate token** and copy the key immediately.

---

### 2. Formspree Form ID (For Serverless Contact Form)
* **Purpose:** Routes messages submitted on your `index.html` contact form directly to your personal email.
* **How to get it:**
  1. Sign up for a free account at [Formspree.io](https://formspree.io).
  2. Click **Create New Form**.
  3. Set the target email where you want recruiters' messages delivered.
  4. Copy your unique **Form Endpoint** or **Form ID** (e.g., `https://formspree.io/f/your_form_id`).

---

### 3. Gemini API Key (For AI Recruiter Chatbot)
* **Purpose:** Powers the floating AI Assistant on `index.html` to answer recruiter questions about your degree, skills, and internship experience.
* **How to get it:**
  1. Go to [Google AI Studio](https://aistudio.google.com/).
  2. Log in with your Google Account and click **Get API key**.
  3. Click **Create API key in new project**.
  4. Copy the generated API Key.

---

### 4. LinkedIn Access Token / OAuth Credentials (Optional - For LinkedIn Sync)
* **Purpose:** Allows automated status updates or profile synchronization with LinkedIn.
* **How to get it:**
  1. Go to the [LinkedIn Developer Portal](https://www.linkedin.com/developers/).
  2. Click **Create App**, fill in your details, and link it to your LinkedIn profile.
  3. Under the **Products** tab, request access to **Share on LinkedIn** and **Sign In with LinkedIn using OpenID Connect**.
  4. Under **Auth**, find your **Client ID** and **Client Secret**, or generate an OAuth 2.0 Access Token using the token generator tool.

---

## 🛠️ Prerequisites

Before running locally, ensure you have the following installed:

1. **Python 3.10+**
2. **Git**
3. **wkhtmltopdf** (Required locally for Markdown-to-PDF conversion)
   - **Windows:** Download installer from [wkhtmltopdf.org](https://wkhtmltopdf.org/downloads.html) and add its `bin/` directory to your System `PATH`.
   - **Linux/Ubuntu:** `sudo apt-get update && sudo apt-get install -y wkhtmltopdf`
   - **macOS:** `brew install wkhtmltopdf`

---

## 🚀 Quickstart: Setup & Customization

Follow these steps if you cloned this repository or extracted the ZIP archive:

### Step 1: Install Python Dependencies
Open your terminal in the root directory of the project and run:

```bash
pip install -r requirements.txt
Step 2: Customize Script & HTML Constants1. Configure Python Script (update_resume_projects.py)Open update_resume_projects.py and set your GitHub username:PythonGITHUB_USERNAME = "YOUR_GITHUB_USERNAME"
2. Configure Portfolio Website (index.html)Open index.html and update your username and credentials in the JavaScript block at the bottom:JavaScriptconst GITHUB_USERNAME = "YOUR_GITHUB_USERNAME";

// Formspree Contact Form Endpoint
// Replace action URL in <form id="contact-form" action="[https://formspree.io/f/YOUR_FORMSPREE_ID](https://formspree.io/f/YOUR_FORMSPREE_ID)">

// Gemini API Key for Chatbot (Optional/Client Injection)
window.GEMINI_API_KEY = "YOUR_GEMINI_API_KEY";
3. Update Resume Content (resume.md)Open resume.md and replace the placeholder contact info, Education, Experience, and Skills sections with your own details.⚠️ Important: Do NOT remove or edit the HTML comment markers shown below. The Python script relies on them to inject your top GitHub projects:Markdown<!-- START_GITHUB_PROJECTS -->
<!-- Dynamic top repositories will automatically populate here -->
<!-- END_GITHUB_PROJECTS -->
Step 3: Tag Your Top Repositories on GitHubTo make your favorite projects rank at the top of your resume and live website:Go to your repository on GitHub.com.Click the gear icon (⚙️) in the top-right corner of the About section.Add portfolio in the Topics field.Add a clean, short Description and (if deployed) a Homepage URL.Step 4: Test Execution LocallyRun the project curator script:Bashpython update_resume_projects.py
Check resume.md—your top repositories will now appear under the START_GITHUB_PROJECTS section!To test PDF generation locally:Bashpython -c "import markdown, pdfkit; html=markdown.markdown(open('resume.md').read()); pdfkit.from_string(html, 'FullStack_Resume.pdf')"
⚙️ Configuring GitHub Repository Secrets & ActionsTo enable full daily automation on GitHub:Push your cloned/modified repository to your GitHub account.Go to Settings > Secrets and variables > Actions in your GitHub repository.Click New repository secret and add your credentials:GH_TOKEN: Your Personal Access Token with repo write permissions.GEMINI_API_KEY: Your Gemini API Key.LINKEDIN_ACCESS_TOKEN (if using LinkedIn sync features).Go to Settings > Actions > General. Scroll down to Workflow permissions, select Read and write permissions, and click Save.Now, every time you commit code or every night on schedule, GitHub Actions will automatically update your resume, compile your PDFs, and deploy your fresh portfolio!⚠️ Maintenance Watchouts & Token Lifecycles (Crucial for Long-term Use)Automated pipelines are incredible, but they require periodic check-ins. If your automated workflow suddenly stops updating or fails in GitHub Actions, it is usually due to an expired credential.Keep these key watchouts in mind:1. Token Expiration PitfallsCredentialTypical ExpirationWatchout & Maintenance TipGitHub Personal Access Token (GH_TOKEN)30 to 90 Days (if set) or No Expiration (classic)If set with an expiration date, your workflow will fail when it expires with 401 Unauthorized or Resource protected by organization permission.• Tip: Choose "No Expiration" for Classic Personal Access Tokens, OR set a calendar reminder before the 90-day expiry to regenerate it in GitHub Settings > Developer Settings.LinkedIn OAuth Access Token60 DaysLinkedIn OAuth 2.0 user tokens expire every 60 days. If you use the automated LinkedIn sync script, the API call will return 401 Token Expired.• Tip: Re-authenticate via the LinkedIn Developer Portal or your OAuth flow every two months and update the LINKEDIN_ACCESS_TOKEN secret in GitHub Repository Secrets.Gemini API KeyDoes Not Expire (unless revoked)Free-tier Gemini keys do not expire by date, but they have rate limits (RPM - Requests Per Minute).• Tip: Do not expose this key in public client-side scripts if hosted on a public repo; store it securely in GitHub Secrets.Formspree Form IDDoes Not ExpirePermanent unless you delete the form or hit free-tier monthly submission limits (50 submissions/month).2. GitHub Actions Secrets ChecklistWhenever you renew an API key or access token:Go to your repository on GitHub: Settings > Secrets and variables > Actions.Click Update next to the secret name (e.g., GH_TOKEN or LINKEDIN_ACCESS_TOKEN).Paste the newly generated token and click Update secret.Go to the Actions tab and click Re-run all jobs on the failed workflow run to test.3. Workflow Silent Failure PreventionGitHub Workflow Inactivity Auto-Disable: GitHub automatically disables scheduled workflows (cron) if there is no commit activity in the repository for 60 consecutive days.Fix: If you haven't pushed code in two months, check your Actions tab. If you see a banner saying "Workflows have been disabled due to inactivity", simply click Enable Workflows.Third-Party API Breaking Changes: External public APIs (like LeetCode community endpoints or GitHub API endpoints) occasionally update their response schemas. If LeetCode stats stop rendering on index.html, verify that the API endpoint URL in loadLeetCodeMetrics() is still online.4. How to Debug a Failed PipelineIf a GitHub Action run shows a red X:Click on the failed workflow run under the Actions tab.Click on the failed job step (e.g., Fetch Latest GitHub Projects or Commit and Push Updated Files).Read the terminal log output:401 / 403 Error: Expired or invalid token / secret.Errno 2 No such file or directory: Incorrect path in .github/workflows/daily_automation.yml.Permission to repo denied: Workflow permissions need to be changed to "Read and write permissions" in Settings > Actions > General.
