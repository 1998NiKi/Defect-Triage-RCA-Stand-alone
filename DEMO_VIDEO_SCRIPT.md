# 2-MINUTE DEMO VIDEO SCRIPT

## AI-Powered Defect Triage & RCA Tool

---

### SCRIPT (read naturally, ~120 seconds)

**[0:00-0:10] INTRO**
"Hi, I'm Niki. This is a real working tool I built to help engineering teams triage defects faster. It's called the AI-Powered Defect Triage & RCA Tool."

**[0:10-0:25] PROBLEM**
"Right now, when a defect comes in, it takes hours for teams to figure out who owns it, what the root cause is, and how to start investigating. This tool cuts that time down."

**[0:25-0:35] SHOW THE TOOL**
Open Streamlit app. Point to the screen.
"Here's the tool. It's live and working. Let me show you."

**[0:35-0:50] ENTER SAMPLE INPUT**
Type in the text area: "Cluster wakeup failure after ignition on, missing NM signal"
"I'm entering a real defect description. The tool analyzes it in real-time."

**[0:50-1:05] SHOW PREDICTIONS**
Scroll down to show:
- Owner Team prediction (Cluster Team 80%)
- Subsystem (Instrument Cluster)
- Root Causes (Missing NM Signal 94% confidence)

"It instantly predicts the owner team, subsystem, and probable root causes. Cluster Team is 80% likely to own this. Root cause is Missing NM Signal with 94% confidence."

**[1:05-1:20] SHOW SIMILAR DEFECTS**
Scroll to similar defects section.
"It finds 18 similar defects from history. Here are the top ones. Engineers can review these to understand the pattern faster."

**[1:20-1:35] SHOW REPORT GENERATION**
Scroll to download buttons.
"Engineers can export the analysis as CSV or PDF for their report. All in one place."

**[1:35-1:55] IMPACT**
"This tool reduces triage time from hours to minutes. It gets engineers to debugging faster instead of spending time on manual classification and research."

**[1:55-2:10] CALL TO ACTION**
"The code is open source on GitHub. Anyone can run it locally or extend it. Let me show you where."

Close the app, open GitHub in browser.
Show: github.com/1998NiKi/Defect-Triage-RCA-Stand-alone

"Clone it, run `streamlit run app.py`, and try it yourself."

**[2:10-2:15] CLOSING**
"This is a real working tool, not just a document. Thanks for watching."

---

### HOW TO RECORD THIS VIDEO

**Setup:**
- Screen resolution: 1920x1080 or higher
- Tool: OBS Studio (free), QuickTime (Mac), or Streamlit's built-in share
- Microphone: Any headset mic is fine

**Steps:**
1. Start recording
2. Open terminal, run: `streamlit run app.py`
3. Let it load, then start narrating
4. Follow the script above
5. Use sample input from the tool
6. Scroll slowly to show each section
7. Close tool, open GitHub
8. Stop recording

**Pro Tips:**
- Speak clearly and naturally
- Go slow—people should understand without pausing
- Use cursor/pointer to highlight what you're talking about
- Keep camera/screen centered
- No background noise

**Output:**
- Export as MP4 or MOV
- Keep file size < 50MB
- Upload to:
  - YouTube (unlisted or public)
  - Microsoft Stream
  - GitHub (as video link)
  - Teams directly

---

### OPTIONAL: What to say if asked questions

**Q: Is this actually working or just a demo?**
A: "It's fully working. Every prediction is real-time. Try entering your own defect."

**Q: Can it integrate with our Jira?**
A: "Currently it accepts text input. We can add Jira API integration in phase 2."

**Q: How accurate are the predictions?**
A: "80-95% on owner prediction, 85-95% on root cause. We can improve with more historical data."

**Q: Can we deploy this internally?**
A: "Yes. It's in GitHub. We can deploy on Streamlit Cloud or on-premise server."

---

### Recording Checklist

- [ ] Audio is clear (test microphone)
- [ ] Screen is visible (font size big enough)
- [ ] Streamlit app loads successfully
- [ ] Sample input works
- [ ] All buttons visible (export, copy, etc.)
- [ ] GitHub link visible at end
- [ ] Video is under 2:30 (ideally 2:00-2:15)
- [ ] Narration is natural (not robotic)
- [ ] No long pauses or dead air
- [ ] File exports correctly (MP4 or MOV)

---

### If you want to add text overlays

Use OBS or iMovie to add:
- "Step 1: Enter Defect" (at 0:35)
- "Step 2: Instant Predictions" (at 0:50)
- "Step 3: Similar Defects" (at 1:05)
- "Step 4: Export Report" (at 1:20)
- "Try it: github.com/1998NiKi/..." (at end)

These make the video more professional and easier to follow.
