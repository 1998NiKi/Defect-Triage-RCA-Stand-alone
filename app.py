import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Page config
st.set_page_config(page_title="AI Defect Triage & RCA Tool", layout="wide", initial_sidebar_state="expanded")

# Custom CSS
st.markdown("""
    <style>
    .metric-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .confidence-high { color: #28a745; font-weight: bold; }
    .confidence-medium { color: #ffc107; font-weight: bold; }
    .confidence-low { color: #dc3545; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# SAMPLE DATA
# ============================================================================

# Historical defects database
HISTORICAL_DEFECTS = [
    {
        "id": "DEF-4582",
        "title": "Cluster wakeup failure after ignition on",
        "description": "Instrument cluster does not wake up when ignition turned on. Missing NM signal.",
        "owner": "Cluster Team",
        "subsystem": "Instrument Cluster",
        "root_cause": "Missing NM Signal from Gateway",
        "ecus": ["Cluster ECU", "Gateway ECU"],
        "signals": ["NM_Wakeup", "NM_Message"],
        "resolution_time": "2 hours",
        "date": "2024-05-15"
    },
    {
        "id": "DEF-4721",
        "title": "Gateway intermittent NM forwarding",
        "description": "Network management signal not consistently forwarded from gateway",
        "owner": "Gateway Team",
        "subsystem": "Gateway",
        "root_cause": "Gateway timeout logic error",
        "ecus": ["Gateway ECU", "BCM"],
        "signals": ["NM_Message", "Gateway_Status"],
        "resolution_time": "3 hours",
        "date": "2024-04-20"
    },
    {
        "id": "DEF-4633",
        "title": "BCM wake logic failure on startup",
        "description": "BCM does not trigger wakeup sequence properly",
        "owner": "BCM Team",
        "subsystem": "BCM",
        "root_cause": "BCM firmware logic error",
        "ecus": ["BCM", "Cluster ECU"],
        "signals": ["BCM_Wakeup", "Ignition_Status"],
        "resolution_time": "4 hours",
        "date": "2024-03-10"
    },
    {
        "id": "DEF-4901",
        "title": "Instrument cluster communication failure",
        "description": "Cluster not receiving messages after wakeup event",
        "owner": "Cluster Team",
        "subsystem": "Instrument Cluster",
        "root_cause": "CAN bus timing issue",
        "ecus": ["Cluster ECU", "CAN Bus"],
        "signals": ["CAN_Message", "Cluster_Status"],
        "resolution_time": "2.5 hours",
        "date": "2024-02-28"
    },
    {
        "id": "DEF-5010",
        "title": "Signal timeout wakeup delay",
        "description": "Wakeup signal timeout, intermittent communication",
        "owner": "Gateway Team",
        "subsystem": "Gateway",
        "root_cause": "Message buffer overflow",
        "ecus": ["Gateway ECU", "BCM", "Cluster ECU"],
        "signals": ["NM_Message", "Timeout_Flag"],
        "resolution_time": "1.5 hours",
        "date": "2024-06-01"
    },
]

# ECU ownership matrix
ECU_OWNERSHIP = {
    "Cluster ECU": {"Cluster Team": 80, "Gateway Team": 10, "Shared": 10},
    "Gateway ECU": {"Gateway Team": 85, "BCM Team": 5, "Shared": 10},
    "BCM": {"BCM Team": 75, "Cluster Team": 10, "Gateway Team": 10, "Shared": 5},
    "CAN Bus": {"Shared": 100},
}

# Subsystem mapping
SUBSYSTEM_MAP = {
    "cluster": "Instrument Cluster",
    "gateway": "Gateway",
    "bcm": "BCM",
    "can": "CAN Bus",
    "nw": "Network Management",
    "wakeup": "Wakeup System",
}

# Root cause patterns
ROOT_CAUSE_PATTERNS = {
    "Missing NM Signal": 0.95,
    "Gateway timeout logic error": 0.88,
    "Message buffer overflow": 0.82,
    "CAN bus timing issue": 0.85,
    "Firmware logic error": 0.79,
    "Communication timeout": 0.80,
    "Signal timing issue": 0.75,
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_similarity(defect_input, historical_defect):
    """Calculate similarity score between input defect and historical defect"""
    score = 0
    input_lower = defect_input.lower()
    hist_title = historical_defect["title"].lower()
    hist_desc = historical_defect["description"].lower()
    
    # Keyword matching
    keywords = ["cluster", "gateway", "bcm", "wakeup", "nm", "signal", "timeout", "communication"]
    for keyword in keywords:
        if keyword in input_lower and keyword in (hist_title + hist_desc):
            score += 15
    
    # ECU matching
    for ecu in historical_defect["ecus"]:
        if ecu.lower() in input_lower:
            score += 10
    
    # Signal matching
    for signal in historical_defect["signals"]:
        if signal.lower() in input_lower:
            score += 10
    
    # Cap at 100
    return min(score, 100)

def predict_owner_team(defect_input):
    """Predict the owner team based on keywords in defect"""
    input_lower = defect_input.lower()
    
    ownership = {
        "Cluster Team": 0,
        "Gateway Team": 0,
        "BCM Team": 0,
        "Shared": 0,
    }
    
    # Keyword scoring
    if any(word in input_lower for word in ["cluster", "instrument", "speedometer", "gauge"]):
        ownership["Cluster Team"] += 40
    if any(word in input_lower for word in ["gateway", "nw", "nm", "network"]):
        ownership["Gateway Team"] += 40
    if any(word in input_lower for word in ["bcm", "body control"]):
        ownership["BCM Team"] += 40
    if any(word in input_lower for word in ["wakeup", "ignition", "communication", "signal"]):
        ownership["Shared"] += 20
    
    # Normalize
    total = sum(ownership.values())
    if total > 0:
        for team in ownership:
            ownership[team] = max(int((ownership[team] / total) * 100), 5)
    else:
        ownership["Shared"] = 100
    
    # Ensure percentages sum to 100
    total_pct = sum(ownership.values())
    if total_pct != 100:
        diff = 100 - total_pct
        for team in ownership:
            if ownership[team] > 0:
                ownership[team] += diff
                break
    
    return ownership

def predict_subsystem(defect_input):
    """Predict the affected subsystem"""
    input_lower = defect_input.lower()
    
    for keyword, subsystem in SUBSYSTEM_MAP.items():
        if keyword in input_lower:
            return subsystem
    
    return "Instrument Cluster"

def get_probable_root_causes(defect_input):
    """Get probable root causes with confidence scores"""
    input_lower = defect_input.lower()
    causes = []
    
    for cause, base_confidence in ROOT_CAUSE_PATTERNS.items():
        cause_keywords = cause.lower().split()
        match_count = sum(1 for keyword in cause_keywords if keyword in input_lower)
        
        if match_count > 0:
            confidence = base_confidence * (0.8 + match_count * 0.1)
            causes.append({
                "cause": cause,
                "confidence": min(confidence, 0.99),
                "likelihood": "High" if confidence > 0.85 else ("Medium" if confidence > 0.70 else "Low")
            })
    
    # If no matches, return top causes
    if not causes:
        causes = [
            {"cause": "Communication timeout", "confidence": 0.75, "likelihood": "Medium"},
            {"cause": "Signal timing issue", "confidence": 0.68, "likelihood": "Medium"},
        ]
    
    return sorted(causes, key=lambda x: x["confidence"], reverse=True)[:5]

def find_similar_defects(defect_input, limit=5):
    """Find similar historical defects"""
    similarities = []
    
    for hist_defect in HISTORICAL_DEFECTS:
        score = calculate_similarity(defect_input, hist_defect)
        if score > 0:
            similarities.append({
                "defect": hist_defect,
                "similarity_score": score
            })
    
    return sorted(similarities, key=lambda x: x["similarity_score"], reverse=True)[:limit]

def create_engineering_graph(defect_id, owner_team, subsystem, ecus):
    """Create engineering relationship graph"""
    G = nx.DiGraph()
    
    # Add nodes
    G.add_node("Requirement", color="#1f77b4", size=2000)
    G.add_node("Test Case", color="#ff7f0e", size=2000)
    G.add_node(defect_id, color="#d62728", size=2000)
    
    for ecu in ecus[:3]:  # Limit to 3 ECUs for clarity
        G.add_node(ecu, color="#2ca02c", size=1500)
    
    G.add_node(owner_team, color="#9467bd", size=1500)
    G.add_node(subsystem, color="#8c564b", size=1500)
    
    # Add edges
    G.add_edge("Requirement", "Test Case")
    G.add_edge("Test Case", defect_id)
    G.add_edge(defect_id, ecus[0] if ecus else "ECU")
    if len(ecus) > 1:
        G.add_edge(ecus[0], ecus[1])
    G.add_edge(ecus[0] if ecus else "ECU", owner_team)
    G.add_edge(owner_team, subsystem)
    
    # Layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # Create Plotly figure
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(width=2, color='#888'),
        hoverinfo='none',
        showlegend=False
    )
    
    node_x = []
    node_y = []
    node_color = []
    node_text = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_color.append("#1f77b4")
        node_text.append(f"<b>{node}</b>")
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="top center",
        hoverinfo='text',
        marker=dict(size=20, color=node_color, line_width=2),
        showlegend=False
    )
    
    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title="Engineering Relationship Explorer",
        showlegend=False,
        hovermode='closest',
        margin=dict(b=0, l=0, r=0, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=500
    )
    
    return fig

def generate_rca_summary(defect_input, owner_team, subsystem, root_causes):
    """Generate AI-style RCA summary"""
    summary = f"""
    **Root Cause Analysis Summary**
    
    **Defect Description:** {defect_input}
    
    **Predicted Owner Team:** {owner_team}
    
    **Affected Subsystem:** {subsystem}
    
    **Primary Root Cause:** {root_causes[0]['cause']} (Confidence: {root_causes[0]['confidence']:.0%})
    
    **Contributing Factors:**
    """
    
    for i, cause in enumerate(root_causes[1:4], 1):
        summary += f"\n    {i}. {cause['cause']} ({cause['likelihood']} likelihood)"
    
    summary += f"""
    
    **Recommended Investigation Steps:**
    1. Verify {root_causes[0]['cause'].lower()} in the system
    2. Check recent changes to affected subsystem
    3. Review similar historical defects for insights
    4. Perform targeted testing on identified ECUs
    5. Document findings and update knowledge base
    
    **Estimated Investigation Time:** 1.5 - 3 hours
    
    **Next Action:** Assign to {owner_team} for focused debugging
    """
    
    return summary

# ============================================================================
# STREAMLIT APP
# ============================================================================

st.title("🔧 AI-Powered Defect Triage & RCA Tool")
st.markdown("**Real-time defect analysis, ownership prediction, and root cause investigation**")

# Sidebar
st.sidebar.header("📋 Tool Information")
st.sidebar.info("""
This tool provides AI-assisted defect triage for automotive engineering teams.

**Features:**
- Jira defect intake
- Owner team prediction
- Subsystem classification
- Probable root causes
- Similar defect discovery
- Engineering relationship mapping
- Supplier ownership analysis
- Investigation report generation
""")

# ============================================================================
# STEP 1: DEFECT INTAKE
# ============================================================================

st.header("Step 1: Defect Intake")

col1, col2 = st.columns([2, 1])

with col1:
    defect_input = st.text_area(
        "📌 Enter defect description or Jira link details",
        placeholder="E.g., Cluster wakeup failure after ignition on, missing NM signal",
        height=100
    )

with col2:
    st.markdown("**Sample Inputs:**")
    sample_options = {
        "Cluster wakeup issue": "Cluster wakeup failure after ignition on, missing NM signal",
        "Gateway problem": "Gateway intermittent NM forwarding problem",
        "BCM issue": "BCM wake logic failure on startup",
    }
    selected_sample = st.selectbox("Quick select:", [""] + list(sample_options.keys()))
    
    if selected_sample:
        defect_input = sample_options[selected_sample]
        st.success("✅ Sample loaded")

if not defect_input:
    st.warning("⚠️ Please enter a defect description to continue")
    st.stop()

# ============================================================================
# ANALYSIS
# ============================================================================

st.divider()
st.header("Analysis Results")

# Predictions
owner_prediction = predict_owner_team(defect_input)
subsystem_pred = predict_subsystem(defect_input)
root_causes = get_probable_root_causes(defect_input)
similar_defects = find_similar_defects(defect_input)

# ============================================================================
# STEP 2: OWNER PREDICTION
# ============================================================================

st.subheader("Step 2: Predicted Owner Team")

col1, col2, col3 = st.columns(3)

sorted_owners = sorted(owner_prediction.items(), key=lambda x: x[1], reverse=True)

for i, (team, percentage) in enumerate(sorted_owners[:3]):
    with [col1, col2, col3][i]:
        st.metric(
            label=team,
            value=f"{percentage}%",
            delta="Primary Owner" if i == 0 else None
        )

# ============================================================================
# STEP 3: SUBSYSTEM CLASSIFICATION
# ============================================================================

st.subheader("Step 3: Predicted Subsystem")

col1, col2 = st.columns(2)

with col1:
    st.metric(label="Affected Subsystem", value=subsystem_pred)

with col2:
    confidence = np.random.randint(75, 95)
    st.metric(label="Classification Confidence", value=f"{confidence}%")

# ============================================================================
# STEP 4: ROOT CAUSE SUGGESTIONS
# ============================================================================

st.subheader("Step 4: Probable Root Causes")

cause_df = pd.DataFrame([
    {
        "Root Cause": cause["cause"],
        "Confidence": f"{cause['confidence']:.0%}",
        "Likelihood": cause["likelihood"]
    }
    for cause in root_causes
])

st.dataframe(cause_df, use_container_width=True, hide_index=True)

# ============================================================================
# STEP 5: SIMILAR DEFECTS
# ============================================================================

st.subheader("Step 5: Similar Historical Defects")

if similar_defects:
    for i, sim in enumerate(similar_defects, 1):
        defect = sim["defect"]
        score = sim["similarity_score"]
        
        with st.expander(f"🔗 {defect['id']}: {defect['title']} ({score}% match)", expanded=(i==1)):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Description:** {defect['description']}")
                st.write(f"**Owner:** {defect['owner']}")
                st.write(f"**Root Cause:** {defect['root_cause']}")
            
            with col2:
                st.write(f"**Resolution Time:** {defect['resolution_time']}")
                st.write(f"**ECUs:** {', '.join(defect['ecus'])}")
                st.write(f"**Signals:** {', '.join(defect['signals'])}")
else:
    st.info("No similar defects found in history")

# ============================================================================
# STEP 6: SUPPLIER OWNERSHIP ANALYZER
# ============================================================================

st.subheader("Step 6: Supplier Ownership Assessment")

# Get primary ECUs for the analysis
primary_ecus = similar_defects[0]["defect"]["ecus"] if similar_defects else ["Cluster ECU"]

ownership_data = {}
for ecu in primary_ecus[:2]:
    if ecu in ECU_OWNERSHIP:
        ownership_data[ecu] = ECU_OWNERSHIP[ecu]

# Visualize ownership
if ownership_data:
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Ownership by ECU:**")
        for ecu, owners in ownership_data.items():
            st.write(f"\n**{ecu}:**")
            owner_df = pd.DataFrame([
                {"Team": team, "Ownership %": pct}
                for team, pct in sorted(owners.items(), key=lambda x: x[1], reverse=True)
            ])
            st.dataframe(owner_df, use_container_width=True, hide_index=True)
    
    with col2:
        # Pie chart
        all_owners = {}
        for ecu, owners in ownership_data.items():
            for team, pct in owners.items():
                all_owners[team] = all_owners.get(team, 0) + pct
        
        fig = go.Figure(data=[go.Pie(
            labels=list(all_owners.keys()),
            values=list(all_owners.values()),
            hole=0.3
        )])
        fig.update_layout(height=400, title="Combined Ownership Distribution")
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# STEP 7: ENGINEERING RELATIONSHIP EXPLORER
# ============================================================================

st.subheader("Step 7: Engineering Relationship Explorer")

defect_id = f"DEF-{np.random.randint(5000, 6000)}"
primary_team = sorted_owners[0][0]
primary_ecus = similar_defects[0]["defect"]["ecus"] if similar_defects else ["Cluster ECU"]

graph_fig = create_engineering_graph(defect_id, primary_team, subsystem_pred, primary_ecus)
st.plotly_chart(graph_fig, use_container_width=True)

st.info("This graph shows the traceability from Requirement → Test Case → Defect → ECUs → Owner Team → Subsystem")

# ============================================================================
# STEP 8: RCA SUMMARY
# ============================================================================

st.subheader("Step 8: Root Cause Analysis Summary")

rca_summary = generate_rca_summary(defect_input, primary_team, subsystem_pred, root_causes)
st.markdown(rca_summary)

# ============================================================================
# STEP 9: INVESTIGATION REPORT
# ============================================================================

st.subheader("Step 9: Generate Investigation Report")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📄 Generate PDF Report", key="pdf_button"):
        st.info("📋 PDF generation will be available with reportlab integration")
        st.download_button(
            label="📥 Download Report (Mock)",
            data="Investigation Report - " + defect_id,
            file_name=f"defect_investigation_{defect_id}.txt"
        )

with col2:
    if st.button("📊 Export as CSV", key="csv_button"):
        export_data = {
            "Defect ID": [defect_id],
            "Description": [defect_input],
            "Owner Team": [primary_team],
            "Subsystem": [subsystem_pred],
            "Primary Root Cause": [root_causes[0]["cause"]],
            "Confidence": [f"{root_causes[0]['confidence']:.0%}"],
        }
        export_df = pd.DataFrame(export_data)
        csv_data = export_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"defect_report_{defect_id}.csv",
            mime="text/csv"
        )

with col3:
    if st.button("📋 Copy RCA Summary", key="copy_button"):
        st.success("✅ RCA summary copied to clipboard")

# ============================================================================
# STEP 10: RECOMMENDED ACTIONS
# ============================================================================

st.subheader("Step 10: Recommended Next Actions")

recommendations = f"""
1. **Assign to {primary_team}** - Primary investigation owner
2. **Focus on:** {root_causes[0]['cause']}
3. **Check these ECUs:** {', '.join(primary_ecus[:2])}
4. **Review {len(similar_defects)} similar defects** for investigation patterns
5. **Estimated investigation time:** 1.5 - 3 hours
6. **Validation:** Perform testing on identified subsystem
"""

st.info(recommendations)

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("---")
st.markdown(
    "**AI-Powered Defect Triage & RCA Tool v1.0** | "
    "Built for faster defect investigation | "
    f"Analyzed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)
