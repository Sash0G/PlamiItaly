import pandas as pd
import json
import re
import os
import hashlib

# -------------------------------------------------------------------------
# 1. Configuration
# -------------------------------------------------------------------------
INPUT_CSV = 'set5.csv'
OUTPUT_HTML = 'index.html'

# Mapping Cyrillic answers to Latin Options
ANSWER_MAPPING = {
    'а': 'A', 'б': 'B', 'в': 'C', 'г': 'D', 'д': 'E',
    'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D', 'E': 'E'
}

# -------------------------------------------------------------------------
# 2. Parse CSV Data
# -------------------------------------------------------------------------
def parse_csv(filename):
    if not os.path.exists(filename):
        print(f"Error: {filename} not found.")
        return []

    try:
        df = pd.read_csv(filename, sep=';', header=None, engine='python')
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return []

    questions_data = []
    
    for idx, row in df.iterrows():
        q_text = str(row[0]).strip()
        
        # --- STABLE HASHING (MD5) ---
        # ensures ID stays same even if file order changes
        q_id = hashlib.md5(q_text.encode('utf-8')).hexdigest()

        options = []
        letters = ['A', 'B', 'C', 'D', 'E']
        for i, letter in enumerate(letters):
            col_idx = i + 1
            val = row[col_idx]
            if pd.notna(val):
                clean_text = re.sub(r'^[A-Ea-e]\)\s*', '', str(val)).strip()
                options.append({'id': letter, 'text': clean_text})

        raw_correct = str(row[6]).strip().lower()
        correct_letter = ANSWER_MAPPING.get(raw_correct, None)

        if q_text and options and correct_letter:
            questions_data.append({
                'id': q_id,
                'q': q_text,
                'opts': options,
                'a': correct_letter
            })
            
    return questions_data

print("Reading CSV...")
questions_json = json.dumps(parse_csv(INPUT_CSV))
print(f"Processed {len(json.loads(questions_json))} questions.")

# -------------------------------------------------------------------------
# 3. HTML Template
# -------------------------------------------------------------------------
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Quiz App</title>
    <style>
        :root {{ --primary: #007aff; --bg: #f2f2f7; --card: #ffffff; --text: #000; --border: #c6c6c8; }}
        
        * {{ box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: var(--bg); color: var(--text); 
            padding: 20px; margin: 0;
            display: flex; justify-content: center; 
        }}
        
        .container {{ 
            width: 100%; max-width: 800px; 
            background: var(--card); 
            padding: 25px; 
            border-radius: 16px; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.08); 
        }}
        
        h1, h2 {{ text-align: center; color: var(--primary); margin-top: 0; }}
        
        /* Buttons (iOS style) */
        button {{ 
            background: var(--primary); color: white; border: none; 
            padding: 14px 24px; font-size: 17px; font-weight: 600; 
            border-radius: 12px; cursor: pointer; width: 100%; 
            touch-action: manipulation;
            transition: opacity 0.2s;
        }}
        button:active {{ opacity: 0.7; }}
        .btn-secondary {{ background: #8e8e93; margin-top: 15px; }}
        
        /* Inputs */
        input[type="number"] {{ 
            padding: 12px; font-size: 18px; width: 100px; 
            text-align: center; border: 1px solid var(--border); 
            border-radius: 8px; -webkit-appearance: none; 
        }}
        
        /* Quiz List */
        .question-block {{ margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #eee; }}
        .q-text {{ font-size: 1.1em; font-weight: 600; margin-bottom: 15px; line-height: 1.4; }}
        
        /* Options (Touch Friendly) */
        .options label {{ 
            display: flex; align-items: center;
            padding: 14px; margin: 8px 0; 
            background: #fafafa; border: 1px solid #eee; 
            border-radius: 10px; cursor: pointer; 
            font-size: 16px;
            touch-action: manipulation;
        }}
        
        /* Custom Radio Indicator */
        .options input {{ 
            margin-right: 12px; transform: scale(1.3); accent-color: var(--primary);
        }}
        
        /* Selected State for feedback */
        .options label:has(input:checked) {{
            background-color: #eef5ff; border-color: var(--primary);
        }}

        /* Results */
        .result-row {{ padding: 15px; border-bottom: 1px solid #eee; }}
        .status {{ font-weight: bold; margin-bottom: 4px; }}
        .correct {{ color: #34c759; }}
        .incorrect {{ color: #ff3b30; }}
        .ans-text {{ color: #555; font-size: 0.95em; }}

        .hidden {{ display: none !important; }}
    </style>
</head>
<body>

<div class="container" id="app">
    <div id="start-screen">
        <h1>Quiz Time</h1>
        <p style="text-align:center; color:#666;">Total Questions: <span id="total-q">0</span></p>
        
        <div style="text-align:center; margin: 40px 0;">
            <label for="num-q" style="display:block; margin-bottom:10px; font-weight:bold;">Questions to Practice</label>
            <input type="number" id="num-q" value="10" min="1">
            <br><br><br>
            <button onclick="startQuiz(false)">Start Quiz</button>
            <button onclick="resetData()" class="btn-secondary" style="background: transparent; color: #ff3b30; margin-top:30px; font-size:14px;">Reset Learning Progress</button>
        </div>
    </div>

    <div id="quiz-screen" class="hidden">
        <h2 id="round-title">Quiz</h2>
        <div id="questions-container"></div>
        <div style="padding: 20px 0;">
            <button onclick="submitQuiz()">Submit Answers</button>
        </div>
    </div>

    <div id="result-screen" class="hidden">
        <h2>Results</h2>
        <div style="text-align: center; margin-bottom: 25px;">
            <h3 id="score-summary" style="margin-bottom:5px;"></h3>
            <p id="retry-msg" style="color:#666; font-size:0.9em; margin-top:0;"></p>
        </div>
        
        <div id="action-area" style="margin-bottom: 30px;">
            </div>

        <div id="results-list"></div>
    </div>
</div>

<script>
    const allQuestions = {questions_json};
    const STORAGE_KEY = 'quiz_v2_scores'; // Changed key for V2 (MD5)
    
    // State
    let currentQuiz = [];
    let wrongQuestions = [];
    let isRetryMode = false; // true if we are in "Retry Wrong" phase

    document.getElementById('total-q').textContent = allQuestions.length;
    document.getElementById('num-q').max = allQuestions.length;

    // --- DATA LOGIC ---

    function getScores() {{
        const s = localStorage.getItem(STORAGE_KEY);
        return s ? JSON.parse(s) : {{}};
    }}

    function saveScores(scores) {{
        localStorage.setItem(STORAGE_KEY, JSON.stringify(scores));
    }}

    function getWeight(score) {{
        if (score === 0) return 1.0;
        if (score >= 1 && score <= 2) return 0.5;
        return 0.2;
    }}

    function shuffleArray(array) {{
        for (let i = array.length - 1; i > 0; i--) {{
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }}
        return array;
    }}

    // --- MAIN FLOW ---

    function startQuiz(isRetry) {{
        isRetryMode = isRetry;
        
        if (!isRetry) {{
            // FRESH START: Select Weighted
            const num = parseInt(document.getElementById('num-q').value) || 10;
            currentQuiz = selectWeightedQuestions(allQuestions, num);
            document.getElementById('round-title').textContent = "Quiz";
        }} else {{
            // RETRY: Use the wrong questions from previous round
            currentQuiz = [...wrongQuestions];
            document.getElementById('round-title').textContent = "Retry Incorrect";
        }}

        renderQuiz();
        switchScreen('quiz-screen');
    }}

    function selectWeightedQuestions(pool, count) {{
        let scores = getScores();
        let selected = [];
        let available = [...pool];
        count = Math.min(count, available.length);

        for (let i = 0; i < count; i++) {{
            let totalWeight = 0;
            let weightedPool = available.map(q => {{
                let s = scores[q.id] || 0;
                let w = getWeight(s);
                totalWeight += w;
                return {{ ...q, _w: w }};
            }});

            let r = Math.random() * totalWeight;
            let running = 0;
            let pickIndex = -1;

            for (let j = 0; j < weightedPool.length; j++) {{
                running += weightedPool[j]._w;
                if (r <= running) {{
                    pickIndex = j;
                    break;
                }}
            }}
            if (pickIndex === -1) pickIndex = weightedPool.length - 1;

            selected.push(weightedPool[pickIndex]);
            available.splice(pickIndex, 1);
        }}
        return selected;
    }}

    function renderQuiz() {{
        const container = document.getElementById('questions-container');
        container.innerHTML = '';

        currentQuiz.forEach((q, index) => {{
            // Always shuffle options for display
            let displayOpts = [...q.opts];
            shuffleArray(displayOpts);

            let html = `
                <div class="question-block">
                    <div class="q-text">${{index + 1}}. ${{q.q}}</div>
                    <div class="options">
            `;
            
            displayOpts.forEach(opt => {{
                html += `
                    <label>
                        <input type="radio" name="q_${{q.id}}" value="${{opt.id}}">
                        ${{opt.text}}
                    </label>
                `;
            }});

            html += `</div></div>`;
            container.innerHTML += html;
        }});
        window.scrollTo(0,0);
    }}

    function submitQuiz() {{
        let scores = getScores();
        let resultsHTML = '';
        let correctCount = 0;
        
        // Reset wrong questions for the *next* potential retry
        let nextWrongQuestions = [];

        currentQuiz.forEach((q, idx) => {{
            const inputs = document.getElementsByName(`q_${{q.id}}`);
            let userVal = null;
            for(let inp of inputs) if(inp.checked) userVal = inp.value;

            const isCorrect = (userVal === q.a);
            
            // --- SCORING (Only if NOT in retry mode) ---
            if (!isRetryMode) {{
                let oldScore = scores[q.id] || 0;
                let newScore = oldScore;
                
                if (isCorrect) {{
                    newScore = oldScore + 2;
                }} else {{
                    newScore = (oldScore === 1) ? 0 : 1;
                }}
                scores[q.id] = newScore;
            }}

            if (isCorrect) {{
                correctCount++;
            }} else {{
                nextWrongQuestions.push(q);
            }}

            // --- DISPLAY LOGIC ---
            // Find text of correct answer
            let correctOpt = q.opts.find(o => o.id === q.a);
            let correctText = correctOpt ? correctOpt.text : q.a;

            let statusClass = isCorrect ? 'correct' : 'incorrect';
            let statusLabel = isCorrect ? 'Correct' : 'Incorrect';
            
            // Only show detailed answer text if wrong (or if you want to confirm correct text too)
            let answerDisplay = isCorrect 
                ? `<span class="ans-text">Answer: ${{(userVal ? (q.opts.find(o=>o.id==userVal)?.text || userVal) : "None")}}</span>`
                : `<span class="ans-text">Correct Answer: <strong>${{correctText}}</strong></span>`;

            resultsHTML += `
                <div class="result-row">
                    <div style="margin-bottom:5px;"><strong>${{idx+1}}. ${{q.q}}</strong></div>
                    <div class="status ${{statusClass}}">${{statusLabel}}</div>
                    ${{answerDisplay}}
                </div>
            `;
        }});

        // Save scores only if this was the first run
        if (!isRetryMode) {{
            saveScores(scores);
        }}

        // Setup State for Next Step
        wrongQuestions = nextWrongQuestions;
        
        // Render Results Screen
        document.getElementById('score-summary').textContent = `${{correctCount}} / ${{currentQuiz.length}} Correct`;
        document.getElementById('results-list').innerHTML = resultsHTML;

        // Setup Buttons
        const actionArea = document.getElementById('action-area');
        if (wrongQuestions.length > 0) {{
            document.getElementById('retry-msg').textContent = "You must clear all errors to finish.";
            actionArea.innerHTML = `
                <button onclick="startQuiz(true)" style="background:#ff9500;">
                    Retry ${{wrongQuestions.length}} Incorrect Questions
                </button>
            `;
        }} else {{
            document.getElementById('retry-msg').textContent = "Excellent work!";
            actionArea.innerHTML = `
                <button onclick="location.reload()" style="background:#34c759;">
                    Start New Quiz
                </button>
            `;
        }}

        switchScreen('result-screen');
    }}

    function switchScreen(id) {{
        ['start-screen', 'quiz-screen', 'result-screen'].forEach(s => {{
            document.getElementById(s).classList.add('hidden');
        }});
        document.getElementById(id).classList.remove('hidden');
        window.scrollTo(0,0);
    }}

    function resetData() {{
        if(confirm("Delete all learning progress and weights?")) {{
            localStorage.removeItem(STORAGE_KEY);
            alert("Done.");
        }}
    }}
</script>

</body>
</html>
"""

# -------------------------------------------------------------------------
# 4. Write Output
# -------------------------------------------------------------------------
with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"SUCCESS! Created '{OUTPUT_HTML}'.")