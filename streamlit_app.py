import json
import random

import streamlit as st


COLORS = {
    "red": "#FF0000",
    "blue": "#0000FF",
    "green": "#008000",
    "orange": "#FFA500",
    "yellow": "#FFFF00",
    "purple": "#800080",
    "black": "#000000",
    "white": "#FFFFFF",
}


def generate_frames(count):
    names = list(COLORS)
    recent_words, recent_text, recent_backgrounds = [], [], []
    frames = []

    for _ in range(count):
        word = random.choice([x for x in names if x not in recent_words])
        ink = random.choice([x for x in names if x not in recent_text])
        background = random.choice(
            [x for x in names if x != ink and x not in recent_backgrounds]
        )

        frames.append({
            "word": word,
            "color": COLORS[ink],
            "bg": COLORS[background],
            "top": random.randint(15, 75),
            "left": random.randint(15, 65),
        })

        for recent, choice in (
            (recent_words, word),
            (recent_text, ink),
            (recent_backgrounds, background),
        ):
            recent.append(choice)
            if len(recent) > 2:
                recent.pop(0)

    return frames


STROOP_HTML = """
<style>
  body { margin: 0; font-family: Arial, sans-serif; }
  button { padding: 12px 22px; border: 0; border-radius: 6px;
           cursor: pointer; font-weight: bold; font-size: 16px; }
  #start { background: #28a745; color: white; margin: 0 0 12px; }
  #test { display: none; position: relative; height: 500px;
          background: black; border-radius: 8px; overflow: hidden; }
  #stop { position: absolute; top: 12px; right: 12px; z-index: 2;
          background: #333; color: white; padding: 8px 12px; font-size: 14px; }
  #canvas { position: relative; height: 100%; width: 100%;
            transition: background-color .15s; }
  #word { position: absolute; font-size: clamp(30px, 5vw, 48px);
          font-weight: bold; white-space: nowrap; text-transform: uppercase;
          text-shadow: 1px 1px 3px #555; }
</style>
<button id="start">Start Stroop Presentation</button>
<div id="test">
  <button id="stop">Stop Test</button>
  <div id="canvas"><span id="word"></span></div>
</div>
<script>
  const frames = __FRAMES__;
  const intervalMs = __INTERVAL__;
  const test = document.getElementById('test');
  const canvas = document.getElementById('canvas');
  const word = document.getElementById('word');
  let index = 0;
  let timer = null;

  function stopTimer() {
    if (timer !== null) { clearInterval(timer); timer = null; }
  }

  function showNext() {
    if (index >= frames.length) {
      stopTimer();
      canvas.style.backgroundColor = '#111';
      word.style.color = 'white';
      word.style.left = '50%';
      word.style.top = '50%';
      word.style.transform = 'translate(-50%, -50%)';
      word.textContent = 'TEST COMPLETE';
      return;
    }
    const frame = frames[index++];
    canvas.style.backgroundColor = frame.bg;
    word.style.color = frame.color;
    word.style.left = frame.left + '%';
    word.style.top = frame.top + '%';
    word.style.transform = 'none';
    word.textContent = frame.word;
  }

  document.getElementById('start').addEventListener('click', () => {
    stopTimer();
    index = 0;
    test.style.display = 'block';
    showNext();
    timer = setInterval(showNext, intervalMs);
  });

  document.getElementById('stop').addEventListener('click', () => {
    stopTimer();
    test.style.display = 'none';
  });
</script>
"""


st.set_page_config(page_title="Stroop Test", layout="wide")
st.title("Stroop Test")
st.write("Set the duration and the time between color changes, then generate your test.")

with st.form("stroop_settings"):
    duration_minutes = st.number_input(
        "Total duration (minutes)", min_value=0.1, value=1.0, step=0.5
    )
    frequency_seconds = st.number_input(
        "Seconds between visual changes", min_value=0.1, value=3.0, step=0.5
    )
    generate = st.form_submit_button("Generate test")

if generate:
    count = max(1, int(duration_minutes * 60 / frequency_seconds))
    st.session_state["stroop_frames"] = generate_frames(count)
    st.session_state["stroop_interval"] = int(frequency_seconds * 1000)

if "stroop_frames" in st.session_state:
    st.success(f"Test ready: {len(st.session_state['stroop_frames'])} color changes.")
    html = (STROOP_HTML
            .replace("__FRAMES__", json.dumps(st.session_state["stroop_frames"]))
            .replace("__INTERVAL__", str(st.session_state["stroop_interval"])))
    st.iframe(html, height=565, alt="Interactive Stroop color presentation")
else:
    st.info("Choose your settings and click Generate test.")
