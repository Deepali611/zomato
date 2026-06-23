"""Streamlit UI for restaurant recommendations."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from src.models.preferences import PreferenceValidationError
from src.services.recommendation_service import create_default_service


def clean_html(html: str) -> str:
    """Remove leading indentation from each line to prevent Streamlit/Markdown code block rendering."""
    return "\n".join(line.lstrip() for line in html.splitlines())


def render_label(text: str, value_suffix: str = "") -> None:
    """Render a custom bold uppercase label matching the design system."""
    if value_suffix:
        st.markdown(clean_html(f"""
        <div class="flex justify-between items-center mb-2" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <label class="font-label-bold-caps text-[12px] uppercase font-bold text-[#c7c4d7]" style="font-family:'Inter', sans-serif; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#c7c4d7;">{text}</label>
            <span class="text-[#4edea3] font-bold" style="color:#4edea3; font-weight:700; font-family:'Inter', sans-serif; font-size:14px;">{value_suffix}</span>
        </div>
        """), unsafe_allow_html=True)
    else:
        st.markdown(clean_html(f"""
        <div class="mb-2" style="margin-bottom:8px;">
            <label class="font-label-bold-caps text-[12px] uppercase font-bold text-[#c7c4d7]" style="font-family:'Inter', sans-serif; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#c7c4d7;">{text}</label>
        </div>
        """), unsafe_allow_html=True)


@st.cache_resource
def _get_service():
    return create_default_service()


def main() -> None:
    st.set_page_config(
        page_title="Zomato AI - Concierge Search",
        page_icon="🍽️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    service = _get_service()

    # 1. Custom CSS and styling injection based on DESIGN.md
    st.markdown(clean_html("""
    <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&amp;family=Outfit:wght@400;600;700&amp;display=swap" rel="stylesheet"/>
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
    
    <script>
    // Injected Javascript to support interactive tag clicking
    window.toggleCuisine = window.parent.toggleCuisine = function(cuisineName) {
        const container = window.parent.document.querySelector('div[data-testid="stTextInput"]');
        if (!container) return;
        const input = container.querySelector('input');
        if (!input) return;
        
        let val = input.value.trim();
        let parts = val ? val.split(',').map(s => s.trim()).filter(Boolean) : [];
        
        const partsLower = parts.map(s => s.toLowerCase());
        const index = partsLower.indexOf(cuisineName.toLowerCase());
        
        if (index > -1) {
            parts.splice(index, 1);
        } else {
            parts.push(cuisineName);
        }
        
        const newValue = parts.join(', ');
        const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
        nativeSetter.call(input, newValue);
        input.dispatchEvent(new Event('input', { bubbles: true }));
    };
    </script>
    
    <style>
        /* Ambient background glows */
        .bg-glow-indigo {
            position: fixed !important;
            top: -10% !important;
            right: -10% !important;
            width: 60vw !important;
            height: 60vh !important;
            background: radial-gradient(circle, rgba(192, 193, 255, 0.06) 0%, rgba(192, 193, 255, 0) 70%) !important;
            z-index: -1 !important;
            pointer-events: none !important;
        }
        .bg-glow-emerald {
            position: fixed !important;
            bottom: -10% !important;
            left: -10% !important;
            width: 50vw !important;
            height: 50vh !important;
            background: radial-gradient(circle, rgba(78, 222, 163, 0.05) 0%, rgba(78, 222, 163, 0) 70%) !important;
            z-index: -1 !important;
            pointer-events: none !important;
        }

        /* Body & page layout theme */
        body, [data-testid="stAppViewContainer"], .stApp {
            background-color: #0f131d !important;
            color: #dfe2f1 !important;
            font-family: 'Inter', sans-serif !important;
            overflow-x: hidden !important;
        }
        
        /* Hide native Streamlit header */
        header[data-testid="stHeader"] {
            display: none !important;
        }
        
        /* Custom Top Navigation Bar styling */
        nav.fixed-navbar {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100% !important;
            height: 70px !important;
            z-index: 999999 !important;
            background-color: rgba(15, 19, 29, 0.85) !important;
            backdrop-filter: blur(24px) !important;
            border-bottom: 1px solid rgba(70, 69, 84, 0.3) !important;
            display: flex !important;
            flex-direction: row !important;
            justify-content: space-between !important;
            align-items: center !important;
            padding: 0 24px !important;
            box-sizing: border-box !important;
        }

        .flex-left {
            display: flex !important;
            flex-direction: row !important;
            align-items: center !important;
            gap: 24px !important;
        }

        .flex-right {
            display: flex !important;
            flex-direction: row !important;
            align-items: center !important;
            gap: 16px !important;
        }

        .pills-container {
            display: flex !important;
            flex-direction: row !important;
            gap: 8px !important;
        }

        .pill {
            display: flex !important;
            flex-direction: row !important;
            align-items: center !important;
            gap: 6px !important;
            padding: 4px 12px !important;
            background-color: #1c1f2a !important;
            border-radius: 9999px !important;
            border: 1px solid rgba(70, 69, 84, 0.3) !important;
        }

        .pill-primary {
            color: #c0c1ff !important;
            border-color: rgba(192, 193, 255, 0.3) !important;
        }

        .pill-secondary {
            color: #4edea3 !important;
            border-color: rgba(78, 222, 163, 0.3) !important;
        }

        .pill-text {
            font-family: 'Inter', sans-serif !important;
            font-size: 10px !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.1em !important;
        }

        .avatar-container {
            width: 40px !important;
            height: 40px !important;
            border-radius: 9999px !important;
            border: 2px solid #8083ff !important;
            overflow: hidden !important;
            display: block !important;
        }

        .avatar-img {
            width: 40px !important;
            height: 40px !important;
            object-fit: cover !important;
            display: block !important;
        }

        /* Push content below top nav */
        [data-testid="stSidebarUserContent"] {
            padding-top: 50px !important;
        }
        [data-testid="stMainBlockContainer"] {
            padding-top: 60px !important;
        }
        
        /* Hide scrollbars */
        ::-webkit-scrollbar {
            display: none !important;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: rgba(28, 31, 42, 0.8) !important;
            backdrop-filter: blur(24px) !important;
            border-right: 1px solid rgba(144, 143, 160, 0.2) !important;
            width: 380px !important;
        }
        
        /* Remove default form border and background inside sidebar */
        [data-testid="stSidebar"] .stForm {
            border: none !important;
            background: transparent !important;
            padding: 0 !important;
        }
        
        /* Custom styled controls for selectbox, text input, slider and text area */
        div[data-testid="stSelectbox"] div[data-baseweb="select"], 
        div[data-testid="stTextInput"] div[data-baseweb="input"], 
        div[data-testid="stTextArea"] textarea {
            background-color: #262a35 !important;
            border: 1px solid rgba(144, 143, 160, 0.2) !important;
            border-radius: 12px !important;
            color: #dfe2f1 !important;
        }
        
        div[data-testid="stSelectbox"] div[data-baseweb="select"]:focus-within, 
        div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within, 
        div[data-testid="stTextArea"] textarea:focus {
            border-color: #c0c1ff !important;
            box-shadow: 0 0 10px rgba(192, 193, 255, 0.2) !important;
        }
        
        /* Location selectbox pin icon */
        div[data-testid="stSelectbox"] div[data-baseweb="select"] {
            position: relative !important;
        }
        div[data-testid="stSelectbox"] div[data-baseweb="select"]::before {
            content: "location_on" !important;
            font-family: 'Material Symbols Outlined' !important;
            position: absolute !important;
            left: 12px !important;
            top: 50% !important;
            transform: translateY(-50%) !important;
            color: #908fa0 !important;
            font-size: 20px !important;
            z-index: 2 !important;
            pointer-events: none !important;
        }
        div[data-testid="stSelectbox"] div[data-baseweb="select"] [role="combobox"] {
            padding-left: 36px !important;
        }
        
        /* Custom st.radio styled as Segmented Control */
        div[data-testid="stRadio"] div[role="radiogroup"] {
            display: flex !important;
            flex-direction: row !important;
            background-color: #0a0e18 !important;
            padding: 4px !important;
            border-radius: 12px !important;
            border: 1px solid rgba(70, 69, 84, 0.2) !important;
            gap: 4px !important;
            width: 100% !important;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] {
            flex: 1 !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            padding: 8px 12px !important;
            border-radius: 8px !important;
            background-color: transparent !important;
            border: 1px solid transparent !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            margin: 0 !important;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child {
            display: none !important;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] div[data-testid="stMarkdownContainer"] p {
            font-family: 'Inter', sans-serif !important;
            font-size: 12px !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.1em !important;
            color: #c7c4d7 !important;
            margin: 0 !important;
            text-align: center !important;
            width: 100% !important;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
            background-color: rgba(78, 222, 163, 0.15) !important;
            border-color: rgba(78, 222, 163, 0.3) !important;
            box-shadow: 0 0 15px rgba(78, 222, 163, 0.2) !important;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) div[data-testid="stMarkdownContainer"] p {
            color: #4edea3 !important;
            font-weight: 700 !important;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"]:hover:not(:has(input:checked)) {
            background-color: #353944 !important;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"]:hover:not(:has(input:checked)) div[data-testid="stMarkdownContainer"] p {
            color: #dfe2f1 !important;
        }

        /* Slider track styling */
        div[data-testid="stSlider"] [data-testid="stSliderTickBar"] {
            display: none !important;
        }
        div[data-testid="stSlider"] [data-testid="stSliderThumbValue"] {
            display: none !important;
        }
        div[data-testid="stSlider"] div[role="presentation"] {
            background: linear-gradient(to right, #4edea3, #c0c1ff) !important;
            height: 6px !important;
            border-radius: 3px !important;
        }
        div[data-testid="stSlider"] [role="slider"] {
            background-color: #ffffff !important;
            box-shadow: 0 0 12px rgba(192, 193, 255, 0.9) !important;
            border: none !important;
            width: 20px !important;
            height: 20px !important;
            top: -7px !important;
        }
        
        /* Submit Button Styling */
        button[kind="primaryFormSubmit"] {
            background-color: #00a572 !important;
            color: #00311f !important;
            font-family: 'Outfit', sans-serif !important;
            font-size: 18px !important;
            font-weight: 600 !important;
            border-radius: 12px !important;
            border: none !important;
            width: 100% !important;
            padding: 12px !important;
            box-shadow: 0 0 25px rgba(78, 222, 163, 0.3) !important;
            transition: all 0.3s ease !important;
            margin-top: 1.5rem !important;
            cursor: pointer !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }
        button[kind="primaryFormSubmit"]:hover {
            transform: scale(1.02) !important;
            box-shadow: 0 0 40px rgba(78, 222, 163, 0.5) !important;
        }
        button[kind="primaryFormSubmit"]:active {
            transform: scale(0.98) !important;
        }
        button[kind="primaryFormSubmit"] p::before {
            content: "auto_awesome" !important;
            font-family: 'Material Symbols Outlined' !important;
            font-variation-settings: 'FILL' 1 !important;
            margin-right: 8px !important;
            font-size: 18px !important;
            vertical-align: middle !important;
        }

        /* Results Grid Layout and Card styles */
        .results-grid {
            display: grid !important;
            grid-template-columns: repeat(1, 1fr) !important;
            gap: 24px !important;
            width: 100% !important;
        }
        @media (min-width: 1200px) {
            .results-grid {
                grid-template-columns: repeat(3, 1fr) !important;
            }
        }

        .glass-card {
            background: rgba(49, 53, 64, 0.7) !important;
            backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(144, 143, 160, 0.2) !important;
            border-radius: 16px !important;
            overflow: hidden !important;
            transition: all 0.3s ease !important;
            display: flex !important;
            flex-direction: column !important;
        }
        .glass-card:hover {
            transform: scale(1.02) !important;
        }
        .card-img-container {
            position: relative !important;
            height: 192px !important;
            overflow: hidden !important;
        }
        .card-img {
            width: 100% !important;
            height: 100% !important;
            object-fit: cover !important;
            transition: transform 0.5s ease !important;
        }
        .glass-card:hover .card-img {
            transform: scale(1.1) !important;
        }
        .rank-badge {
            position: absolute !important;
            top: 16px !important;
            left: 16px !important;
            background-color: rgba(15, 19, 29, 0.8) !important;
            backdrop-filter: blur(8px) !important;
            padding: 4px 12px !important;
            border-radius: 8px !important;
            border: 1px solid rgba(144, 143, 160, 0.3) !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 10px !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.1em !important;
            color: #c0c1ff !important;
        }
        .card-body {
            padding: 24px !important;
            display: flex !important;
            flex-direction: column !important;
            gap: 16px !important;
            flex-grow: 1 !important;
        }
        .card-header-row {
            display: flex !important;
            justify-content: space-between !important;
            align-items: flex-start !important;
            gap: 12px !important;
        }
        .card-title {
            font-family: 'Outfit', sans-serif !important;
            font-size: 20px !important;
            font-weight: 700 !important;
            color: #dfe2f1 !important;
            margin: 0 !important;
        }
        .rating-badge {
            display: flex !important;
            align-items: center !important;
            gap: 4px !important;
            background-color: rgba(0, 165, 114, 0.15) !important;
            padding: 4px 8px !important;
            border-radius: 8px !important;
            border: 1px solid rgba(0, 165, 114, 0.3) !important;
            flex-shrink: 0 !important;
        }
        .rating-text {
            color: #4edea3 !important;
            font-weight: 700 !important;
            font-size: 14px !important;
            font-family: 'Inter', sans-serif !important;
        }
        .cuisines-row {
            display: flex !important;
            flex-wrap: wrap !important;
            gap: 8px !important;
        }
        .cuisine-pill {
            font-family: 'Inter', sans-serif !important;
            font-size: 12px !important;
            padding: 2px 8px !important;
            background-color: #313540 !important;
            border-radius: 4px !important;
            border: 1px solid rgba(70, 69, 84, 0.3) !important;
            color: #c7c4d7 !important;
        }
        .meta-row {
            display: flex !important;
            justify-content: space-between !important;
            font-size: 14px !important;
            font-family: 'Inter', sans-serif !important;
        }
        .meta-cost {
            color: #c7c4d7 !important;
        }
        .meta-loc {
            color: #908fa0 !important;
        }
        .reason-box {
            padding: 12px !important;
            background-color: rgba(0, 165, 114, 0.05) !important;
            border-left: 4px solid #4edea3 !important;
            border-radius: 0 8px 8px 0 !important;
            margin-top: auto !important;
        }
        .reason-text {
            font-size: 14px !important;
            font-style: italic !important;
            color: #c7c4d7 !important;
            margin: 0 !important;
            font-family: 'Inter', sans-serif !important;
        }
    </style>
    """), unsafe_allow_html=True)

    # 2. Sidebar Search form setup
    with st.sidebar:
        st.markdown(clean_html("""
        <div class="space-y-2 mb-6 pt-4">
            <h2 class="font-headline-md text-2xl font-bold text-[#c0c1ff]" style="font-family:'Outfit';">Concierge Search</h2>
            <p class="font-label-sm text-sm text-[#c7c4d7]">AI-Powered Discovery</p>
        </div>
        """), unsafe_allow_html=True)

        with st.form("preferences_form"):
            # Get unique locations dynamically from dataset
            unique_locations = sorted(list({r.location for r in service.repository.get_all() if r.location}))
            default_loc_idx = 0
            if "Indiranagar" in unique_locations:
                default_loc_idx = unique_locations.index("Indiranagar")
            elif "BTM" in unique_locations:
                default_loc_idx = unique_locations.index("BTM")

            render_label("Location")
            location = st.selectbox("Location", options=unique_locations, index=default_loc_idx, label_visibility="collapsed")
            
            render_label("Budget Range")
            budget_display = st.radio("Budget Range", ["Low", "Medium", "High"], index=1, horizontal=True, label_visibility="collapsed")
            budget = budget_display.lower()
            
            render_label("Cuisines")
            cuisine = st.text_input("Cuisines", placeholder="Add cuisine...", value="Italian", label_visibility="collapsed")
            
            # Interactive tags
            active_cuisines = [c.strip() for c in cuisine.split(",") if c.strip()]
            active_cuisines_lower = [c.lower() for c in active_cuisines]
            suggestions = ["Italian", "Chinese", "South Indian"]
            
            tags_html = '<div class="flex flex-wrap gap-2 pt-2" style="display:flex; flex-wrap:wrap; gap:8px; padding-top:8px; padding-bottom:16px;">'
            for sug in suggestions:
                sug_lower = sug.lower()
                if sug_lower in active_cuisines_lower:
                    tags_html += f"""
                    <span onclick="toggleCuisine('{sug}')" class="px-3 py-1 rounded-full text-[12px] flex items-center gap-1" style="background-color:rgba(192, 193, 255, 0.1); border:1px solid rgba(192, 193, 255, 0.3); color:#c0c1ff; border-radius:9999px; padding:4px 12px; font-size:12px; font-family:'Inter'; font-weight:500; cursor:pointer; display:flex; align-items:center; gap:4px;">
                        {sug} <span class="material-symbols-outlined text-[14px]" style="font-size:14px;">close</span>
                    </span>
                    """
                else:
                    tags_html += f"""
                    <span onclick="toggleCuisine('{sug}')" class="px-3 py-1 rounded-full text-[12px] flex items-center gap-1" style="background-color:#313540; border:1px solid rgba(144, 143, 160, 0.3); color:#c7c4d7; border-radius:9999px; padding:4px 12px; font-size:12px; font-family:'Inter'; font-weight:500; cursor:pointer; display:flex; align-items:center; gap:4px;">
                        {sug}
                    </span>
                    """
            tags_html += '</div>'
            st.markdown(clean_html(tags_html), unsafe_allow_html=True)
            
            # Slider label with dynamic value
            slider_val = st.session_state.get("min_rating_slider", 4.0)
            render_label("Minimum Rating", f"{slider_val:.1f}+")
            min_rating = st.slider(
                "Minimum Rating",
                0.0,
                5.0,
                4.0,
                0.1,
                key="min_rating_slider",
                label_visibility="collapsed"
            )
            st.markdown(clean_html("""
            <div class="flex justify-between text-[10px] text-[#908fa0] px-1" style="margin-top:-8px; display:flex; justify-content:space-between; font-size:10px; color:#908fa0; font-family:'Inter';">
                <span>0.0</span>
                <span>2.5</span>
                <span>5.0</span>
            </div>
            """), unsafe_allow_html=True)
            
            render_label("Natural Language Constraints")
            additional = st.text_area(
                "Natural Language Constraints",
                placeholder="e.g. rooftop, romantic, live music, outdoor seating...",
                value="romantic rooftop",
                label_visibility="collapsed"
            )
            submitted = st.form_submit_button("Generate")

    # 3. Main content area setup
    # Render Top Navigation bar overlay
    st.markdown(clean_html("""
    <div class="bg-glow-indigo"></div>
    <div class="bg-glow-emerald"></div>
    <nav class="fixed-navbar">
        <div class="flex-left">
            <span class="font-headline-lg text-2xl font-bold text-[#dfe2f1]" style="font-family:'Outfit'; text-shadow:0 0 15px rgba(192,193,255,0.5);">🍽️ Zomato AI</span>
            <div class="pills-container">
                <div class="pill pill-primary">
                    <span class="material-symbols-outlined text-[#c0c1ff]" style="font-size:14px;">memory</span>
                    <span class="pill-text text-[#c0c1ff]">Groq / Llama 3.3</span>
                </div>
                <div class="pill pill-secondary">
                    <span class="material-symbols-outlined text-[#4edea3]" style="font-size:14px;">database</span>
                    <span class="pill-text text-[#4edea3]">In-Memory Dataset</span>
                </div>
            </div>
        </div>
        <div class="flex-right">
            <span class="material-symbols-outlined text-[#c7c4d7] hover:text-[#c0c1ff] transition-colors cursor-pointer" style="font-size: 24px;">notifications</span>
            <div class="avatar-container">
                <img class="avatar-img" alt="User Profile" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCO8c5rbiG4JWcz-GhcCd5UJ8lLKKUjxHvAvVh3yZkJ0C1TB_5n4dZ0rmBKcMVKcMoEBuxNXo4UWfaE7hVW_ThNIX27Tuld64KIVs9FSwVWE4h4S3n7OntsAL_1F45QIM4JAE4hFIC4rwWYihwBkh-FTniCZjZrkPs4CHn2tF0nk4uJup6DeGEGC2_yDYn7pXqyXV_u0OVYOlfdyKBE_ICrfJ41SIeZDLLbbphrva883Knq1oL5sNoV1hZgZsMDrLCdaLXqMGd1ct4"/>
            </div>
        </div>
    </nav>
    """), unsafe_allow_html=True)

    # Resolve recommendations
    if submitted:
        raw = {
            "location": location,
            "budget": budget,
            "cuisine": cuisine,
            "min_rating": min_rating,
            "additional_preferences": additional.strip() or None,
        }

        try:
            with st.spinner("Finding restaurants and ranking with AI..."):
                result = service.recommend(raw)
                rec = result.recommendation
        except PreferenceValidationError as exc:
            st.error(str(exc))
            return
        except Exception as exc:
            st.error(f"Something went wrong: {exc}")
            return
    else:
        # Default mock state matching DESIGN.md and code.html on first load
        class MockItem:
            def __init__(self, rank: int, name: str, rating: float, cuisines: list[str], cost_for_two: float, location: str, explanation: str, restaurant_id: str = "") -> None:
                self.restaurant_id = restaurant_id
                self.rank = rank
                self.name = name
                self.rating = rating
                self.cuisines = cuisines
                self.cost_for_two = cost_for_two
                self.location = location
                self.explanation = explanation

        class MockRecommendation:
            def __init__(self) -> None:
                self.summary = 'Based on your preference for <span class="text-[#c0c1ff] font-semibold">romantic rooftop</span> vibes and <span class="text-[#4edea3] font-semibold">Italian cuisine</span> in Indiranagar, I\'ve curated a list of top-tier spots. Most of these venues are seeing peak activity tonight, so I recommend securing a reservation within the next 15 minutes.'
                self.recommendations = [
                    MockItem(
                        rank=1,
                        name="The Aviary Rooftop",
                        rating=4.8,
                        cuisines=["Italian", "Fine Dining"],
                        cost_for_two=2500,
                        location="Indiranagar",
                        explanation="Unparalleled panoramic views combined with authentic wood-fired pizzas make this the perfect romantic escape you described."
                    ),
                    MockItem(
                        rank=2,
                        name="Lupa Italian",
                        rating=4.6,
                        cuisines=["Contemporary Italian", "Cocktails"],
                        cost_for_two=3000,
                        location="MG Road",
                        explanation="High-energy atmosphere with a specialized hand-crafted pasta menu that caters to your specific cuisine tag preferences."
                    ),
                    MockItem(
                        rank=3,
                        name="Bologna Bistro",
                        rating=4.5,
                        cuisines=["Classic Italian", "Wine Bar"],
                        cost_for_two=1800,
                        location="Indiranagar",
                        explanation="A hidden gem with dim lighting and excellent hospitality, providing the 'romantic' constraint in a more intimate setting."
                    )
                ]
                self.degraded = False
                self.warnings: list[str] = []

        rec = MockRecommendation()

    # Build warning alerts html
    warnings_html = ""
    if submitted:
        all_warnings = []
        if service.llm_warning:
            all_warnings.append(service.llm_warning)
        all_warnings.extend(result.messages)
        for msg in all_warnings:
            if "relaxed" in msg.lower() or "truncated" in msg.lower() or "degraded" in msg.lower():
                warnings_html += f"""
                <div class="glass-card p-4 rounded-xl border-l-4 border-[#ffb95f] bg-[#ffb95f]/5 text-[#ffb95f] mb-6 flex items-center gap-3">
                    <span class="material-symbols-outlined text-xl">warning</span>
                    <span class="text-sm font-medium">{msg}</span>
                </div>
                """

    if not rec.recommendations:
        st.markdown(clean_html(f"""
        {warnings_html}
        <div class="glass-card p-8 rounded-2xl border-l-4 border-[#ffb4ab] bg-[#ffb4ab]/5 text-[#ffb4ab] text-center">
            <span class="material-symbols-outlined text-5xl mb-4">sentiment_dissatisfied</span>
            <h3 class="font-headline-md text-xl font-bold mb-2">No Match Found</h3>
            <p class="text-sm text-[#c7c4d7]">Try relaxing your rating or cuisine filters to discover more restaurants.</p>
        </div>
        """), unsafe_allow_html=True)
        return

    # Build AI Summary insights
    summary_html = ""
    if rec.summary:
        summary_html = f"""
        <section class="glass-card p-6 rounded-2xl border-l-4 border-[#c0c1ff] neon-glow-indigo mb-8" style="margin-bottom: 32px;">
            <div class="flex items-start gap-4" style="display: flex; align-items: flex-start; gap: 16px;">
                <div class="w-12 h-12 rounded-xl bg-[#c0c1ff]/10 flex items-center justify-center flex-shrink-0" style="width: 48px; height: 48px; border-radius: 12px; background-color: rgba(192, 193, 255, 0.1); display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                    <span class="material-symbols-outlined text-[#c0c1ff] text-3xl" style="font-size: 30px; color:#c0c1ff;">chat_bubble</span>
                </div>
                <div class="space-y-2" style="display: flex; flex-direction: column; gap: 8px;">
                    <h3 class="font-headline-md text-xl font-bold" style="font-family:'Outfit', sans-serif; font-size: 20px; font-weight: 700; margin: 0; color:#dfe2f1;">AI Insights for your Evening</h3>
                    <p class="text-body-lg text-[#c7c4d7] leading-relaxed" style="font-family:'Inter', sans-serif; font-size: 16px; color:#c7c4d7; line-height: 1.6; margin: 0;">
                        {rec.summary}
                    </p>
                </div>
            </div>
        </section>
        """

    # Build Recommendation Cards grid HTML
    cards_html = ""
    for i, item in enumerate(rec.recommendations[:3]):
        rank = item.rank
        name = item.name
        rating = f"{item.rating:.1f}" if item.rating is not None else "N/A"
        cuisines_list = item.cuisines if item.cuisines else []
        cuisines_html = "".join([
            f'<span class="cuisine-pill">{c}</span>'
            for c in cuisines_list[:3]
        ])
        cost = f"₹{item.cost_for_two:,.0f} for two" if item.cost_for_two is not None else "N/A"
        # Get location from repository lookup if not present on item (RecommendationItem)
        loc = getattr(item, "location", None)
        if not loc:
            matches = service.repository.get_by_ids([item.restaurant_id])
            if matches:
                loc = matches[0].location
            else:
                loc = "Unknown"
        explanation = item.explanation

        # Premium card images from code.html
        img_urls = [
            "https://lh3.googleusercontent.com/aida-public/AB6AXuD16t3b3NtGy7FN_Vaxe2VVA9pvdFVh1QwXB7XhoBq9MiXq7xAF3AOIFKixMF26Xnwp1llyCcjWoou7DECQcDd-L-w8odsXAAMKq_MYy-9fdlTx1aDyEhiuB8js5RFt90V6oGuVhh57RG_crqAXhu2V488z9WjOQdf9qmlsjPwYp7lQPxyWN5oZpCzPXW8bscLmEgZPE1QhSYZgF0ITyp9Rc-1f0_OZQ-TwjrthFdSZUGxzoWPaWOjLCX5sJqMkp1gGSBljdBFdfqo",
            "https://lh3.googleusercontent.com/aida-public/AB6AXuC2ns28CkDvGT8btORKTmQqvQtbjo6SGYGCbN-CGTNj1tT0CKKNugFWoHV5W_MQ9Hfi0BLlyvNIxaGNAcHUzla6zCqIUilbJOGwwq4Irj1TIyqvaTGYdx5YQrpJUMsCYm35EdZIFfM3LPiEZPGo1n7tyKa19OclckdWbOhymaQdCScH-6doJfUzwz2r8RnuPLmc6g_r1SjCeu2MqLWuBclwMGsrPFcEovIOi3zJxx4rplzwbjFN8YpUZcqVnJGV1ceXr82AueI4a18",
            "https://lh3.googleusercontent.com/aida-public/AB6AXuAtrFR9F_tERih7a2zJXRhYIg2Hel0mSV97KOxmqC1dKYRayaLa9Aoy_045OGqDOlNjTHHN_y1BCo4Zc7rn846wRLjrJfe2Ks2kaMhYpo4cDqBbX7LLUFehEvXwCYDWYAaj9jcb5E1UYKFkSoEy1ejLvBGBuT7zmDVEpT4EmXGa_PW7q2WTrJNYR_EONNiUN3qXHiEwIXmai-ZEzNxoH3QovsBsRefsOZaTyn7UnzrPwkLpCEfeu8k27GcInW8D3JHeHvHVqRuO46w"
        ]
        img_url = img_urls[i % len(img_urls)]

        cards_html += f"""
        <div class="glass-card">
            <div class="card-img-container">
                <img class="card-img" src="{img_url}" />
                <div class="rank-badge">#{rank} Rank</div>
            </div>
            <div class="card-body">
                <div class="card-header-row">
                    <h4 class="card-title">{name}</h4>
                    <div class="rating-badge">
                        <span class="material-symbols-outlined text-[#4edea3]" style="font-size:14px; font-variation-settings: 'FILL' 1;">star</span>
                        <span class="rating-text">{rating}</span>
                    </div>
                </div>
                <div class="cuisines-row">
                    {cuisines_html}
                </div>
                <div class="meta-row">
                    <span class="meta-cost">{cost}</span>
                    <span class="meta-loc">{loc}</span>
                </div>
                <div class="reason-box">
                    <p class="reason-text">
                        "Why this fits: {explanation}"
                    </p>
                </div>
            </div>
        </div>
        """

    # 4. Render main workspace feed using the exact HTML structure from code.html
    st.markdown(clean_html(f"""
    <div style="display:flex; flex-direction:column; gap:24px; position:relative; width:100%;">
        {warnings_html}
        {summary_html}
        
        <!-- Results Grid -->
        <div class="results-grid">
            {cards_html}
        </div>
        
        <!-- More Results CTA -->
        <div style="display:flex; justify-content:center; padding-top:24px;">
            <button class="px-8 py-3 rounded-full border border-[#464554]/30 text-[#c7c4d7] hover:bg-[#353944] hover:text-[#c0c1ff] transition-all flex items-center gap-2" style="background:transparent; cursor:pointer; display:flex; flex-direction:row; align-items:center; gap:8px; border:1px solid rgba(70,69,84,0.3); border-radius:9999px; padding:12px 24px; color:#c7c4d7; font-family:'Inter', sans-serif; font-size:14px; font-weight:500;">
                <span class="material-symbols-outlined">expand_more</span>
                <span>Discover More Matches</span>
            </button>
        </div>
    </div>
    """), unsafe_allow_html=True)


if __name__ == "__main__":
    main()

