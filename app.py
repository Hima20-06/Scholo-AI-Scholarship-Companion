import os
import base64
from pathlib import Path

import requests
import streamlit as st

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Scholo | AI Scholarship Companion",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = os.getenv("SCHOLO_API_URL", "http://127.0.0.1:8000").rstrip("/")
MASCOT_PATH = Path(__file__).parent / "assets" / "scholo_mascot.png"

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
defaults = {
    "messages": [],
    "selected_action": None,
    "student_profile": {},
    "active_page": "Home",
    "navigation": "Home",
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def mascot_data_uri():
    if not MASCOT_PATH.exists():
        return ""
    encoded = base64.b64encode(MASCOT_PATH.read_bytes()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def search_scholarships(query):
    """Send the search query and saved student profile to the existing API."""
    profile = st.session_state.get("student_profile", {})
    payload = {
        "query": query,
        "state": profile.get("state"),
        "education_level": profile.get("education_level"),
        "course": profile.get("course"),
        "annual_income_inr": profile.get("annual_income_inr"),
        "tenth_percentage": profile.get("tenth_percentage"),
        "twelfth_percentage": profile.get("twelfth_percentage"),
        "cgpa": profile.get("cgpa"),
        "cgpa_scale": profile.get("cgpa_scale"),
        "academic_year": profile.get("academic_year"),
    }

    try:
        response = requests.post(
            f"{API_URL}/search-scholarships",
            json=payload,
            timeout=45,
        )
        if response.status_code != 200:
            try:
                detail = response.json().get("detail", "Unknown API error")
            except ValueError:
                detail = "The API returned an unexpected response."
            return {"error": f"Search failed (HTTP {response.status_code}): {detail}"}
        try:
            return response.json()
        except ValueError:
            return {"error": "The API returned invalid JSON."}
    except requests.exceptions.ConnectionError:
        return {
            "error": "I can't reach the scholarship service. Start the FastAPI server in another terminal."
        }
    except requests.exceptions.Timeout:
        return {"error": "The search took too long. Please try again."}
    except requests.exceptions.RequestException as exc:
        return {"error": f"A network error occurred: {exc}"}


def display_results(data):
    if data.get("error"):
        st.error(data["error"])
        return

    results = data.get("results", [])
    if not results:
        st.info("No results were returned. Try a broader search.")
        return

    st.success(f"Found {len(results)} web search result(s).")
    for index, item in enumerate(results, start=1):
        title = item.get("title") or f"Search result {index}"
        url = item.get("url", "")
        snippet = item.get("snippet", "")
        with st.container(border=True):
            st.markdown(f"#### {index:02d}  {title}")
            if snippet:
                st.write(snippet)
            if url.startswith(("https://", "http://")):
                st.link_button("Open source website ↗", url)
            st.caption("Source status: Not independently verified.")
            st.warning(
                "This is a potential lead, not a confirmed scholarship or eligibility decision. "
                "Check the official scheme guidelines and current deadline."
            )

def run_search(query):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.spinner("Scholo is searching for useful scholarship information..."):
        result = search_scholarships(query)

    if result.get("error"):
        answer = result["error"]
        st.session_state.messages.append({"role": "assistant", "content": answer})
    else:
        answer = (
            f"I searched for **{query}**. Here are the results I found. "
            "Please verify eligibility and deadlines with the official provider."
        )
        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "results": result}
        )
    return result
def open_scholo_chat():
    st.session_state.navigation = "AI Chat"
def navigate_to(page):
    st.session_state.navigation = page


def open_chat_with_home_query():
    query = st.session_state.get("home_search", "").strip()

    if query:
        st.session_state.pending_query = query
        st.session_state.navigation = "AI Chat"
# --------------------------------------------------
# THEME / UI
# --------------------------------------------------
st.markdown(
    """
    <style>
    :root {
        --bg: #080B1B;
        --panel: rgba(19, 24, 54, .82);
        --panel2: rgba(25, 31, 72, .78);
        --line: rgba(139, 124, 255, .28);
        --text: #F4F2FF;
        --muted: #A9ADD0;
        --purple: #9675FF;
        --cyan: #66D9FF;
    }
    .stApp {
        background:
          radial-gradient(circle at 78% 7%, rgba(100, 72, 210, .18), transparent 27%),
          radial-gradient(circle at 8% 80%, rgba(53, 100, 210, .12), transparent 28%),
          #080B1B;
        color: var(--text);
    }
    [data-testid="stHeader"] { background: rgba(8,11,27,.72); }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111632 0%, #0B1025 100%);
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] > div { padding-top: 1.2rem; }
    h1, h2, h3, h4, p, label, span { color: var(--text); }
    .brand {
        font-size: 1.9rem; font-weight: 850; letter-spacing: -.7px;
        color: #E8E2FF; margin: 0;
    }
    .brand-sub { color: #A9ADD0; font-size: .78rem; margin-top: -5px; }
    .eyebrow {
        color: #A995FF; text-transform: uppercase; letter-spacing: 2px;
        font-size: .72rem; font-weight: 800;
    }
    .hero {
        border: 1px solid var(--line); border-radius: 24px;
        padding: 30px 32px; margin: 8px 0 22px;
        background: linear-gradient(115deg, rgba(33,31,83,.92), rgba(16,28,58,.88));
        box-shadow: 0 18px 55px rgba(0,0,0,.22);
    }
    .hero h1 { font-size: clamp(2rem, 4vw, 3.2rem); line-height: 1.08; margin: 8px 0; }
    .hero p { color: #C5C8E7; max-width: 650px; margin-bottom: 0; }
    .section-heading { font-size: 1.35rem; font-weight: 800; margin: 20px 0 12px; }
    .mini-card {
        border: 1px solid var(--line); border-radius: 18px; padding: 18px;
        background: linear-gradient(145deg, rgba(34,39,88,.78), rgba(15,22,48,.86));
        min-height: 142px;
    }
    .mini-card .icon { font-size: 1.45rem; }
    .mini-card h3 { font-size: 1.02rem; margin: 8px 0 5px; }
    .mini-card p { color: #B7BAD8; font-size: .86rem; margin: 0; }
    .soft-note {
        color: #B8BCE0; background: rgba(25,31,72,.65);
        border: 1px solid var(--line); border-radius: 14px;
        padding: 12px 15px; font-size: .88rem;
    }
    div.stButton > button, div.stFormSubmitButton > button, div.stLinkButton > a {
        border-radius: 13px; border: 1px solid rgba(164,143,255,.52);
        background: linear-gradient(100deg, #7655E9, #5B6BEA);
        color: white; font-weight: 700; min-height: 2.7rem;
        transition: .2s ease;
    }
    div.stButton > button:hover, div.stFormSubmitButton > button:hover {
        border-color: #B8A7FF; box-shadow: 0 0 20px rgba(133,105,255,.28);
        transform: translateY(-1px);
    }
    div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-testid="stChatInput"] textarea {
        background: #111936; color: #F4F2FF; border-color: #414879;
        border-radius: 12px;
    }
    [data-testid="stExpander"] {
        border: 1px solid var(--line); border-radius: 15px; background: rgba(17,23,51,.55);
    }
    [data-testid="stMetric"] {
        background: rgba(25,31,72,.7); border: 1px solid var(--line);
        border-radius: 16px; padding: 14px;
    }
    [data-testid="stMetricValue"] { color: #DCD4FF; }
    [data-testid="stChatMessage"] {
        background: rgba(24,30,67,.72); border: 1px solid rgba(139,124,255,.18);
        border-radius: 16px; padding: 12px;
    }
    .mascot-float {
        position: fixed; right: 22px; bottom: 76px; z-index: 999;
        width: 132px; pointer-events: none;
        filter: drop-shadow(0 8px 20px rgba(112,83,255,.35));
        animation: bob 3.2s ease-in-out infinite;
    }
    @keyframes bob {
        0%,100% { transform: translateY(0) rotate(-1deg); }
        50% { transform: translateY(-11px) rotate(1deg); }
    }
    .sidebar-tip {
        border: 1px solid rgba(139,124,255,.2); border-radius: 15px;
        background: rgba(34,38,87,.48); padding: 13px; color: #BFC2E2;
        font-size: .82rem; margin-top: 18px;
    }
    footer { visibility: hidden; }
    @media (max-width: 800px) {
        .mascot-float { width: 88px; right: 10px; bottom: 65px; }
        .hero { padding: 22px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Floating mascot artwork (the actual chat action is a Streamlit button below).
mascot_uri = mascot_data_uri()
if mascot_uri:
    st.markdown(
        f'<img class="mascot-float" src="{mascot_uri}" alt="Scholo mascot">',
        unsafe_allow_html=True,
    )
else:
    st.sidebar.warning(
        f"Mascot image not found. Place scholo_mascot.png inside: "
        f"{MASCOT_PATH.parent}"
    )
# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------
with st.sidebar:
    st.markdown('<div class="brand">✦ Scholo</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="brand-sub">Your AI Scholarship Companion</div>',
        unsafe_allow_html=True
    )
    st.markdown("---")

    pages = [
        "Home",
        "Find Scholarships",
        "My Profile",
        "Saved Scholarships",
        "My Applications",
        "Deadlines",
        "AI Chat",
    ]

    active = st.radio(
        "NAVIGATION",
        pages,
        key="navigation",
    )

    st.session_state.active_page = active

    st.markdown(
        '<div class="sidebar-tip">✦ Big dreams need the right support.<br>'
        'Scholo is here to help you find your next opportunity.</div>',
        unsafe_allow_html=True,
    )

    st.button(
        "💬 Talk to Scholo",
        use_container_width=True,
        key="sidebar_chat",
        on_click=open_scholo_chat,
    )
# --------------------------------------------------
# HOME
# --------------------------------------------------
if active == "Home":
    st.markdown(
        """
        <div class="hero">
          <div class="eyebrow">Your scholarship journey starts here</div>
          <h1>Find your next opportunity<span style="color:#A995FF">.</span></h1>
          <p>Discover scholarship leads, explore eligibility requirements, and keep your
          education goals moving forward — with Scholo by your side.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    search_col, button_col = st.columns([5, 1])
    with search_col:
        home_query = st.text_input(
            "Search scholarships",
            placeholder="Try: BTech AI scholarships in India",
            label_visibility="collapsed",
            key="home_search",
        )
    with button_col:
        st.button(
    "Search ↗",
    use_container_width=True,
    key="home_search_button",
    on_click=open_chat_with_home_query,
)
    if home_query.strip():
        st.session_state.pending_query = home_query.strip()
        st.session_state.active_page = "AI Chat"
        st.rerun()
    else:
        st.warning("Enter a scholarship search first.")

    st.markdown('<div class="section-heading">What would you like to do?</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    cards = [
        ("🔎", "Find scholarships", "Explore scholarship opportunities for your course."),
        ("🛡️", "Check eligibility", "Compare your profile with scheme requirements."),
        ("🗓️", "Upcoming deadlines", "Look for opportunities with approaching deadlines."),
    ]
    for col, card in zip((c1, c2, c3), cards):
        with col:
            st.markdown(
                f'<div class="mini-card"><div class="icon">{card[0]}</div>'
                f'<h3>{card[1]}</h3><p>{card[2]}</p></div>',
                unsafe_allow_html=True,
            )
    a1, a2, a3 = st.columns(3)

    with a1:
        st.button(
        "Find scholarships",
        use_container_width=True,
        key="home_find",
        on_click=navigate_to,
        args=("AI Chat",),
    )

    with a2:
        st.button(
        "Check my eligibility",
        use_container_width=True,
        key="home_eligibility",
        on_click=navigate_to,
        args=("AI Chat",),
    )

    with a3:
        st.button(
        "Upcoming deadlines",
        use_container_width=True,
        key="home_deadlines",
        on_click=navigate_to,
        args=("Deadlines",),
    )
    st.markdown('<div class="section-heading">Your profile snapshot</div>', unsafe_allow_html=True)
    profile = st.session_state.student_profile
    if profile:
        p1, p2, p3 = st.columns(3)
        p1.metric("Education", profile.get("education_level", "—").title())
        p2.metric("Course", profile.get("course", "—"))
        p3.metric("State", profile.get("state", "—"))
    else:
        st.markdown(
            '<div class="soft-note">Your student profile is not set up yet. '
            'Add your details under <b>My Profile</b> to personalise your searches.</div>',
            unsafe_allow_html=True,
        )
        st.button(
            "Set up my profile →",
            key="home_profile",
            on_click=navigate_to,
            args=("My Profile",),
        )

# --------------------------------------------------
# PROFILE
# --------------------------------------------------
elif active == "My Profile":

    st.markdown(
        '<div class="eyebrow">Personalise your discovery</div>',
        unsafe_allow_html=True
    )

    st.title("My Student Profile")
    st.write(
        "Enter your academic details so Scholo can find scholarships "
        "that match your profile."
    )

    saved = st.session_state.student_profile

    with st.form("student_profile_form"):

        st.subheader("Personal Details")

        state_options = [
            "Tamil Nadu",
            "Kerala",
            "Karnataka",
            "Andhra Pradesh",
            "Telangana",
            "Maharashtra",
            "Delhi",
            "Other",
        ]

        state = st.selectbox(
            "State or Union Territory",
            state_options,
            index=state_options.index(saved["state"])
            if saved.get("state") in state_options else 0
        )

        education_options = [
            "undergraduate",
            "postgraduate",
            "diploma",
            "doctoral",
            "school"
        ]

        education_level = st.selectbox(
            "Education Level",
            education_options,
            index=education_options.index(saved["education_level"])
            if saved.get("education_level") in education_options else 0
        )

        course = st.text_input(
            "Course or Degree",
            value=saved.get("course", ""),
            placeholder="Example: BTech CSE - AI and ML"
        )

        annual_income = st.number_input(
            "Annual Family Income (₹)",
            min_value=0,
            max_value=100000000,
            value=int(saved.get("annual_income_inr", 300000)),
            step=25000
        )

        st.divider()
        st.subheader("Academic Scores")

        tenth = st.number_input(
            "10th Standard Percentage",
            min_value=0.0,
            max_value=100.0,
            value=float(saved.get("tenth_percentage") or 0.0),
            step=0.1
        )

        twelfth = st.number_input(
            "12th Standard Percentage",
            min_value=0.0,
            max_value=100.0,
            value=float(saved.get("twelfth_percentage") or 0.0),
            step=0.1
        )

        cgpa = st.number_input(
            "Current CGPA",
            min_value=0.0,
            max_value=10.0,
            value=float(saved.get("cgpa") or 0.0),
            step=0.01
        )

        cgpa_scale = st.selectbox(
            "CGPA Scale",
            [10.0, 4.0, 5.0],
            index=0
        )

        academic_year = st.selectbox(
            "Academic Year",
            ["2026-27", "2027-28", "2025-26"]
        )

        submitted = st.form_submit_button(
            "Save My Profile",
            use_container_width=True
        )

    if submitted:

        if not course.strip():
            st.warning("Please enter your course or degree.")

        else:

            st.session_state.student_profile = {
                "state": state,
                "education_level": education_level,
                "course": course.strip(),
                "annual_income_inr": int(annual_income),
                "tenth_percentage": float(tenth),
                "twelfth_percentage": float(twelfth),
                "cgpa": float(cgpa),
                "cgpa_scale": float(cgpa_scale),
                "academic_year": academic_year,
            }

            st.success("Your student profile has been saved!")
            st.rerun()
# --------------------------------------------------
# SCHOLARSHIP SEARCH
# --------------------------------------------------
elif active == "Find Scholarships":
    st.markdown('<div class="eyebrow">Explore opportunities</div>', unsafe_allow_html=True)
    st.title("Find scholarships")
    st.write("Search for scholarship opportunities using a topic, course, provider, or location.")
    query = st.text_input("What are you looking for?",
                          placeholder="e.g. BTech AI scholarships for students in Tamil Nadu")
    if st.button("Search scholarships ↗", use_container_width=False, key="find_search"):
        if query.strip():
            result = run_search(query.strip())
            display_results(result)
        else:
            st.warning("Enter a search query.")

# --------------------------------------------------
# AI CHAT
# --------------------------------------------------
elif active == "AI Chat":
    st.markdown('<div class="eyebrow">Your study-funding sidekick</div>', unsafe_allow_html=True)
    st.title("Chat with Scholo")
    st.caption("Ask about scholarship opportunities, eligibility criteria, documents, or deadlines.")
    if mascot_uri:
        st.image(str(MASCOT_PATH), width=145)
    pending = st.session_state.pop("pending_query", None)
    if pending:
        result = run_search(pending)
        with st.chat_message("assistant"):
            if result.get("error"):
                st.error(result["error"])
            else:
                st.markdown(
                    f"I searched for **{pending}**. Here are the results I found. "
                    "Please verify the current requirements on official websites."
                )
                display_results(result)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("results"):
                display_results(message["results"])
    if prompt := st.chat_input("Message Scholo..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        result = run_search(prompt)
        with st.chat_message("assistant"):
            if result.get("error"):
                st.error(result["error"])
            else:
                st.markdown(
                    f"I searched for **{prompt}**. Here are the results. "
                    "Please check official sources before applying."
                )
                display_results(result)
# --------------------------------------------------
# FUTURE SECTIONS (CLEARLY LABELLED)
# --------------------------------------------------
elif active in ["Saved Scholarships", "My Applications", "Deadlines"]:
    st.markdown('<div class="eyebrow">Your scholarship workspace</div>', unsafe_allow_html=True)
    titles = {
        "Saved Scholarships": "Saved scholarships",
        "My Applications": "My applications",
        "Deadlines": "Scholarship deadlines",
    }
    st.title(titles[active])
    st.markdown(
        '<div class="soft-note">This section is part of the new Scholo layout. '
        'Its data and actions will be connected in the next development stage.</div>',
        unsafe_allow_html=True,
    )
    if active == "Saved Scholarships":
        st.info("You will be able to bookmark and revisit scholarship opportunities here.")
    elif active == "My Applications":
        st.info("You will be able to track application status and required documents here.")
    else:
        st.info("Verified deadline tracking will be added after the scholarship data flow is connected.")

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.caption(
    "Scholo is a scholarship discovery assistant. Search results may be incomplete or outdated. "
    "Always verify eligibility, award amounts, and deadlines with the official scholarship provider."
)

