st.markdown("""
<style>
  :root {
    --bg: #0a0e1a;
    --surface: #111827;
    --border: #1e2d45;
    --accent: #00d4ff;
    --accent2: #7c3aed;
    --green: #00e676;
    --red: #ff1744;
    --yellow: #ffb300;
    --text: #e2e8f0;
    --muted: #94a3b8;
  }

  .stApp {
    background-color: var(--bg);
    color: var(--text);
  }

  section[data-testid="stSidebar"] {
    background-color: var(--surface);
    border-right: 1px solid var(--border);
  }

  section[data-testid="stSidebar"] label,
  section[data-testid="stSidebar"] p,
  section[data-testid="stSidebar"] span,
  section[data-testid="stSidebar"] div,
  section[data-testid="stSidebar"] h1,
  section[data-testid="stSidebar"] h2,
  section[data-testid="stSidebar"] h3 {
    color: var(--text) !important;
  }

  .stMarkdown,
  .stMarkdown p,
  .stMarkdown span,
  .stMarkdown li,
  .stText,
  .stCaption,
  .stAlert,
  .stInfo,
  .stWarning,
  .stSuccess,
  .stError,
  h1, h2, h3, h4, h5, h6,
  p, li, label {
    color: var(--text) !important;
  }

  [data-testid="metric-container"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px 16px;
  }

  [data-testid="metric-container"] label {
    color: var(--muted) !important;
    font-size: 11px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  [data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--text) !important;
    font-size: 22px !important;
    font-weight: 700;
  }

  .stTabs [data-baseweb="tab"] {
    color: var(--muted) !important;
    font-weight: 600;
    letter-spacing: 0.05em;
  }

  .stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
  }

  .stButton > button {
    background: linear-gradient(135deg, #00d4ff18, #7c3aed18);
    border: 1px solid var(--accent);
    color: var(--accent);
    font-weight: 600;
    letter-spacing: 0.05em;
    border-radius: 6px;
    transition: all 0.2s;
  }

  .stButton > button:hover {
    background: var(--accent);
    color: #000 !important;
  }

  .stTextInput input,
  .stNumberInput input,
  textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 6px !important;
  }

  div[data-baseweb="select"] > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
  }

  [data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 8px;
  }
</style>
""", unsafe_allow_html=True)
