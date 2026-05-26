import streamlit as st


def apply_calm_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --calm-bg: #f6f4ee;
            --calm-panel: rgba(255, 252, 245, 0.92);
            --calm-panel-strong: #fffaf1;
            --calm-mint: #bfd9c7;
            --calm-sage: #7ca38b;
            --calm-blue: #b8d7df;
            --calm-lavender: #d7cbe8;
            --calm-peach: #f1c9b7;
            --calm-ink: #31413b;
            --calm-muted: #68766f;
            --calm-line: rgba(102, 129, 116, 0.2);
        }

        .stApp {
            background:
                radial-gradient(circle at 12% 10%, rgba(184, 215, 223, 0.34), transparent 28rem),
                radial-gradient(circle at 88% 8%, rgba(215, 203, 232, 0.28), transparent 24rem),
                linear-gradient(180deg, #f8f5ed 0%, #eef6f1 100%);
            color: var(--calm-ink);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #eef5ef 0%, #f9f3ea 100%);
            border-right: 1px solid var(--calm-line);
        }

        h1, h2, h3 {
            color: var(--calm-ink);
            letter-spacing: 0;
        }

        p, li, label, .stCaption, [data-testid="stMarkdownContainer"] {
            color: var(--calm-muted);
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1180px;
        }

        .calm-hero {
            position: relative;
            overflow: hidden;
            min-height: 300px;
            padding: 2.2rem;
            border: 1px solid var(--calm-line);
            border-radius: 18px;
            background:
                linear-gradient(135deg, rgba(255, 252, 245, 0.95), rgba(234, 246, 239, 0.9)),
                linear-gradient(90deg, rgba(191, 217, 199, 0.28), rgba(184, 215, 223, 0.24));
            box-shadow: 0 18px 45px rgba(93, 121, 108, 0.12);
        }

        .calm-hero h1 {
            max-width: 720px;
            margin: 0;
            font-size: clamp(2rem, 4vw, 3.6rem);
            line-height: 1.12;
        }

        .calm-hero p {
            max-width: 680px;
            margin-top: 1rem;
            font-size: 1.05rem;
            line-height: 1.8;
        }

        .calm-hero-art {
            position: absolute;
            right: 2rem;
            bottom: 1.2rem;
            width: min(32vw, 300px);
            min-width: 210px;
            pointer-events: none;
        }

        .calm-card-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 1rem;
            margin-top: 1.3rem;
        }

        .calm-card {
            min-height: 135px;
            padding: 1rem;
            border: 1px solid var(--calm-line);
            border-radius: 14px;
            background: var(--calm-panel);
            box-shadow: 0 10px 28px rgba(92, 118, 105, 0.1);
        }

        .calm-card b {
            display: block;
            margin-bottom: 0.45rem;
            color: var(--calm-ink);
            font-size: 1rem;
        }

        .calm-card span {
            color: var(--calm-muted);
            line-height: 1.65;
            font-size: 0.94rem;
        }

        .soft-panel {
            padding: 1.1rem 1.2rem;
            border: 1px solid var(--calm-line);
            border-radius: 14px;
            background: var(--calm-panel);
            box-shadow: 0 10px 28px rgba(92, 118, 105, 0.08);
        }

        .gentle-note {
            padding: 0.9rem 1rem;
            border-left: 5px solid var(--calm-sage);
            border-radius: 12px;
            background: rgba(255, 250, 241, 0.86);
            color: var(--calm-muted);
        }

        div.stButton > button,
        div.stDownloadButton > button,
        button[kind="primary"] {
            border: 0;
            border-radius: 999px;
            background: linear-gradient(135deg, #7ca38b, #6b93a0);
            color: white;
            box-shadow: 0 8px 18px rgba(94, 128, 111, 0.24);
        }

        div.stButton > button:hover,
        div.stDownloadButton > button:hover {
            color: white;
            border: 0;
            filter: brightness(1.03);
        }

        textarea, input, [data-baseweb="select"] > div {
            border-radius: 14px !important;
            border-color: rgba(124, 163, 139, 0.32) !important;
            background: rgba(255, 252, 245, 0.88) !important;
        }

        [data-testid="stMetric"] {
            padding: 1rem;
            border: 1px solid var(--calm-line);
            border-radius: 14px;
            background: var(--calm-panel);
        }

        [data-testid="stChatMessage"] {
            border-radius: 14px;
            border: 1px solid rgba(124, 163, 139, 0.16);
            background: rgba(255, 252, 245, 0.72);
        }

        @media (max-width: 900px) {
            .calm-card-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
            .calm-hero {
                padding: 1.4rem;
                min-height: 420px;
            }
            .calm-hero-art {
                right: 50%;
                transform: translateX(50%);
                bottom: 0.8rem;
                width: 240px;
            }
        }

        @media (max-width: 560px) {
            .calm-card-grid {
                grid-template-columns: 1fr;
            }
            .calm-hero {
                min-height: 470px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_cartoon_companion() -> str:
    return """
    <svg class="calm-hero-art" viewBox="0 0 320 260" role="img" aria-label="卡通陪伴插画">
      <defs>
        <linearGradient id="leafGrad" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0" stop-color="#bfd9c7"/>
          <stop offset="1" stop-color="#7ca38b"/>
        </linearGradient>
        <linearGradient id="skyGrad" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0" stop-color="#b8d7df"/>
          <stop offset="1" stop-color="#d7cbe8"/>
        </linearGradient>
      </defs>
      <ellipse cx="162" cy="230" rx="112" ry="17" fill="#d8ded2"/>
      <path d="M80 160c-38-35-17-88 28-83 12-44 77-54 100-13 42-4 70 34 53 70 36 18 29 76-18 82H105c-47-3-66-31-25-56z" fill="#fffaf1" stroke="#8faf9e" stroke-width="4"/>
      <circle cx="132" cy="130" r="9" fill="#31413b"/>
      <circle cx="198" cy="130" r="9" fill="#31413b"/>
      <path d="M142 160c16 15 34 15 50 0" fill="none" stroke="#31413b" stroke-width="6" stroke-linecap="round"/>
      <circle cx="108" cy="150" r="13" fill="#f1c9b7" opacity=".74"/>
      <circle cx="223" cy="150" r="13" fill="#f1c9b7" opacity=".74"/>
      <path d="M65 99c-24-32-9-64 24-76 8 34 1 61-24 76z" fill="url(#leafGrad)" opacity=".9"/>
      <path d="M252 90c-5-36 17-61 53-62-8 34-24 55-53 62z" fill="url(#skyGrad)" opacity=".9"/>
      <path d="M142 73c-12-26 3-48 32-54 4 29-7 47-32 54z" fill="#d7cbe8" opacity=".85"/>
      <path d="M86 206c-14 13-38 14-52-1 21-13 38-12 52 1z" fill="#bfd9c7"/>
      <path d="M254 205c15 13 39 12 52-4-22-11-39-10-52 4z" fill="#b8d7df"/>
    </svg>
    """


def render_home_hero() -> None:
    st.markdown(
        f"""
        <section class="calm-hero">
          <h1>基于 NLP 的多模态情绪陪伴与情感分析系统</h1>
          <p>用柔和的界面承接文字、音频、视频与 CSV 数据，识别情绪变化，生成温和回应和可导出的分析报告。</p>
          {render_cartoon_companion()}
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_feature_cards() -> None:
    st.markdown(
        """
        <div class="calm-card-grid">
          <div class="calm-card"><b>情绪聊天</b><span>输入一句话，识别情绪标签和置信度，并获得更贴近当前状态的回复。</span></div>
          <div class="calm-card"><b>音视频分析</b><span>上传音频或视频，转写成文字后继续完成情绪分析和陪伴回应。</span></div>
          <div class="calm-card"><b>CSV 批量分析</b><span>面向评论、问卷和反馈数据，批量标注情绪并支持筛选导出。</span></div>
          <div class="calm-card"><b>可视化报告</b><span>展示分布图、趋势图、关键词词云、代表性语句和整体建议。</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
