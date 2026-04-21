from __future__ import annotations

import re
from typing import Any, Dict, List

import streamlit as st

from agents.planner_agent import run_planner
from utils.file_parser import parse_uploaded_file
from utils.report_generator import build_report_payload, render_report_json, render_text_summary

st.set_page_config(page_title="SAFE-INTERN", page_icon="🛡️", layout="wide")

st.markdown(
    """
<style>
    .card { padding: 1rem; border-radius: 14px; border: 1px solid #33415544; background: linear-gradient(135deg, #0f172a08, #0284c708); margin-bottom: 0.8rem; }
    .badge { padding: 5px 12px; border-radius: 999px; font-weight: 700; display: inline-block; }
    .safe { background:#dcfce7; color:#166534; }
    .low { background:#fef9c3; color:#854d0e; }
    .medium { background:#fde68a; color:#92400e; }
    .high { background:#fecaca; color:#991b1b; }
    .scam { background:#b91c1c; color:#fff; }
</style>
""",
    unsafe_allow_html=True,
)


RISK_ICON_MAP: Dict[str, str] = {
    "Safe": "✅",
    "Low Risk": "🟡",
    "Medium Risk": "🟠",
    "High Risk": "🔴",
    "Scam Likely": "🚨",
}


def _badge_style(label: str) -> str:
    return {
        "Safe": "badge safe",
        "Low Risk": "badge low",
        "Medium Risk": "badge medium",
        "High Risk": "badge high",
        "Scam Likely": "badge scam",
    }.get(label, "badge low")


def _escape_markdown(value: str) -> str:
    """Escape markdown special chars to safely render highlighted text."""
    escaped = value.replace("\\", "\\\\")
    for ch in ["*", "_", "`", "[", "]", "(", ")", "#", "+", "-", ".", "!"]:
        escaped = escaped.replace(ch, f"\\{ch}")
    return escaped


def highlight_keywords(source_text: str, keyword_hits: List[str]) -> str:
    """Highlight detected scam keywords in source text."""
    if not source_text.strip() or not keyword_hits:
        return _escape_markdown(source_text)
    unique_terms = sorted({kw.strip() for kw in keyword_hits if kw.strip()}, key=len, reverse=True)
    highlighted = source_text
    for term in unique_terms:
        pattern = re.compile(re.escape(term), flags=re.IGNORECASE)
        highlighted = pattern.sub(lambda m: f"**⚠ {m.group(0)}**", highlighted)
    return _escape_markdown(highlighted).replace("\\*\\*⚠ ", "**⚠ ").replace("\\*\\*", "**")


def _flatten_patterns(found: Dict[str, List[str]]) -> List[str]:
    """Render pattern dictionary as compact readable rows."""
    rows = []
    for key, values in found.items():
        if values:
            rows.append(f"{key.replace('_', ' ').title()}: {', '.join(values[:3])}")
    return rows


def _safe_tips() -> List[str]:
    """Return practical anti-scam safety recommendations."""
    return [
        "Never pay any internship registration fee, deposit, or processing charge.",
        "Verify recruiter identity using official company website and domain email.",
        "Do not share Aadhaar, PAN, passport, bank info, OTP, or UPI PIN.",
        "Reject offers with no interview and unrealistic salary promises.",
        "Avoid pressure tactics like 'confirm now', 'limited seats', or 'pay immediately'.",
    ]


def _bucket_patterns(found_patterns: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Group raw pattern keys into user-friendly indicator buckets."""
    buckets = {
        "Detected personal information": ["aadhaar_numbers", "pan_cards", "bank_accounts", "ifsc_codes", "otp_requests"],
        "Suspicious payment indicators": ["upi_ids", "payment_requests", "qr_codes"],
        "Suspicious urgency language": ["urgency_language", "unrealistic_salary"],
        "Suspicious contact methods": ["telegram_usernames", "whatsapp_numbers", "public_domains", "fake_domains", "suspicious_urls"],
    }
    grouped: Dict[str, List[str]] = {}
    for title, keys in buckets.items():
        rows = []
        for key in keys:
            if key in found_patterns:
                rows.append(f"{key.replace('_', ' ').title()}: {', '.join(found_patterns[key][:3])}")
        grouped[title] = rows
    return grouped


st.markdown("## 🛡️ SAFE-INTERN")
st.markdown("### AI-powered internship scam guard")
st.write(
    "Analyze pasted messages, emails, PDFs, screenshots, and offer letters using a resilient "
    "ML + rule engine designed to fail safely when optional dependencies are unavailable."
)

with st.sidebar:
    st.markdown("### Platform Status")
    st.info("CrewAI is intentionally disabled as optional.")
    st.info("Gemini is optional and not required for core analysis.")
    st.markdown("### Example Scam Message")
    st.code("URGENT: Pay ₹1999 registration fee now via UPI to confirm internship seat.")
    st.markdown("### Example Safe Message")
    st.code("Interview scheduled via official company email. No payment requested.")

tab_msg, tab_file, tab_indicators, tab_ml = st.tabs(
    ["Message Analysis", "PDF / Offer Letter Upload", "Scam Indicators Found", "ML Risk Breakdown"]
)

if "input_text" not in st.session_state:
    st.session_state.input_text = ""
if "analysis" not in st.session_state:
    st.session_state.analysis = {}

with tab_msg:
    typed = st.text_area(
        "Paste internship message/email text",
        value=st.session_state.input_text,
        height=250,
        placeholder="Paste suspicious text, offer letter email, chat screenshot text, or job description...",
    )
    st.session_state.input_text = typed
    st.markdown('<div class="card">Supported: pasted messages, emails, offer texts, OCR text.</div>', unsafe_allow_html=True)

with tab_file:
    upload = st.file_uploader(
        "Upload txt/pdf/docx/image/eml",
        type=["txt", "pdf", "docx", "png", "jpg", "jpeg", "webp", "eml"],
    )
    if upload:
        parsed_text, meta = parse_uploaded_file(upload.name, upload.getvalue())
        if meta.get("status") == "ok":
            st.success(f"Parsed {meta.get('type', 'file')} successfully.")
            st.session_state.input_text = parsed_text
            st.text_area("Extracted text preview", parsed_text[:5000], height=220)
        else:
            st.error(meta.get("message", "Could not parse the uploaded file."))

if st.button("Analyze Risk", type="primary"):
    if not st.session_state.input_text.strip():
        st.error("Please paste text or upload a supported file before analysis.")
    else:
        with st.spinner("Running scam risk analysis..."):
            st.session_state.analysis = run_planner({"clean_text": st.session_state.input_text})

analysis = st.session_state.analysis
if analysis:
    ml_result = analysis.get("ml", {})
    pattern_result = analysis.get("patterns", {})
    scoring = analysis.get("scoring", {})
    final_score = int(scoring.get("final_score", 0))
    label = scoring.get("label", "Low Risk")
    confidence = int(scoring.get("confidence", 20))
    ml_percent = int(scoring.get("ml_percent", 0))
    rule_score = int(scoring.get("rule_score", 0))
    found_patterns = pattern_result.get("found_patterns", {})
    reasons = pattern_result.get("reasons", [])
    keyword_hits = pattern_result.get("keyword_hits", [])

    st.markdown("---")
    card_cols = st.columns(5)
    labels = ["Safe", "Low Risk", "Medium Risk", "High Risk", "Scam Likely"]
    for idx, risk_label in enumerate(labels):
        card_cols[idx].markdown(
            f"<div class='card'><b>{RISK_ICON_MAP.get(risk_label, '⚠')} {risk_label}</b></div>",
            unsafe_allow_html=True,
        )

    m1, m2, m3 = st.columns(3)
    m1.metric("Final Risk Score", f"{final_score}/100")
    m1.progress(final_score / 100.0)
    m2.metric("Confidence Score", f"{confidence}%")
    m2.progress(confidence / 100.0)
    m3.markdown(f"<span class='{_badge_style(label)}'>{RISK_ICON_MAP.get(label, '⚠')} {label}</span>", unsafe_allow_html=True)
    m3.caption("Final label from combined ML + rule scoring")

    st.markdown("### Risk Meter")
    st.progress(final_score / 100.0, text=f"{label} ({final_score}%)")

    with tab_indicators:
        st.markdown("### Why this may be risky")
        for reason in reasons[:8]:
            st.warning(reason)
        if not reasons:
            st.success("No strong high-risk indicators detected by rule engine.")
        flat_patterns = _flatten_patterns(found_patterns)
        if flat_patterns:
            st.markdown("### Highlighted scam keywords and patterns")
            for row in flat_patterns:
                st.write(f"- {row}")
        if keyword_hits:
            st.info(f"Keyword hits: {', '.join(keyword_hits)}")

        grouped = _bucket_patterns(found_patterns)
        for group_title, items in grouped.items():
            st.markdown(f"### {group_title}")
            if items:
                for item in items:
                    st.write(f"- {item}")
            else:
                st.caption("No indicators in this section.")

        with st.expander("Raw extracted text (with highlighted scam keywords)"):
            highlighted = highlight_keywords(st.session_state.input_text[:6000], keyword_hits)
            st.markdown(highlighted or "_No extracted text available._")

        st.markdown("### How to stay safe")
        for tip in _safe_tips():
            st.write(f"- {tip}")

    with tab_ml:
        st.markdown("### ML Risk Breakdown")
        ml_breakdown: Dict[str, Any] = {
            "ml_used": ml_result.get("ml_used", False),
            "model_type": ml_result.get("model_type", "N/A"),
            "retrained": ml_result.get("retrained", False),
            "ml_percent": ml_percent,
            "rule_score": rule_score,
            "integrations": analysis.get("integrations", {}),
        }
        st.json(ml_breakdown)

    report = build_report_payload(
        source_text=st.session_state.input_text,
        ml_result=ml_result,
        pattern_result=pattern_result,
        scoring=scoring,
        integrations=analysis.get("integrations", {}),
    )
    st.download_button(
        "Download JSON Report",
        data=render_report_json(report),
        file_name="safe_intern_report.json",
        mime="application/json",
    )
    st.download_button(
        "Download Text Summary",
        data=render_text_summary(report),
        file_name="safe_intern_summary.txt",
        mime="text/plain",
    )

st.markdown("---")
st.caption(
    "Safety disclaimer: SAFE-INTERN provides risk guidance, not legal or financial advice. "
    "Always verify recruiter identity through official channels."
)
