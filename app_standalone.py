"""
JoSAA Choice Filling Assistant - Single File Version
All HTML embedded in this file - no separate templates folder needed!
"""

from flask import Flask, request, jsonify
import pandas as pd
from pathlib import Path

app = Flask(__name__)

# NIRF 2024 Rankings (Top Engineering Colleges)
NIRF_RANKINGS = {
    "Indian Institute of Technology Madras": 1,
    "Indian Institute of Technology Delhi": 2,
    "Indian Institute of Technology Bombay": 3,
    "Indian Institute of Technology Kanpur": 4,
    "Indian Institute of Technology Kharagpur": 5,
    "Indian Institute of Technology Roorkee": 6,
    "Indian Institute of Technology Guwahati": 7,
    "Indian Institute of Technology Hyderabad": 8,
    "National Institute of Technology Tiruchirappalli": 9,
    "Indian Institute of Technology (Indian School of Mines) Dhanbad": 10,
    "Indian Institute of Technology Indore": 11,
    "Indian Institute of Technology (BHU) Varanasi": 12,
    "Indian Institute of Technology Ropar": 13,
    "Anna University": 14,
    "National Institute of Technology Karnataka Surathkal": 15,
    "Jadavpur University": 16,
    "National Institute of Technology Rourkela": 17,
    "Amrita Vishwa Vidyapeetham": 18,
    "Indian Institute of Technology Bhubaneswar": 19,
    "Vellore Institute of Technology": 20,
    "Indian Institute of Technology Gandhinagar": 21,
    "Indian Institute of Technology Patna": 22,
    "National Institute of Technology Warangal": 23,
    "Indian Institute of Technology Jodhpur": 24,
    "Birla Institute of Technology and Science Pilani": 25,
    "National Institute of Technology Calicut": 26,
    "Motilal Nehru National Institute of Technology Allahabad": 27,
    "Visvesvaraya National Institute of Technology Nagpur": 28,
    "Indian Institute of Technology Mandi": 29,
    "Jamia Millia Islamia": 30,
}

# Branch preference scores
BRANCH_SCORES = {
    "Computer Science and Engineering": 100,
    "Artificial Intelligence": 98,
    "Data Science": 97,
    "Computer Science": 100,
    "Information Technology": 95,
    "Electronics and Communication Engineering": 90,
    "Electrical Engineering": 85,
    "Mechanical Engineering": 80,
    "Civil Engineering": 75,
    "Chemical Engineering": 73,
    "Aerospace Engineering": 82,
    "Biotechnology": 70,
    "Mathematics and Computing": 96,
    "Engineering Physics": 78,
}

class ChoiceFillingAssistant:
    def __init__(self, josaa_csv_path=None):
        self.df = None
        if josaa_csv_path and Path(josaa_csv_path).exists():
            self.load_data(josaa_csv_path)
    
    def load_data(self, csv_path):
        try:
            self.df = pd.read_csv(csv_path)
            print(f"✓ Loaded {len(self.df)} records from {csv_path}")
        except Exception as e:
            print(f"✗ Error loading data: {e}")
            self.df = None
    
    def normalize_institute_name(self, name):
        if not isinstance(name, str):
            return name
        name = name.replace("IIT", "Indian Institute of Technology")
        name = name.replace("NIT", "National Institute of Technology")
        return name.strip()
    
    def get_nirf_rank(self, institute_name):
        normalized = self.normalize_institute_name(institute_name)
        if normalized in NIRF_RANKINGS:
            return NIRF_RANKINGS[normalized]
        for nirf_name, rank in NIRF_RANKINGS.items():
            if nirf_name.lower() in normalized.lower() or normalized.lower() in nirf_name.lower():
                return rank
        return 999
    
    def get_branch_score(self, branch_name):
        if not isinstance(branch_name, str):
            return 50
        branch_lower = branch_name.lower()
        for key, score in BRANCH_SCORES.items():
            if key.lower() in branch_lower:
                return score
        return 50
    
    def calculate_choice_score(self, row, user_prefs):
        score = 0
        nirf_rank = self.get_nirf_rank(row.get('Institute', ''))
        nirf_score = max(0, 40 - (nirf_rank * 0.5))
        score += nirf_score
        
        branch_score = self.get_branch_score(row.get('Academic Program Name', ''))
        branch_score_normalized = (branch_score / 100) * 30
        score += branch_score_normalized
        
        try:
            closing_rank = float(row.get('Closing Rank', 999999))
            user_rank = user_prefs.get('rank', 999999)
            if closing_rank > 0:
                safety_margin = (closing_rank - user_rank) / closing_rank
                safety_score = min(30, max(0, safety_margin * 30))
                score += safety_score
        except:
            pass
        
        return score
    
    def get_recommendations(self, user_prefs):
        if self.df is None:
            return {'error': 'No data loaded', 'recommendations': []}
        
        filtered_df = self.df.copy()
        user_rank = user_prefs.get('rank', 0)
        exam_type = user_prefs.get('exam_type', 'advanced')
        
        print(f"\n=== DEBUG INFO ===")
        print(f"Starting with {len(filtered_df)} total records")
        print(f"User rank: {user_rank}, Exam type: {exam_type}")
        
        # CRITICAL: Filter by exam type
        if exam_type == 'advanced':
            # JEE Advanced - Show only IITs (Indian Institute of Technology)
            filtered_df = filtered_df[
                filtered_df['Institute'].str.contains('Indian Institute of Technology', case=False, na=False)
            ]
            print(f"After IIT filter: {len(filtered_df)} records")
        else:
            # JEE Main - Show NITs, IIITs, GFTIs (exclude IITs but keep IIITs)
            filtered_df = filtered_df[
                ~filtered_df['Institute'].str.contains('Indian Institute of Technology', case=False, na=False)
            ]
            print(f"After non-IIT filter: {len(filtered_df)} records")
        
        if 'Closing Rank' in filtered_df.columns:
            filtered_df['Closing Rank'] = pd.to_numeric(filtered_df['Closing Rank'], errors='coerce')
            print(f"Closing rank range: {filtered_df['Closing Rank'].min()} - {filtered_df['Closing Rank'].max()}")
            
            # Filter: closing rank should be >= user rank * 0.8 (safety margin)
            before_rank_filter = len(filtered_df)
            filtered_df = filtered_df[filtered_df['Closing Rank'] >= user_rank * 0.8]
            print(f"After rank filter (closing >= {user_rank * 0.8}): {len(filtered_df)} records (removed {before_rank_filter - len(filtered_df)})")
        
        category = user_prefs.get('category')
        if category and 'Seat Type' in filtered_df.columns:
            before_category = len(filtered_df)
            filtered_df = filtered_df[filtered_df['Seat Type'].str.contains(category, case=False, na=False)]
            print(f"After category filter ({category}): {len(filtered_df)} records (removed {before_category - len(filtered_df)})")
        
        gender = user_prefs.get('gender')
        if gender and 'Gender' in filtered_df.columns:
            before_gender = len(filtered_df)
            filtered_df = filtered_df[
                (filtered_df['Gender'].str.contains(gender, case=False, na=False)) |
                (filtered_df['Gender'].str.contains('Neutral', case=False, na=False))
            ]
            print(f"After gender filter ({gender}): {len(filtered_df)} records (removed {before_gender - len(filtered_df)})")
        
        print(f"Final filtered count: {len(filtered_df)}")
        print(f"=== END DEBUG ===\n")
        
        if len(filtered_df) == 0:
            return {
                'exam_type': exam_type,
                'total_options': 0,
                'showing': 0,
                'recommendations': [],
                'error': f'No colleges found! Try: 1) Different category, 2) Higher rank cutoff, 3) Check exam type'
            }
        
        filtered_df['NIRF_Rank'] = filtered_df['Institute'].apply(self.get_nirf_rank)
        filtered_df['Branch_Score'] = filtered_df['Academic Program Name'].apply(self.get_branch_score)
        
        # Calculate choice scores - iterate to avoid pandas issues
        choice_scores = []
        for idx, row in filtered_df.iterrows():
            score = self.calculate_choice_score(dict(row), user_prefs)
            choice_scores.append(score)
        
        filtered_df['Choice_Score'] = choice_scores
        
        filtered_df = filtered_df.sort_values('Choice_Score', ascending=False)
        max_choices = user_prefs.get('max_choices', 100)
        top_choices = filtered_df.head(max_choices)
        
        recommendations = []
        for idx, row in top_choices.iterrows():
            recommendations.append({
                'rank': len(recommendations) + 1,
                'institute': row.get('Institute', 'N/A'),
                'program': row.get('Academic Program Name', 'N/A'),
                'quota': row.get('Quota', 'N/A'),
                'seat_type': row.get('Seat Type', 'N/A'),
                'opening_rank': row.get('Opening Rank', 'N/A'),
                'closing_rank': row.get('Closing Rank', 'N/A'),
                'nirf_rank': int(row.get('NIRF_Rank', 999)),
                'choice_score': round(row.get('Choice_Score', 0), 2),
                'probability': self.get_probability(user_rank, row.get('Closing Rank', 999999))
            })
        
        return {
            'exam_type': exam_type,
            'total_options': len(filtered_df),
            'showing': len(recommendations),
            'recommendations': recommendations
        }
    
    def get_probability(self, user_rank, closing_rank):
        try:
            closing_rank = float(closing_rank)
            if closing_rank >= user_rank * 1.2:
                return "High"
            elif closing_rank >= user_rank:
                return "Moderate"
            else:
                return "Low"
        except:
            return "Unknown"

# Global assistant instance
assistant = ChoiceFillingAssistant()

# HTML template embedded in the code
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JoSAA Choice Filling Assistant</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .main-card {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            margin-bottom: 30px;
        }
        .form-section { margin-bottom: 30px; }
        .form-section h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        .form-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .form-group {
            display: flex;
            flex-direction: column;
        }
        .form-group label {
            font-weight: 600;
            margin-bottom: 8px;
            color: #333;
            font-size: 0.95em;
        }
        .form-group input, .form-group select {
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            transition: all 0.3s;
        }
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.1em;
            font-weight: 600;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        .btn-container {
            text-align: center;
            margin-top: 30px;
        }
        .results-section { display: none; }
        .results-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .results-header h2 { margin-bottom: 10px; }
        .results-stats {
            display: flex;
            gap: 30px;
            font-size: 1.1em;
        }
        .choice-card {
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            transition: all 0.3s;
            position: relative;
        }
        .choice-card:hover {
            border-color: #667eea;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
            transform: translateY(-2px);
        }
        .choice-rank {
            position: absolute;
            top: 15px;
            right: 20px;
            background: #667eea;
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.1em;
        }
        .choice-institute {
            font-size: 1.3em;
            font-weight: 700;
            color: #333;
            margin-bottom: 8px;
            padding-right: 60px;
        }
        .choice-program {
            font-size: 1.1em;
            color: #555;
            margin-bottom: 15px;
        }
        .choice-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #e0e0e0;
        }
        .detail-item {
            display: flex;
            flex-direction: column;
        }
        .detail-label {
            font-size: 0.85em;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }
        .detail-value {
            font-size: 1em;
            font-weight: 600;
            color: #333;
        }
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }
        .badge-high {
            background: #d4edda;
            color: #155724;
        }
        .badge-moderate {
            background: #fff3cd;
            color: #856404;
        }
        .badge-low {
            background: #f8d7da;
            color: #721c24;
        }
        .nirf-badge {
            background: #667eea;
            color: white;
        }
        .loading {
            text-align: center;
            padding: 40px;
            display: none;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .info-box {
            background: #e7f3ff;
            border-left: 4px solid #2196F3;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }
        .info-box h3 {
            color: #1976D2;
            margin-bottom: 10px;
        }
        .info-box ul {
            margin-left: 20px;
        }
        .info-box li {
            margin: 5px 0;
            color: #555;
        }
        @media (max-width: 768px) {
            .header h1 { font-size: 1.8em; }
            .main-card { padding: 20px; }
            .form-row { grid-template-columns: 1fr; }
            .results-stats { flex-direction: column; gap: 10px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 JoSAA Choice Filling Assistant</h1>
            <p>Smart recommendations based on NIRF rankings & your preferences</p>
        </div>

        <div class="main-card">
            <form id="preferencesForm">
                <div class="form-section">
                    <h2>📊 Your Details</h2>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="examType">Exam Type *</label>
                            <select id="examType" name="examType" required>
                                <option value="">Select Exam</option>
                                <option value="advanced">JEE Advanced (IITs only)</option>
                                <option value="mains">JEE Main (NITs/IIITs/GFTIs)</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="rank">Your Rank *</label>
                            <input type="number" id="rank" name="rank" required placeholder="e.g., 5000 for Advanced, 50000 for Mains" min="1">
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="category">Category *</label>
                            <select id="category" name="category" required>
                                <option value="">Select Category</option>
                                <option value="OPEN">General (OPEN)</option>
                                <option value="EWS">EWS</option>
                                <option value="OBC-NCL">OBC-NCL</option>
                                <option value="SC">SC</option>
                                <option value="ST">ST</option>
                            </select>
                        </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="gender">Gender *</label>
                            <select id="gender" name="gender" required>
                                <option value="">Select Gender</option>
                                <option value="Gender-Neutral">Gender-Neutral</option>
                                <option value="Female">Female-only</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="maxChoices">Number of Choices</label>
                            <input type="number" id="maxChoices" name="maxChoices" value="50" min="10" max="200">
                        </div>
                    </div>
                </div>

                <div class="info-box">
                    <h3>💡 Important - Two Different Exams:</h3>
                    <ul>
                        <li><strong>JEE Advanced:</strong> For IITs only (ranks typically 1-15,000)</li>
                        <li><strong>JEE Main:</strong> For NITs/IIITs/GFTIs (ranks can be 1-100,000+)</li>
                        <li><strong>Don't mix them!</strong> JEE Advanced rank ≠ JEE Main rank</li>
                        <li>Select your exam type to see relevant colleges only</li>
                    </ul>
                    <h3 style="margin-top: 15px;">📊 How recommendations work:</h3>
                    <ul>
                        <li><strong>NIRF Rankings:</strong> College quality indicator</li>
                        <li><strong>Branch Priority:</strong> CS/IT > ECE > EE > Mech</li>
                        <li><strong>Safety Margin:</strong> High/Moderate/Low probability</li>
                    </ul>
                </div>

                <div class="btn-container">
                    <button type="submit" class="btn">🔍 Find My Best Choices</button>
                </div>
            </form>
        </div>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Analyzing thousands of options...</p>
        </div>

        <div class="results-section" id="results">
            <div class="main-card">
                <div class="results-header">
                    <h2>🎯 Your Personalized Choices</h2>
                    <div class="results-stats">
                        <div>📊 Total Options: <strong id="totalOptions">0</strong></div>
                        <div>✅ Showing Top: <strong id="showingCount">0</strong></div>
                    </div>
                </div>
                <div id="choicesList"></div>
            </div>
        </div>
    </div>

    <script>
        const form = document.getElementById('preferencesForm');
        const loading = document.getElementById('loading');
        const results = document.getElementById('results');
        const choicesList = document.getElementById('choicesList');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            loading.style.display = 'block';
            results.style.display = 'none';

            const formData = {
                exam_type: document.getElementById('examType').value,
                rank: parseInt(document.getElementById('rank').value),
                category: document.getElementById('category').value,
                gender: document.getElementById('gender').value,
                max_choices: parseInt(document.getElementById('maxChoices').value)
            };

            try {
                const response = await fetch('/api/recommendations', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();
                if (data.error) {
                    alert('Error: ' + data.error);
                    loading.style.display = 'none';
                    return;
                }

                displayResults(data);
            } catch (error) {
                alert('Error: ' + error.message);
                loading.style.display = 'none';
            }
        });

        function displayResults(data) {
            document.getElementById('totalOptions').textContent = data.total_options;
            document.getElementById('showingCount').textContent = data.showing;

            choicesList.innerHTML = '';

            data.recommendations.forEach(choice => {
                const card = document.createElement('div');
                card.className = 'choice-card';
                
                const probabilityClass = choice.probability === 'High' ? 'badge-high' : 
                                        choice.probability === 'Moderate' ? 'badge-moderate' : 'badge-low';

                card.innerHTML = `
                    <div class="choice-rank">${choice.rank}</div>
                    <div class="choice-institute">${choice.institute}</div>
                    <div class="choice-program">${choice.program}</div>
                    
                    <div class="choice-details">
                        <div class="detail-item">
                            <span class="detail-label">NIRF Rank</span>
                            <span class="detail-value">
                                <span class="badge nirf-badge">#${choice.nirf_rank}</span>
                            </span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Opening Rank</span>
                            <span class="detail-value">${choice.opening_rank}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Closing Rank</span>
                            <span class="detail-value">${choice.closing_rank}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Probability</span>
                            <span class="detail-value">
                                <span class="badge ${probabilityClass}">${choice.probability}</span>
                            </span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Seat Type</span>
                            <span class="detail-value">${choice.seat_type}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Quota</span>
                            <span class="detail-value">${choice.quota}</span>
                        </div>
                    </div>
                `;

                choicesList.appendChild(card);
            });

            loading.style.display = 'none';
            results.style.display = 'block';
            results.scrollIntoView({ behavior: 'smooth' });
        }
    </script>
</body>
</html>"""

@app.route('/')
def index():
    """Serve the main page"""
    return HTML_TEMPLATE

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """API endpoint to get recommendations"""
    try:
        user_prefs = request.json
        results = assistant.get_recommendations(user_prefs)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Try to load data from default location
    default_data = Path('josaa_data_2024_round5.csv')
    if default_data.exists():
        assistant.load_data(default_data)
    
    print("\n" + "="*60)
    print("JoSAA Choice Filling Assistant - Single File Version")
    print("="*60)
    print("\n🚀 Server starting...")
    print("📍 Open: http://localhost:5000")
    print("\n💡 Place josaa_data_2024_round5.csv in the same folder")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000)
