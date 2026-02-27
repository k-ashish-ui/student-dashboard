"""
JoSAA Choice Filling Assistant - Streamlit Version
Easy deployment on Streamlit Cloud (free!)
"""

import streamlit as st
import pandas as pd
from pathlib import Path

# Page config
st.set_page_config(
    page_title="JoSAA Choice Filling Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: transparent;
    }
    .css-1d391kg {
        background: white;
        border-radius: 20px;
        padding: 2rem;
    }
    h1 {
        color: #667eea;
        text-align: center;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        font-weight: 600;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        border: none;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    .recommendation-card {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s;
    }
    .recommendation-card:hover {
        border-color: #667eea;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
    }
    .badge-high {
        background: #d4edda;
        color: #155724;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .badge-moderate {
        background: #fff3cd;
        color: #856404;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .badge-low {
        background: #f8d7da;
        color: #721c24;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .nirf-badge {
        background: #667eea;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# NIRF Rankings
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

# Branch Scores
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
            st.success(f"✓ Loaded {len(self.df)} records from JoSAA data")
            
            # Show column names for debugging
            st.info(f"📋 Data columns: {', '.join(self.df.columns.tolist())}")
            
            # Show sample institute names (IMPORTANT for debugging)
            if 'Institute' in self.df.columns:
                unique_institutes = self.df['Institute'].unique()[:10]
                st.write("📍 Sample Institute Names (first 10):")
                for inst in unique_institutes:
                    st.write(f"  • {inst}")
            
            # Show a sample row
            if len(self.df) > 0:
                with st.expander("Show sample data (first row)"):
                    st.write(self.df.head(1))
                
        except Exception as e:
            st.error(f"Error loading data: {e}")
            self.df = None
    
    def normalize_institute_name(self, name):
        """Normalize institute names - DO NOT convert, keep as is"""
        if not isinstance(name, str):
            return name
        # Just return the name as-is, don't convert
        return name.strip()
    
    def get_nirf_rank(self, institute_name):
        """Get NIRF ranking for an institute - handles both full names and abbreviations"""
        if not isinstance(institute_name, str):
            return 999
        
        institute_lower = institute_name.lower().strip()
        
        # First try exact match
        for nirf_name, rank in NIRF_RANKINGS.items():
            if nirf_name.lower() == institute_lower:
                return rank
        
        # Try partial match (contains)
        for nirf_name, rank in NIRF_RANKINGS.items():
            if nirf_name.lower() in institute_lower or institute_lower in nirf_name.lower():
                return rank
        
        # Try matching with common abbreviations
        # e.g., "IIT Madras" should match "Indian Institute of Technology Madras"
        if 'iit' in institute_lower:
            # Extract location (e.g., "madras", "delhi", "bombay")
            for nirf_name, rank in NIRF_RANKINGS.items():
                if 'indian institute of technology' in nirf_name.lower():
                    # Get the location part from NIRF name (last word usually)
                    nirf_location = nirf_name.lower().split()[-1]
                    if nirf_location in institute_lower:
                        return rank
        
        if 'nit' in institute_lower:
            # Extract location for NITs
            for nirf_name, rank in NIRF_RANKINGS.items():
                if 'national institute of technology' in nirf_name.lower():
                    nirf_location = nirf_name.lower().split()[-1]
                    if nirf_location in institute_lower:
                        return rank
        
        return 999  # Not found in NIRF top 30
    
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
        # Always return a dict with expected keys
        default_response = {
            'total_options': 0,
            'showing': 0,
            'recommendations': [],
            'error': None
        }
        
        if self.df is None:
            default_response['error'] = 'No data loaded. Please upload josaa_data_2024_round5.csv to your repository.'
            return default_response
        
        try:
            filtered_df = self.df.copy()
            user_rank = user_prefs.get('rank', 0)
            exam_type = user_prefs.get('exam_type', 'advanced')
            
            # Filter by exam type
            # Check for both full name and abbreviation
            if exam_type == 'advanced':
                # JEE Advanced - Show only IITs
                mask = (
                    filtered_df['Institute'].str.contains('Indian Institute of Technology', case=False, na=False) |
                    filtered_df['Institute'].str.contains(r'\bIIT\b', case=False, na=False, regex=True)
                )
                filtered_df = filtered_df[mask]
            else:
                # JEE Main - Show NITs, IIITs, GFTIs (exclude IITs)
                mask = (
                    ~filtered_df['Institute'].str.contains('Indian Institute of Technology', case=False, na=False) &
                    ~filtered_df['Institute'].str.contains(r'\bIIT\b', case=False, na=False, regex=True)
                )
                filtered_df = filtered_df[mask]
            
            if len(filtered_df) == 0:
                default_response['error'] = f'No colleges found for {exam_type} exam type. Check your data has the right institute names.'
                return default_response
            
            if 'Closing Rank' in filtered_df.columns:
                filtered_df['Closing Rank'] = pd.to_numeric(filtered_df['Closing Rank'], errors='coerce')
                filtered_df = filtered_df[filtered_df['Closing Rank'] >= user_rank * 0.8]
            
            if len(filtered_df) == 0:
                default_response['error'] = f'No colleges found within your rank range. Your rank {user_rank} is too high for available options.'
                return default_response
            
            category = user_prefs.get('category')
            if category and 'Seat Type' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Seat Type'].str.contains(category, case=False, na=False)]
            
            if len(filtered_df) == 0:
                default_response['error'] = f'No seats found for {category} category. Try a different category or increase rank range.'
                return default_response
            
            gender = user_prefs.get('gender')
            if gender and 'Gender' in filtered_df.columns:
                filtered_df = filtered_df[
                    (filtered_df['Gender'].str.contains(gender, case=False, na=False)) |
                    (filtered_df['Gender'].str.contains('Neutral', case=False, na=False))
                ]
            
            if len(filtered_df) == 0:
                default_response['error'] = f'No seats found for {gender}. All filtered out.'
                return default_response
            
            filtered_df['NIRF_Rank'] = filtered_df['Institute'].apply(self.get_nirf_rank)
            filtered_df['Branch_Score'] = filtered_df['Academic Program Name'].apply(self.get_branch_score)
            
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
                'total_options': len(filtered_df),
                'showing': len(recommendations),
                'recommendations': recommendations,
                'error': None
            }
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            st.error(f"Detailed error: {error_details}")
            default_response['error'] = f'Error processing recommendations: {str(e)}'
            return default_response
    
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

# Initialize session state
if 'assistant' not in st.session_state:
    # Check if data file exists
    data_file = 'josaa_data_2024_round5.csv'
    
    if Path(data_file).exists():
        try:
            st.session_state.assistant = ChoiceFillingAssistant(data_file)
        except Exception as e:
            st.error(f"Error loading data: {e}")
            st.session_state.assistant = ChoiceFillingAssistant()
    else:
        st.warning(f"""
        ⚠️ **Data file not found: {data_file}**
        
        Please upload `josaa_data_2024_round5.csv` to your repository.
        
        The app will work but recommendations won't be available.
        """)
        st.session_state.assistant = ChoiceFillingAssistant()

# Header
st.title("🎓 JoSAA Choice Filling Assistant")
st.markdown("### Smart recommendations based on NIRF rankings & your preferences")

# Sidebar for user inputs
with st.sidebar:
    st.header("📊 Your Details")
    
    exam_type = st.selectbox(
        "Exam Type *",
        ["", "JEE Advanced (IITs only)", "JEE Main (NITs/IIITs/GFTIs)"],
        help="JEE Advanced for IITs, JEE Main for NITs/IIITs"
    )
    
    rank = st.number_input(
        "Your Rank *",
        min_value=1,
        max_value=1000000,
        value=5000,
        help="Your JEE Advanced or JEE Main rank"
    )
    
    category = st.selectbox(
        "Category *",
        ["", "OPEN", "EWS", "OBC-NCL", "SC", "ST"]
    )
    
    gender = st.selectbox(
        "Gender *",
        ["", "Gender-Neutral", "Female"]
    )
    
    max_choices = st.slider(
        "Number of Choices",
        min_value=10,
        max_value=200,
        value=50,
        step=10
    )
    
    st.markdown("---")
    
    st.markdown("""
    ### 💡 How it works:
    
    **NIRF Rankings:** Colleges ranked by quality
    
    **Branch Priority:** CS/IT > ECE > EE > Mech
    
    **Safety Margin:** High/Moderate/Low probability
    
    **Important:** JEE Advanced ≠ JEE Main!
    """)
    
    submit_button = st.button("🔍 Find My Best Choices", use_container_width=True)

# Main content
if submit_button:
    if not exam_type or not category or not gender:
        st.error("⚠️ Please fill all required fields (marked with *)")
    else:
        # Prepare user preferences
        exam_type_key = 'advanced' if 'Advanced' in exam_type else 'mains'
        
        user_prefs = {
            'exam_type': exam_type_key,
            'rank': rank,
            'category': category,
            'gender': gender,
            'max_choices': max_choices
        }
        
        # Get recommendations
        with st.spinner('🔄 Analyzing thousands of options...'):
            results = st.session_state.assistant.get_recommendations(user_prefs)
        
        # Check if there's an error
        if results.get('error') is not None and results.get('error') != 'None':
            st.error(f"""
            ⚠️ **Error:** {results['error']}
            
            Please check:
            1. Data file is loaded correctly
            2. All fields are filled properly
            3. Try different search criteria
            """)
        elif results.get('total_options', 0) == 0 or len(results.get('recommendations', [])) == 0:
            st.warning("""
            ⚠️ **No colleges found!**
            
            Try:
            1. Different category
            2. Higher max choices  
            3. Check exam type (JEE Advanced vs Main)
            4. Increase your rank range
            """)
        else:
            # Results header
            st.success(f"✅ Found {results['total_options']} options! Showing top {results['showing']}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Options", results['total_options'])
            with col2:
                st.metric("Showing Top", results['showing'])
            
            st.markdown("---")
            
            # Display recommendations
            for rec in results['recommendations']:
                # Probability badge
                prob = rec['probability']
                if prob == "High":
                    prob_badge = '<span class="badge-high">✅ High</span>'
                elif prob == "Moderate":
                    prob_badge = '<span class="badge-moderate">🟡 Moderate</span>'
                else:
                    prob_badge = '<span class="badge-low">🔴 Low</span>'
                
                nirf_badge = f'<span class="nirf-badge">NIRF #{rec["nirf_rank"]}</span>'
                
                # Create columns for better layout
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="recommendation-card">
                        <h3>#{rec['rank']} - {rec['institute']}</h3>
                        <h4 style="color: #666;">{rec['program']}</h4>
                        <p><strong>Opening Rank:</strong> {rec['opening_rank']} | <strong>Closing Rank:</strong> {rec['closing_rank']}</p>
                        <p><strong>Seat Type:</strong> {rec['seat_type']} | <strong>Quota:</strong> {rec['quota']}</p>
                        <p>{nirf_badge} {prob_badge} <strong>Score:</strong> {rec['choice_score']}/100</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")

else:
    # Welcome screen
    st.info("""
    ### 👋 Welcome!
    
    This tool helps you choose the best colleges based on:
    - **Your rank** and category
    - **NIRF rankings** (college quality)
    - **Branch preferences** (CS > ECE > EE...)
    - **Admission probability**
    
    **Fill the form on the left and click "Find My Best Choices"!**
    """)
    
    # Example results preview
    st.markdown("### 📊 Example Results Preview:")
    
    st.markdown("""
    <div class="recommendation-card">
        <h3>#1 - Indian Institute of Technology Madras</h3>
        <h4 style="color: #666;">Computer Science and Engineering</h4>
        <p><strong>Opening Rank:</strong> 1 | <strong>Closing Rank:</strong> 66</p>
        <p><strong>Seat Type:</strong> OPEN | <strong>Quota:</strong> AI</p>
        <p><span class="nirf-badge">NIRF #1</span> <span class="badge-high">✅ High</span> <strong>Score:</strong> 98.5/100</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Built with ❤️ for JEE aspirants | Data: JoSAA 2024 Round 5</p>
    <p>Made using Streamlit • NIRF Rankings 2024</p>
</div>
""", unsafe_allow_html=True)
