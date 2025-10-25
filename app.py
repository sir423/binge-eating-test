import streamlit as st

st.title("🧠 Binge Eating Profile Test")

st.write("""
Answer the questions below honestly to understand your eating patterns.
This test is confidential and meant for self-awareness.
""")

# Example questions
q1 = st.radio("Do you often eat large amounts of food even when not physically hungry?", ["Never", "Sometimes", "Often", "Always"])
q2 = st.radio("Do you eat in secret or hide evidence of your eating?", ["Never", "Sometimes", "Often", "Always"])
q3 = st.radio("Do you feel guilt, shame, or disgust after eating?", ["Never", "Sometimes", "Often", "Always"])

# Simple scoring logic
score_map = {"Never": 0, "Sometimes": 1, "Often": 2, "Always": 3}
score = score_map[q1] + score_map[q2] + score_map[q3]

st.write("---")

if st.button("Show my result"):
    if score <= 2:
        st.success("✅ Mild or situational overeating — you likely eat normally most of the time.")
    elif score <= 5:
        st.warning("⚠️ Emotional or stress-triggered eating — your hunger may be linked to emotions or environment.")
    else:
        st.error("🚨 Possible binge eating behavior — consider exploring emotional triggers and seeking support if needed.")
