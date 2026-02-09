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

ANSWER_MAPPING = {
    'а': 'A', 'б': 'B', 'в': 'C', 'г': 'D', 'д': 'E',
    'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D', 'E': 'E'
}

# -------------------------------------------------------------------------
# 2. Parse CSV Data (Same Logic as Before)
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
        q_id = hashlib.md5(q_text.encode('utf-8')).hexdigest()

        options = []
        letters = ['A', 'B', 'C', 'D', 'E']
        for i, letter in enumerate(letters):
            col_idx = i + 1
            val = row[col_idx]
            if pd.notna(val):
                clean_text = re.sub(r'^[A-Z](\s*[\)\.]|\s+)\s*', '', str(val)).strip()
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
# 3. HTML Template (Architecture Theme)
# -------------------------------------------------------------------------
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Italy</title>
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap" rel="stylesheet">

    <style>
        :root {{
            --primary: #2c3e50;      /* Slate Blue/Grey */
            --accent: #c0392b;       /* Terracotta Red */
            --bg: #fdfbf7;           /* Warm Paper */
            --card-bg: #ffffff;
            --text: #2c3e50;
            --border: #dcdcdc;
            --correct: #27ae60;
            --incorrect: #c0392b;
        }}
        
        * {{ box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
        
        body {{ 
            font-family: 'Lato', sans-serif;
            background-color: var(--bg);
            background-image: radial-gradient(#e0e0e0 1px, transparent 1px);
            background-size: 20px 20px;
            color: var(--text); 
            padding: 20px; margin: 0;
            display: flex; justify-content: center; 
            min-height: 100vh;
        }}
        
        .container {{ 
            width: 100%; max-width: 800px; 
            background: var(--card-bg); 
            padding: 40px; 
            border: 1px solid var(--border);
            box-shadow: 10px 10px 0px rgba(0,0,0,0.05); /* Architectural Block Shadow */
            position: relative;
        }}
        
        /* Decorative Top Border */
        .container::before {{
            content: "";
            position: absolute; top: 0; left: 0; right: 0;
            height: 6px;
            background: var(--primary);
        }}

        h1, h2 {{ 
            font-family: 'Playfair Display', serif; 
            text-align: center; 
            color: var(--primary); 
            margin-top: 0; 
            letter-spacing: 0.5px;
        }}
        
        h1 {{ font-size: 2.2em; border-bottom: 2px solid #eee; padding-bottom: 20px; }}
        
        /* Buttons */
        button {{ 
            background: var(--primary); color: white; border: none; 
            padding: 16px 24px; font-size: 16px; font-family: 'Lato', sans-serif; 
            text-transform: uppercase; letter-spacing: 1px; font-weight: bold;
            cursor: pointer; width: 100%; 
            transition: all 0.2s;
            border-radius: 2px; /* Sharper corners for architectural feel */
        }}
        
        button:active {{ transform: translateY(2px); }}
        
        .btn-retry {{ background: var(--accent); }}
        .btn-reset {{ 
            background: transparent; color: #999; 
            text-transform: none; font-weight: normal; 
            margin-top: 30px; border: 1px dashed #ccc;
        }}
        
        /* Inputs */
        .input-group {{ text-align: center; margin: 40px 0; }}
        input[type="number"] {{ 
            padding: 10px; font-size: 20px; width: 100px; 
            text-align: center; border: 2px solid var(--primary); 
            font-family: 'Playfair Display', serif;
            background: #fafafa;
        }}
        
        /* Questions */
        .question-block {{ 
            margin-bottom: 40px; 
            padding-bottom: 30px; 
            border-bottom: 1px solid #eee; 
        }}
        
        .q-text {{ 
            font-family: 'Playfair Display', serif;
            font-size: 1.3em; 
            font-weight: 600; 
            margin-bottom: 20px; 
            line-height: 1.4; 
            color: #000;
        }}
        
        /* Options */
        .options label {{ 
            display: flex; align-items: center;
            padding: 16px; margin: 10px 0; 
            background: #fff; border: 1px solid #ddd; 
            cursor: pointer; 
            font-size: 17px;
            transition: all 0.2s;
            position: relative;
        }}
        
        /* Hover/Touch State */
        .options label:hover {{ border-color: var(--primary); background: #f8f9fa; }}
        
        /* Selected State */
        .options label:has(input:checked) {{
            background-color: #f0f4f8; 
            border-color: var(--primary);
            border-left: 5px solid var(--primary); /* Accent mark */
        }}

        .options input {{ 
            margin-right: 15px; 
            width: 20px; height: 20px;
            accent-color: var(--primary);
        }}

        /* Results */
        .result-row {{ 
            padding: 20px; 
            background: #fdfdfd;
            border-bottom: 1px solid #eee;
            margin-bottom: 10px;
        }}
        
        .status {{ 
            font-family: 'Playfair Display', serif;
            font-weight: bold; 
            font-size: 1.1em;
            margin: 10px 0; 
        }}
        .correct {{ color: var(--correct); }}
        .incorrect {{ color: var(--incorrect); }}
        
        .ans-text {{ 
            display: block; 
            margin-top: 5px; 
            color: #555; 
            font-style: italic;
        }}

        .hidden {{ display: none !important; }}
    </style>
</head>
<body>

<div class="container" id="app">
    <div id="start-screen">
        <h1></h1>
        <div class="input-group">
            <p style="margin-bottom: 10px; color: #666;">Total Archive Size: <span id="total-q">0</span> questions</p>
            <label for="num-q" style="display:block; margin-bottom:15px; font-weight:bold; font-size: 1.1em;">Session Length</label>
            <input type="number" id="num-q" value="75" min="1">
            
            <div style="margin-top: 40px;">
                <button onclick="startQuiz(false)">Begin Session</button>
            </div>
            
            <button onclick="resetData()" class="btn-reset">Reset Academic Progress</button>
        </div>
    </div>

    <div id="quiz-screen" class="hidden">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 2px solid #eee; padding-bottom: 10px;">
            <h2 id="round-title" style="margin:0; font-size: 1.5em;">Examination</h2>
            <span style="font-size: 0.9em; color: #777;"></span>
        </div>

        <div id="questions-container"></div>
        
        <div style="padding: 20px 0;">
            <button onclick="submitQuiz()">Submit Answers</button>
        </div>
    </div>

    <div id="result-screen" class="hidden">
        <h1>Evaluation</h1>
        <div style="text-align: center; margin-bottom: 30px; background: #f9f9f9; padding: 20px; border: 1px solid #eee;">
            <h3 id="score-summary" style="margin: 0; font-size: 1.8em; font-family: 'Playfair Display', serif;"></h3>
            <p id="retry-msg" style="color:#666; margin-top:10px;"></p>
        </div>
        
        <div id="action-area" style="margin-bottom: 40px;"></div>

        <div id="results-list"></div>
    </div>
</div>

<script>
    const allQuestions = {questions_json};
    const STORAGE_KEY = 'arch_quiz_v1';
    
    // State
    let currentQuiz = [];
    let wrongQuestions = [];
    let isRetryMode = false;

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
            const num = parseInt(document.getElementById('num-q').value) || 10;
            currentQuiz = selectWeightedQuestions(allQuestions, num);
            document.getElementById('round-title').textContent = "Examination";
        }} else {{
            currentQuiz = [...wrongQuestions];
            document.getElementById('round-title').textContent = "Review Incorrect";
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
            let displayOpts = [...q.opts];
            shuffleArray(displayOpts);

            let html = `
                <div class="question-block">
                    <div class="q-text"><span style="color:var(--primary);">${{index + 1}}.</span> ${{q.q}}</div>
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
        let nextWrongQuestions = [];

        currentQuiz.forEach((q, idx) => {{
            const inputs = document.getElementsByName(`q_${{q.id}}`);
            let userVal = null;
            for(let inp of inputs) if(inp.checked) userVal = inp.value;

            const isCorrect = (userVal === q.a);
            
            if (!isRetryMode) {{
                let oldScore = scores[q.id] || 0;
                let newScore = oldScore;
                if (isCorrect) newScore = oldScore + 2;
                else newScore = (oldScore === 1) ? 0 : 1;
                scores[q.id] = newScore;
            }}

            if (isCorrect) correctCount++;
            else nextWrongQuestions.push(q);

            let correctOpt = q.opts.find(o => o.id === q.a);
            let correctText = correctOpt ? correctOpt.text : q.a;
            let statusClass = isCorrect ? 'correct' : 'incorrect';
            let statusLabel = isCorrect ? 'Correct' : 'Incorrect';
            
            let answerDisplay = isCorrect 
                ? `<span class="ans-text">Your answer: ${{(userVal ? (q.opts.find(o=>o.id==userVal)?.text || userVal) : "None")}}</span>`
                : `<span class="ans-text">Correct Answer: <strong>${{correctText}}</strong></span>`;

            resultsHTML += `
                <div class="result-row">
                    <div style="font-family: 'Playfair Display', serif; font-size: 1.1em; margin-bottom: 8px;">
                        ${{idx+1}}. ${{q.q}}
                    </div>
                    <div class="status ${{statusClass}}">${{statusLabel}}</div>
                    ${{answerDisplay}}
                </div>
            `;
        }});

        if (!isRetryMode) saveScores(scores);

        wrongQuestions = nextWrongQuestions;
        
        document.getElementById('score-summary').textContent = `${{correctCount}} / ${{currentQuiz.length}} Correct`;
        document.getElementById('results-list').innerHTML = resultsHTML;

        const actionArea = document.getElementById('action-area');
        if (wrongQuestions.length > 0) {{
            document.getElementById('retry-msg').textContent = "Review required for incorrect answers.";
            actionArea.innerHTML = `
                <button onclick="startQuiz(true)" class="btn-retry">
                    Retry ${{wrongQuestions.length}} Incorrect Items
                </button>
            `;
        }} else {{
            document.getElementById('retry-msg').textContent = "Excellent. Session complete.";
            actionArea.innerHTML = `
                <button onclick="location.reload()">
                    Start New Session
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
        if(confirm("This will erase all study history. Proceed?")) {{
            localStorage.removeItem(STORAGE_KEY);
            alert("History cleared.");
            location.reload();
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