import streamlit as st
import pandas as pd
from ml.api.main import load_models, get_recommendation
from ml.api.schemas import MatchRequest, MaterialRecord

# Initialize backend AI models purely in memory! No FastAPI needed for cloud deployment.
@st.cache_resource(show_spinner="Loading MatrixCode AI Models into Memory...")
def init_system():
    load_models()
    return True

init_system()

st.set_page_config(page_title="MatrixCode AI", layout="wide", page_icon="⚡")

# Custom CSS for glassmorphism, nice typography, and vibrant accents
st.markdown("""
<style>
    /* Premium dark mode styling */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Sleek card containers */
    .metric-card {
        background: rgba(33, 38, 45, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    
    /* Vibrant highlight text */
    .highlight-blue {
        color: #58a6ff;
        font-weight: 600;
    }
    .highlight-green {
        color: #3fb950;
        font-weight: 600;
    }
    .highlight-red {
        color: #f85149;
        font-weight: 600;
    }
    
    /* Attribute comparison chips */
    .attr-chip {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 16px;
        font-size: 0.85em;
        font-weight: bold;
        margin: 2px;
    }
    .chip-match { background-color: rgba(63, 185, 80, 0.2); color: #3fb950; border: 1px solid #3fb950; }
    .chip-conflict { background-color: rgba(248, 81, 73, 0.2); color: #f85149; border: 1px solid #f85149; }
    .chip-missing { background-color: rgba(210, 168, 255, 0.2); color: #d2a8ff; border: 1px solid #d2a8ff; }
</style>
""", unsafe_allow_html=True)

st.title("⚡ MatrixCode AI Harmonization")
st.markdown("Automated, AI-driven material master deduplication and harmonization.")

st.markdown('<div class="metric-card">', unsafe_allow_html=True)
st.header("🎯 Input Material")
st.markdown("Enter the raw CPSE material record:")

with st.form("input_form"):
    col1, col2 = st.columns(2)
    with col1:
        cpse_id = st.text_input("CPSE ID", "TEST-CPSE-1")
        material_description = st.text_area("Material Description", "GATE VALVE 4 INCH 150# RF FLANGED CS ASTM A216 WCB", height=100)
        material_group_code = st.text_input("Material Group (Optional)", "VALVES")
    with col2:
        material_code = st.text_input("Material Code", "TEST-MAT-001")
        material_long_text = st.text_area("Long Text (Optional)", "", height=100)
        manufacturer = st.text_input("Manufacturer (Optional)", "")
        
    submit = st.form_submit_button("🚀 Harmonize Material", use_container_width=True, type="primary")

st.markdown('</div>', unsafe_allow_html=True)

if submit:
    with st.spinner("Processing through MatrixCode Engine..."):
        payload = {
            "source_record": {
                "cpse_id": cpse_id,
                "material_code": material_code,
                "material_description": material_description,
                "material_long_text": material_long_text,
                "material_group_code": material_group_code,
                "uom": "EA",
                "manufacturer": manufacturer
            },
            "top_k": 5
        }
        
        try:
            req = MatchRequest(
                source_record=MaterialRecord(**payload["source_record"]),
                top_k=payload["top_k"]
            )
            # Call python logic directly instead of over HTTP
            # This enables pure serverless deployment on Streamlit Cloud!
            result = get_recommendation(req)
            
            if isinstance(result, dict):
                pass
            else:
                # If it's a Pydantic model
                result = result.dict()
            
            # Layout Setup
            st.markdown("---")
            
            # --- TOP SECTION: DECISION ---
            classification = result.get("classification")
            conf = result.get("confidence", 0) * 100
            
            # Header card
            if classification == "IDENTICAL":
                color_class = "highlight-green"
                icon = "✅"
            elif classification == "NEAR_DUPLICATE":
                color_class = "highlight-blue"
                icon = "🔍"
            elif classification == "DISTINCT":
                color_class = "highlight-red"
                icon = "🛑"
            elif classification == "FUNCTIONALLY_EQUIVALENT":
                color_class = "highlight-blue"
                icon = "🔄"
            else:
                color_class = ""
                icon = "ℹ️"
                
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <h2>{icon} Recommendation: <span class="{color_class}">{classification}</span></h2>
                <h4 style="color: #8b949e;">Confidence: {conf:.1f}%</h4>
                <p style="font-size: 1.1em; margin-top: 10px;">{result.get('reason')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # --- MIDDLE SECTION: SOURCE vs BEST CANDIDATE ---
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.subheader("📦 Source Profile")
                st.write(f"**Family:** `{result.get('source_material', {}).get('family')}`")
                st.write(f"**Normalized:** *{result.get('source_material', {}).get('normalized_description')}*")
                
                attrs = result.get("source_material", {}).get("attributes", {})
                if attrs:
                    df_attrs = pd.DataFrame([{"Attribute": k, "Value": v.get("normalized"), "Raw": v.get("raw")} for k, v in attrs.items()])
                    st.dataframe(df_attrs, hide_index=True, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.subheader("🎯 Best Candidate Registry Match")
                candidates = result.get("candidates", [])
                if candidates:
                    top_c = candidates[0]
                    st.write(f"**Material Code:** `{top_c.get('material_code')}`")
                    st.write(f"**Similarity Score:** `{top_c.get('score', 0):.4f}`")
                    
                    # Display evidence attribute states
                    evidence = result.get("evidence", {})
                    states = evidence.get("attribute_states", [])
                    if states:
                        st.write("**Attribute Comparison:**")
                        html_chips = ""
                        for s in states:
                            state = s.get("state")
                            attr = s.get("attribute")
                            if state == "MATCH":
                                html_chips += f'<span class="attr-chip chip-match">✓ {attr}</span> '
                            elif state == "CONFLICT":
                                html_chips += f'<span class="attr-chip chip-conflict">✗ {attr}</span> '
                            else:
                                html_chips += f'<span class="attr-chip chip-missing">? {attr}</span> '
                        st.markdown(html_chips, unsafe_allow_html=True)
                    
                    if evidence.get("engineering_conflict_status"):
                        st.error("Hard Engineering Conflict Detected!")
                else:
                    st.info("No candidates retrieved.")
                st.markdown('</div>', unsafe_allow_html=True)
                
            # --- BOTTOM SECTION: DETAILS & OTHER CANDIDATES ---
            tab1, tab2 = st.tabs(["Top Candidates", "Detailed Evidence Trace"])
            
            with tab1:
                if len(candidates) > 0:
                    df_cands = pd.DataFrame(candidates)
                    st.dataframe(df_cands, use_container_width=True)
                else:
                    st.write("No candidates.")
                    
            with tab2:
                st.json(result.get("evidence", {}))
            
        except Exception as e:
            st.error(f"⚠️ An error occurred during harmonization: {str(e)}")
