import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ---------------- Streamlit page ----------------
st.set_page_config(page_title="Binge Eating Profile Test", page_icon="🧠")
st.title("🧠 Binge Eating Profile Test")
st.write("""
Complete the questionnaire honestly.  
You will receive a **full confidential analysis** by email once submitted.
""")

# ---------------- User email ----------------
email = st.text_input("📧 Enter your email to receive your results (required)")

st.write("---")

# ---------------- Questionnaire ----------------
items = [
 # Core DSM
 ("I sometimes eat an amount of food in a short time that most people would consider unusually large.", "L"),
 ("During those episodes, I feel I cannot stop eating or control how much I eat.", "L"),
 ("I eat much more quickly than normal during these episodes.", "L"),
 ("I eat until I feel uncomfortably full.", "L"),
 ("I often eat alone because I am embarrassed by how much I eat.", "L"),
 ("After these episodes, I feel disgusted, depressed, or very guilty.", "L"),
 # Emotional
 ("I binge (or overeat) when I feel stressed, anxious, sad or lonely.", "E"),
 ("I use food to soothe or calm down.", "E"),
 ("I feel temporary relief or comfort while eating during episodes.", "E"),
 ("I tend to hide my eating from others.", "E"),
 # Restriction / rebound
 ("I regularly skip meals or restrict calories to control weight.", "R"),
 ("My binges usually follow a period of strict dieting, fasting, or avoiding carbs.", "R"),
 ("I feel extremely hungry right before a binge episode.", "T"),
 ("I often think 'I'll be good tomorrow' and then lose control later.", "R"),
 # Impulsive
 ("I feel a sudden, intense urge to eat that comes on quickly.", "I"),
 ("I eat very fast during these episodes and feel 'driven'.", "I"),
 ("I feel powerless to resist once the urge hits.", "I"),
 # Habitual
 ("My episodes usually happen at the same time or place.", "H"),
 ("I eat without really thinking about it (automatic or distracted).", "H"),
 ("I tend to binge the same types of food repeatedly.", "H"),
 # Night
 ("Most of my excessive eating happens after dinner or during the night.", "N"),
 ("I wake at night to get food or eat even when not hungry.", "N"),
 # Compensatory / distress
 ("After bingeing I try to compensate by skipping meals or over-exercising.", "R"),
 ("My bingeing causes me significant distress or interferes with life.", "L"),
 ("I have used vomiting, laxatives or other purging behaviors after eating.", "RED"),
 # Insight
 ("If I eat regularly, the episodes become less frequent.", "T"),
 ("I can often identify a clear emotion or situation that starts my binge.", "E"),
 ("I rarely feel hungry before an episode — it is driven by emotion or urge.", "E"),
 ("My appetite is normal outside of episodes.", "T"),
 ("I have tried to stop bingeing and have been unsuccessful repeatedly.", "H")
]

options = ["Never (1)", "Rarely (2)", "Often (3)", "Always (4)"]
score_map = {o: i+1 for i, o in enumerate(options)}

responses = []
for q, tag in items:
    ans = st.radio(q, options, index=0, key=q)
    responses.append((q, tag, score_map[ans]))

# Frequency question
freq = st.selectbox("How often do binge episodes occur?", 
                    ["Less than once/week", "1–3 times/week", "4–7 times/week", "8+ times/week"])

st.write("---")

# ---------------- Submission ----------------
if st.button("📨 Get my results by email"):
    if not email:
        st.warning("Please enter your email.")
        st.stop()

    df = pd.DataFrame(responses, columns=["question", "tag", "score"])

    # --- Functions ---
    def mean_score(tag):
        return df.loc[df.tag.str.contains(tag), "score"].mean()
    
    def max_tag_score(tag_list):
        return max({tag: mean_score(tag) for tag in tag_list}, key=lambda x: mean_score(x))
    
    # --- Compute scores ---
    scores = {
        "Emotional": mean_score("E"),
        "Restraint/Rebound": mean_score("R"),
        "Impulsive": mean_score("I"),
        "Habitual": mean_score("H"),
        "Night": mean_score("N"),
        "True-Hunger": mean_score("T")
    }

    loc_mean = mean_score("L")
    distress = df.loc[df.question.str.contains("distress"), "score"].mean()
    purge = mean_score("RED")

    # --- BED pre-screen ---
    probable_bed = loc_mean >= 3 and distress >= 3 and freq != "Less than once/week"

    # --- Subtype analysis ---
    primary_subtype = max(scores, key=scores.get)
    secondary_subtype = sorted(scores, key=scores.get, reverse=True)[1]

    # True-Hunger vs Rebound
    if scores["Restraint/Rebound"] >= 3 and scores["True-Hunger"] >=3 and loc_mean <3:
        primary_subtype = "Dietary-Rebound / Physiological"
    elif scores["Restraint/Rebound"] >= 3 and scores["Emotional"] >=3:
        primary_subtype = "Restraint-Triggered Emotional"

    # ---------------- Compose deep report ----------------
    report = [f"Hello,\n\nHere is your confidential binge-eating screening report:\n"]

    # BED vs non-BED
    if probable_bed:
        report.append("⚠️ Your answers meet the screening threshold for probable Binge-Eating Disorder (BED). "
                      "This is not a diagnosis, but indicates you may benefit from clinical evaluation.\n")
    else:
        report.append("✅ Your answers do **not** indicate probable Binge-Eating Disorder.\n")

    # Subtypes
    report.append("Subtype analysis:")
    for k, v in scores.items():
        report.append(f"  • {k}: {v:.2f}")
    report.append(f"\nPrimary pattern: {primary_subtype}")
    report.append(f"Secondary pattern: {secondary_subtype}\n")

    # Behavioral insights
    report.append("Behavioral insights:")
    if scores["Emotional"] >=3:
        report.append("  • You are likely influenced by emotions; stress or sadness may trigger overeating.")
    if scores["Restraint/Rebound"] >=3:
        report.append("  • Restrictive eating or dieting may precede episodes of overeating.")
    if scores["Impulsive"] >=3:
        report.append("  • Episodes may occur suddenly with strong urges.")
    if scores["Habitual"] >=3:
        report.append("  • Environmental cues and routines may trigger your eating patterns.")
    if scores["Night"] >=3:
        report.append("  • Eating may be concentrated in the evening or night.")
    if scores["True-Hunger"] >=3 and not probable_bed:
        report.append("  • Episodes are likely driven by genuine physiological hunger, not loss of control.")

    # Red flags
    if purge >=3:
        report.append("\n❗ Red-flag: purging behaviors detected — please seek professional support immediately.")
    if distress >=3 and loc_mean >=3:
        report.append("⚠️ High distress and loss-of-control patterns indicate professional evaluation is recommended.")

    report.append("\nYour free eBook: [Download Here](https://your-ebook-link.com)")
    report.append("\nThis tool is for educational purposes only — not a medical diagnosis.")

    body = "\n".join(report)

    # ---------------- Send email ----------------
    try:
        EMAIL = st.secrets["EMAIL_USER"]
        PASSWORD = st.secrets["EMAIL_PASS"]
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 465

        msg = MIMEMultipart()
        msg["From"] = EMAIL
        msg["To"] = email
        msg["Subject"] = "Your Binge-Eating Profile Results"
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)

        st.success(f"✅ Your full personalized report has been sent to {email}. Check your inbox (and spam folder).")
    except Exception as e:
        st.error(f"Error sending email: {e}")
