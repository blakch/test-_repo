# -*- coding: utf-8 -*-
"""Figma 'Start here' 디자인을 Streamlit으로 표시하는 앱."""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
HERO_PATH = ASSETS_DIR / "hero.png"
CSS_PATH = BASE_DIR / "styles.css"

BODY_HTML = """
<main class="start-here" aria-label="Start here">
  <div class="start-here__bg" aria-hidden="true">
    <span class="glow glow--blue glow--1"></span>
    <span class="glow glow--blue glow--2"></span>
    <span class="glow glow--purple glow--3"></span>
    <span class="glow glow--purple glow--4"></span>
  </div>

  <img class="start-here__hero" src="{hero_src}" alt="" width="1200" height="1179" />

  <div class="logos" aria-label="Plugin logos">
    <div class="logo-badge logo-badge--figma">
      <span class="logo-badge__glow"></span>
      <span class="logo-badge__icon" aria-hidden="true">
        <svg viewBox="0 0 38 44" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12.5 44C5.6 44 0 38.4 0 31.5V12.5C0 5.6 5.6 0 12.5 0h12.5v11h-9.5c-1.1 0-2 .9-2 2v20.5c0 1.1.9 2 2 2h9.5v11H12.5z" fill="#AC7EF4"/>
          <path d="M25 0h12.5C44.4 0 50 5.6 50 12.5 50 19.4 44.4 25 37.5 25H25V0z" fill="#A259FF"/>
          <path d="M25 25h12.5c6.9 0 12.5 5.6 12.5 12.5S44.4 50 37.5 50H25V25z" fill="#F24E1E"/>
          <path d="M25 12.5C25 5.6 30.6 0 37.5 0 44.4 0 50 5.6 50 12.5 50 19.4 44.4 25 37.5 25H25V12.5z" fill="#FF7262"/>
          <path d="M12.5 12.5C12.5 5.6 18.1 0 25 0v25h-12.5c-6.9 0-12.5-5.6-12.5-12.5z" fill="#1ABCFE"/>
        </svg>
      </span>
    </div>
    <div class="logo-badge logo-badge--code">
      <span class="logo-badge__glow logo-badge__glow--lime"></span>
      <span class="logo-badge__icon logo-badge__icon--lime" aria-hidden="true">
        <svg viewBox="0 0 29 43" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M8 0L0 8v27l8 8h13l8-8V8l-8-8H8z" stroke="#CAF829" stroke-width="2" fill="#1D2023"/>
          <path d="M10 14l9 7.5L10 29" stroke="#CAF829" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </span>
    </div>
  </div>

  <div class="headline">
    <p class="headline__eyebrow">{eyebrow}</p>
    <h1 class="headline__title">{title}</h1>
  </div>
</main>
"""


def hero_data_uri() -> str:
    if not HERO_PATH.exists():
        return ""
    encoded = base64.b64encode(HERO_PATH.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def load_styles() -> str:
    return CSS_PATH.read_text(encoding="utf-8")


def build_page_html(eyebrow: str, title: str) -> str:
    css = load_styles()
    body = BODY_HTML.format(hero_src=hero_data_uri(), eyebrow=eyebrow, title=title)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500&display=swap" rel="stylesheet" />
  <style>{css}</style>
  <style>
    html, body {{
      margin: 0;
      padding: 0;
      background: #0b0d18;
      overflow: hidden;
    }}
    body {{
      min-height: 0;
      padding: 0;
    }}
    .start-here {{
      margin: 0 auto;
    }}
  </style>
</head>
<body>{body}</body>
</html>"""


def inject_streamlit_chrome_hide() -> None:
    st.markdown(
        """
        <style>
          #MainMenu, footer, header { visibility: hidden; }
          .block-container { padding-top: 0.5rem; padding-bottom: 1rem; max-width: 100%; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="Start here — Figma to Code",
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_streamlit_chrome_hide()

    with st.sidebar:
        st.header("설정")
        eyebrow = st.text_input("Eyebrow", value="Start here")
        title = st.text_input("Title", value="Using Figma to Code Plugin")
        frame_height = st.slider("프레임 높이 (px)", min_value=480, max_value=1200, value=900, step=20)
        st.caption("Figma frame: Start here (1200×1200)")
        if not HERO_PATH.exists():
            st.warning("`assets/hero.png` 파일이 없습니다.")

    html = build_page_html(eyebrow=eyebrow, title=title)
    components.html(html, height=frame_height + 24, scrolling=False)


if __name__ == "__main__":
    main()
