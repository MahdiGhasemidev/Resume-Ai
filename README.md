![Resume AI](https://www.recruiter.com/recruiting/wp-content/uploads/2022/07/ai-based-resume-screening.jpg)

# Resume AI

A Streamlit app that extracts text from PDF resumes, parses them into a structured **YAML** format, and reviews/revises each section using **Gemini** (via a **Cloudflare Worker**).

---

## ✨ Features
- 🧾 **PDF extraction** using `PyPDF2`
- 🧱 **YAML parsing** according to a strict schema (`RESUME_YAML_SCHEMA`)
- 🧠 **AI review**: section-by-section suggestions + revised content + impact level (Low/Medium/High)
- 👀 **Debug-friendly UI**: shows Extracted Text, Raw Parse YAML, Raw Review YAML
- 🔐 **Decoupled LLM calls** via a Cloudflare Worker (no API keys in the client app)

---

## 🗂 Project Structure
```
src/
 ├─ app.py               # Streamlit UI
 ├─ resume_formatter.py  # Nicely formats sections for display
 └─ utils/
    ├─ pdf.p            # extract_text_from_pdf (PyPDF2)
    ├─ llm.py         # call_llm / parse_resume / review_resume
    └─ yaml.py      # extract_yaml from model text
prompts.py       # YAML schema + prompts for parse/review
requirements.txt
```

---

## 🛠 Requirements

Dependencies are listed in `requirements.txt`.  Install them with:

```bash
python -m venv .venv && source .venv/bin/activate  # (optional)
pip install -r requirements.txt
```

Tested with Python **3.10+**.

---

## 🔑 Environment Variables

### Local (Streamlit)
Set your Worker URL (public) in your shell or a `.env` file:

```bash
export CWORKERS_GEMINI="https://<your-worker>.<subdomain>.workers.dev/"
```

> The app only needs the **Worker URL**. The **Gemini API key** is stored on Cloudflare, not locally.

### Cloudflare Worker
In Cloudflare Dashboard → your Worker → **Settings → Variables**:

```
Name: GEMINI_API
Value: <your Gemini API key>
```

---

## ☁️ Cloudflare Worker (Minimal Example)

Create `workers.js` with:

```javascript
export default {
  async fetch(request, env) {
    if (request.method !== "POST") {
      return new Response(
        'Send a POST request with JSON: {"prompt":"your text"}',
        { status: 405 }
      );
    }

    let body = {};
    try {
      body = await request.json();
    } catch {
      return new Response(
        JSON.stringify({ error: "Invalid or empty JSON body" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    const prompt = body.prompt || "Hello!";

    try {
      const resp = await fetch(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + env.GEMINI_API,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ contents: [{ role: "user", parts: [{ text: prompt }] }] }),
        }
      );

      const data = await resp.json();
      const text = data?.candidates?.[0]?.content?.parts?.[0]?.text || "⚠️ No response";

      return new Response(JSON.stringify({ text }), {
        headers: { "Content-Type": "application/json" },
      });
    } catch (err) {
      return new Response(JSON.stringify({ error: err.message }), {
        status: 500,
        headers: { "Content-Type": "application/json" },
      });
    }
  },
};
```

Deploy the worker, then copy its public URL to `CWORKERS_GEMINI` locally.

---

## ▶️ Running the App

```bash
# 1) (Optional) create & activate venv
python -m venv .venv && source .venv/bin/activate

# 2) Install deps
pip install -r requirements.txt

# 3) Set Worker URL (only once per shell)
export CWORKERS_GEMINI="https://<your-worker>.workers.dev/"

# 4) Run Streamlit
streamlit run src/app.py
```

Open the app in your browser. In the sidebar:
1. Upload your **PDF** resume
2. (Optional) paste a **Job Description**
3. Click **Run Analysis**

The app shows:
- **Extracted Resume Text** (from the PDF)
- **Raw parse_resume YAML Output**
- **Raw review_resume YAML Output**
- A two-column comparison: **Original** vs **Revised**

---

## 🧪 Debugging & Tips
- If nothing shows up after clicking **Run Analysis**:
  - Check **Extracted Resume Text**. If empty, your PDF may be scanned (image). Use OCR (`pytesseract` + `pdf2image`) or export a text-based PDF.
  - If you see `{"text": "⚠️ No response"}` from the Worker, verify:
    - `CWORKERS_GEMINI` is correct locally
    - `GEMINI_API` is set in Worker Variables
    - The Worker URL responds to:
      ```bash
      curl -X POST "$CWORKERS_GEMINI" -H "Content-Type: application/json" -d '{"prompt":"Hello"}'
      ```
- If YAML parsing fails, simplify your prompt or input and inspect the **Raw YAML Output** blocks in the UI.


---

## 🪪 License

This project is licensed under the [MIT License](LICENSE).

---

## 👨‍💻 Author
**Mahdi Ghasemi**  
📧 Email: mahdi.ghasemi.dev@gmail.com  
🌐 GitHub: [MahdiGhasemidev](https://github.com/MahdiGhasemidev)

---

### ⭐ If you find this project useful, give it a star!