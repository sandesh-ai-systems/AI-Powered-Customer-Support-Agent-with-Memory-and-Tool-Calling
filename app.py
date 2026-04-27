"""Streamlit dashboard for support agents."""

from __future__ import annotations

import os
from html import escape
from typing import Any

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


st.set_page_config(page_title="Support Copilot", layout="wide")

STATUS_BADGES = {
    "open": ("#2563eb", "#dbeafe"),
    "pending": ("#b45309", "#fef3c7"),
    "resolved": ("#047857", "#d1fae5"),
    "closed": ("#475569", "#e2e8f0"),
}

PRIORITY_BADGES = {
    "low": ("#047857", "#d1fae5"),
    "medium": ("#2563eb", "#dbeafe"),
    "high": ("#b45309", "#fef3c7"),
    "urgent": ("#b91c1c", "#fee2e2"),
}


def apply_theme() -> None:
    st.markdown(
        """
        <style>
            :root {
                --surface: #111827;
                --surface-soft: #0f172a;
                --border: #334155;
                --text-muted: #94a3b8;
                --brand: #14b8a6;
                --brand-strong: #0d9488;
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(20, 184, 166, 0.20), transparent 34rem),
                    radial-gradient(circle at bottom right, rgba(59, 130, 246, 0.14), transparent 30rem),
                    linear-gradient(180deg, #020617 0%, #0f172a 48%, #111827 100%);
            }

            [data-testid="stHeader"] {
                background: rgba(2, 6, 23, 0.72);
                backdrop-filter: blur(12px);
            }

            .block-container {
                padding-top: 1.6rem;
                padding-bottom: 3rem;
                max-width: 1500px;
            }

            .app-hero {
                padding: 1.15rem 1.25rem;
                border: 1px solid rgba(45, 212, 191, 0.20);
                border-radius: 14px;
                background: linear-gradient(135deg, rgba(15,23,42,0.96), rgba(17,24,39,0.86));
                box-shadow: 0 18px 48px rgba(0, 0, 0, 0.28);
                margin-bottom: 1rem;
            }

            .app-hero h1 {
                font-size: 2rem;
                line-height: 1.1;
                margin: 0 0 0.25rem 0;
                letter-spacing: 0;
                color: #f8fafc;
            }

            .app-hero p {
                margin: 0;
                color: var(--text-muted);
                font-size: 0.98rem;
            }

            .section-title {
                margin: 0.25rem 0 0.75rem 0;
                color: #f8fafc;
                font-size: 1.08rem;
                font-weight: 700;
            }

            .muted {
                color: var(--text-muted);
                font-size: 0.92rem;
            }

            .badge {
                display: inline-flex;
                align-items: center;
                min-height: 1.65rem;
                padding: 0.18rem 0.62rem;
                border-radius: 999px;
                font-size: 0.78rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0;
                white-space: nowrap;
            }

            .ticket-heading {
                font-size: 1.25rem;
                font-weight: 750;
                color: #f8fafc;
                margin: 0.2rem 0 0.4rem 0;
            }

            .ticket-meta {
                color: var(--text-muted);
                font-size: 0.9rem;
                margin-bottom: 0.85rem;
            }

            div[data-testid="stMetric"] {
                background: rgba(15, 23, 42, 0.72);
                border: 1px solid var(--border);
                border-radius: 12px;
                padding: 0.7rem 0.8rem;
            }

            .stButton > button {
                border-radius: 10px;
                min-height: 2.65rem;
                font-weight: 700;
                border-color: #334155;
            }

            .stButton > button[kind="primary"] {
                background: var(--brand);
                border-color: var(--brand);
            }

            .stButton > button[kind="primary"]:hover {
                background: var(--brand-strong);
                border-color: var(--brand-strong);
            }

            textarea, input, div[data-baseweb="select"] > div {
                border-radius: 10px !important;
            }

            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #020617 0%, #0f172a 100%);
                border-right: 1px solid var(--border);
            }

             [data-testid="stSidebar"] * {
                color: #f8fafc;
            }

            [data-testid="stSidebar"] code {
                color: #e5edf7 !important;
                background: #111827 !important;
                border-radius: 8px;
            }

            [data-testid="stVerticalBlockBorderWrapper"] {
                background: rgba(15, 23, 42, 0.78);
                border-color: rgba(51, 65, 85, 0.88);
                box-shadow: 0 18px 48px rgba(0, 0, 0, 0.28);
            }

            [data-testid="stForm"] {
                background: transparent;
                border: 0;
                box-shadow: none;
            }

            [data-testid="stForm"] [data-testid="stVerticalBlockBorderWrapper"] {
                background: transparent;
                border: 0;
                box-shadow: none;
            }

            label,
            [data-testid="stWidgetLabel"],
            [data-testid="stWidgetLabel"] p {
                color: #cbd5e1 !important;
                font-weight: 650 !important;
            }

            .stTextInput input,
            .stTextArea textarea,
            .stSelectbox div[data-baseweb="select"] > div {
                background-color: #111827 !important;
                color: #f8fafc !important;
                border: 1px solid #334155 !important;
                box-shadow: none !important;
            }

            .stTextInput input::placeholder,
            .stTextArea textarea::placeholder {
                color: #94a3b8 !important;
                opacity: 1 !important;
            }

            .stSelectbox div[data-baseweb="select"] span {
                color: #f8fafc !important;
            }

            .stCheckbox label,
            .stCheckbox p {
                color: #cbd5e1 !important;
                font-weight: 650 !important;
            }

            .stCheckbox [data-testid="stWidgetLabel"] {
                color: #cbd5e1 !important;
            }

            .stButton > button {
                background: #111827;
                color: #f8fafc;
            }

            .stCodeBlock pre,
            .stCodeBlock code,
            [data-testid="stCodeBlock"] pre,
            [data-testid="stCodeBlock"] code {
                color: #f8fafc !important;
                background: #111827 !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_badge(label: str, palette: dict[str, tuple[str, str]]) -> str:
    color, background = palette.get(label.lower(), ("#475569", "#e2e8f0"))
    return (
        f'<span class="badge" style="color:{color}; background:{background};">'
        f"{escape(label)}</span>"
    )


def section_title(label: str) -> None:
    st.markdown(f'<div class="section-title">{label}</div>', unsafe_allow_html=True)


apply_theme()
st.markdown(
    """
    <div class="app-hero">
        <h1>Support Copilot Dashboard</h1>
        <p>Create tickets, generate grounded replies, inspect tool traces, and save accepted resolutions into memory.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=10)
def fetch_tickets() -> list[dict[str, Any]]:
    response = requests.get(f"{API_BASE_URL}/api/tickets", timeout=20)
    response.raise_for_status()
    return response.json()


def fetch_draft(ticket_id: int) -> dict[str, Any] | None:
    response = requests.get(f"{API_BASE_URL}/api/drafts/{ticket_id}", timeout=20)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()


def _extract_api_error(response: requests.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return response.text or response.reason or "Unknown API error"

    detail = payload.get("detail")
    if isinstance(detail, list):
        parts = []
        for item in detail:
            if isinstance(item, dict):
                loc = ".".join(str(p) for p in item.get("loc", []))
                msg = item.get("msg", "validation error")
                parts.append(f"{loc}: {msg}" if loc else msg)
            else:
                parts.append(str(item))
        return "; ".join(parts)
    if detail:
        return str(detail)
    return str(payload)


def create_ticket(payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(f"{API_BASE_URL}/api/tickets", json=payload, timeout=20)
    if response.status_code >= 400:
        raise RuntimeError(_extract_api_error(response))
    fetch_tickets.clear()
    return response.json()


def trigger_draft(ticket_id: int) -> dict[str, Any]:
    response = requests.post(
        f"{API_BASE_URL}/api/tickets/{ticket_id}/generate-draft",
        timeout=60,
    )
    if response.status_code >= 400:
        raise RuntimeError(_extract_api_error(response))
    return response.json()["draft"]


def update_draft(draft_id: int, content: str, status: str) -> dict[str, Any]:
    response = requests.patch(
        f"{API_BASE_URL}/api/drafts/{draft_id}",
        json={"content": content, "status": status},
        timeout=60,
    )
    if response.status_code >= 400:
        raise RuntimeError(_extract_api_error(response))
    fetch_tickets.clear()
    return response.json()


def ingest_knowledge(clear_existing: bool) -> dict[str, Any]:
    response = requests.post(
        f"{API_BASE_URL}/api/knowledge/ingest",
        json={"clear_existing": clear_existing},
        timeout=60,
    )
    if response.status_code >= 400:
        raise RuntimeError(_extract_api_error(response))
    return response.json()


def search_memory(customer_id: int, query: str, limit: int = 8) -> list[dict[str, Any]]:
    response = requests.get(
        f"{API_BASE_URL}/api/customers/{customer_id}/memory-search",
        params={"query": query, "limit": limit},
        timeout=20,
    )
    if response.status_code >= 400:
        raise RuntimeError(_extract_api_error(response))
    payload = response.json()
    return payload.get("results", [])


def render_context(context: dict[str, Any] | None) -> None:
    if not context:
        st.info("No context captured for this draft.")
        return

    if context.get("version") != 2:
        st.json(context)
        return

    signals = context.get("signals") or {}
    memory_hits = context.get("memory_hits") or []
    knowledge_hits = context.get("knowledge_hits") or []
    tool_calls = context.get("tool_calls") or []
    highlights = context.get("highlights") or {}

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Memory Hits", signals.get("memory_hit_count", len(memory_hits)))
    c2.metric("KB Hits", signals.get("knowledge_hit_count", len(knowledge_hits)))
    c3.metric("Tool Calls", signals.get("tool_call_count", len(tool_calls)))
    c4.metric(
        "Tool Errors",
        signals.get(
            "tool_error_count",
            len([call for call in tool_calls if call.get("status") != "ok"]),
        ),
    )

    sources = signals.get("knowledge_sources") or []
    if sources:
        st.caption(f"Knowledge sources: {', '.join(sources)}")

    if any(highlights.get(key) for key in ("memory", "knowledge", "tools")):
        st.markdown("**Highlights**")
        for label, key in (
            ("Memory", "memory"),
            ("Knowledge", "knowledge"),
            ("Tools", "tools"),
        ):
            values = [item for item in (highlights.get(key) or []) if item]
            if values:
                st.write(f"{label}:")
                for item in values:
                    st.write(f"- {item}")

    if tool_calls:
        st.markdown("**Tool Calls**")
        rows = [
            {
                "Tool": call.get("tool_name", "unknown"),
                "Status": call.get("status", "unknown"),
                "Summary": call.get("summary") or call.get("output_text", ""),
            }
            for call in tool_calls
        ]
        st.dataframe(rows, use_container_width=True, hide_index=True)

        for index, call in enumerate(tool_calls, start=1):
            title = (
                f"{index}. {call.get('tool_name', 'unknown')} "
                f"({call.get('status', 'unknown')})"
            )
            with st.expander(title):
                st.caption("Arguments")
                st.json(call.get("arguments") or {})
                output = call.get("output")
                if output:
                    st.caption("Structured Output")
                    st.json(output)
                else:
                    st.caption("Raw Output")
                    st.code(call.get("output_text", ""), language="text")

    with st.expander("Detailed Memory Hits"):
        st.json(memory_hits)
    with st.expander("Detailed Knowledge Hits"):
        st.json(knowledge_hits)

    errors = context.get("errors") or []
    if errors:
        with st.expander("Context Errors"):
            for err in errors:
                st.error(err)


with st.sidebar:
    st.markdown("### Workspace")
    st.caption("API endpoint")
    st.code(API_BASE_URL, language="text")

    if st.button("Ingest Knowledge Base", use_container_width=True):
        try:
            result = ingest_knowledge(clear_existing=False)
            st.success(
                f"Indexed {result['files_indexed']} files / {result['chunks_indexed']} chunks"
            )
        except Exception as exc:
            st.error(f"Knowledge ingest failed: {exc}")


with st.container(border=True):
    section_title("Create Ticket")
    with st.form("create_ticket_form"):
        col1, col2 = st.columns(2)
        with col1:
            customer_email = st.text_input("Customer Email", placeholder="alex@acme.io")
            customer_name = st.text_input("Customer Name", placeholder="Alex Rivera")
        with col2:
            customer_company = st.text_input("Company", placeholder="Acme Labs")
            priority = st.selectbox(
                "Priority",
                ["low", "medium", "high", "urgent"],
                index=1,
            )

        subject = st.text_input("Subject")
        description = st.text_area("Description", height=120)
        form_actions = st.columns([1, 1, 2])
        with form_actions[0]:
            auto_generate = st.checkbox("Auto-generate", value=True)
        with form_actions[1]:
            submitted = st.form_submit_button("Create Ticket", use_container_width=True)

        if submitted:
            if not customer_email or not subject or not description:
                st.warning("Email, subject, and description are required.")
            elif len(subject.strip()) < 3:
                st.warning("Subject must be at least 3 characters.")
            elif len(description.strip()) < 10:
                st.warning("Description must be at least 10 characters.")
            else:
                try:
                    created = create_ticket(
                        {
                            "customer_email": customer_email,
                            "customer_name": customer_name or None,
                            "customer_company": customer_company or None,
                            "subject": subject,
                            "description": description,
                            "priority": priority,
                            "auto_generate": auto_generate,
                        }
                    )
                    st.success(f"Ticket #{created['id']} created")
                except Exception as exc:
                    st.error(f"Ticket creation failed: {exc}")

st.divider()
section_title("Tickets")

try:
    tickets = fetch_tickets()
except Exception as exc:
    tickets = []
    st.error(f"Could not load tickets: {exc}")

if not tickets:
    st.info("No tickets yet. Create one above or run seed_data.py")
else:
    labels = [
        f"#{t['id']} | {t['status']} | {t['customer_email']} | {t['subject']}"
        for t in tickets
    ]
    selected_label = st.selectbox(
        "Select ticket",
        labels,
        label_visibility="collapsed",
    )
    selected_ticket = tickets[labels.index(selected_label)]

    left, right = st.columns([0.92, 1.35], gap="large")

    with left:
        with st.container(border=True):
            ticket_status = str(selected_ticket["status"])
            ticket_priority = str(selected_ticket["priority"])
            st.markdown(
                f"""
                <div class="ticket-meta">Ticket #{selected_ticket['id']}</div>
                <div class="ticket-heading">{escape(str(selected_ticket['subject']))}</div>
                {render_badge(ticket_status, STATUS_BADGES)}
                {render_badge(ticket_priority, PRIORITY_BADGES)}
                """,
                unsafe_allow_html=True,
            )
            st.write(selected_ticket["description"])

            info_a, info_b = st.columns(2)
            with info_a:
                st.caption("Customer")
                st.write(selected_ticket["customer_email"])
                st.write(selected_ticket.get("customer_name") or "-")
            with info_b:
                st.caption("Company")
                st.write(selected_ticket.get("customer_company") or "-")
                st.caption("Created")
                st.write(selected_ticket.get("created_at") or "-")

            if st.button("Generate Draft", type="primary", use_container_width=True):
                try:
                    new_draft = trigger_draft(selected_ticket["id"])
                    st.session_state[f"draft_{selected_ticket['id']}"] = new_draft
                    st.success("Draft generated")
                except Exception as exc:
                    st.error(f"Draft generation failed: {exc}")

        with st.container(border=True):
            section_title("Memory Probe")
            probe_query = st.text_input(
                "Search customer memory by entities/issues",
                value=f"{selected_ticket['subject']} {selected_ticket['priority']}",
                key=f"memory_probe_{selected_ticket['id']}",
            )
            if st.button("Run Memory Probe", use_container_width=True):
                try:
                    hits = search_memory(selected_ticket["customer_id"], probe_query)
                    if not hits:
                        st.info("No memory hits for this query yet.")
                    else:
                        st.success(f"Found {len(hits)} memory hit(s).")
                        for idx, hit in enumerate(hits, start=1):
                            with st.expander(f"Memory hit {idx}"):
                                st.write(hit.get("memory", ""))
                                metadata = hit.get("metadata") or {}
                                if metadata:
                                    st.caption("Metadata")
                                    st.json(metadata)
                except Exception as exc:
                    st.error(f"Memory probe failed: {exc}")

    with right:
        draft_data = st.session_state.get(f"draft_{selected_ticket['id']}") or fetch_draft(
            selected_ticket["id"]
        )

        with st.container(border=True):
            section_title("Draft Workspace")
            if not draft_data:
                st.info("No draft exists for this ticket yet. Generate one to start editing.")
            else:
                if draft_data.get("status") == "failed":
                    st.warning(
                        "Latest draft attempt failed. Check API key configuration and retry generation."
                    )

                edited_content = st.text_area(
                    "Edit before sending",
                    value=draft_data["content"],
                    height=260,
                    key=f"draft_content_{draft_data['id']}",
                )

                c3, c4 = st.columns(2)
                with c3:
                    if st.button("Accept Draft", type="primary", use_container_width=True):
                        try:
                            updated = update_draft(draft_data["id"], edited_content, "accepted")
                            st.session_state[f"draft_{selected_ticket['id']}"] = updated
                            st.success("Draft accepted and memory updated")
                        except Exception as exc:
                            st.error(f"Failed to accept draft: {exc}")

                with c4:
                    if st.button("Discard Draft", use_container_width=True):
                        try:
                            updated = update_draft(draft_data["id"], edited_content, "discarded")
                            st.session_state[f"draft_{selected_ticket['id']}"] = updated
                            st.info("Draft discarded")
                        except Exception as exc:
                            st.error(f"Failed to discard draft: {exc}")

        if draft_data:
            with st.container(border=True):
                section_title("Context Used")
                render_context(draft_data.get("context_used"))
