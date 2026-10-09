import streamlit as st
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="File Manager Pro",
    page_icon="📁",
    layout="wide",
)

# All files live inside this folder (keeps the app safe and tidy)
BASE_DIR = Path("file_storage")
BASE_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem; max-width: 1200px;}

    .hero {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
        padding: 2.2rem 2.5rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.35);
    }
    .hero h1 {margin: 0; font-size: 2.3rem; font-weight: 800; color: white;}
    .hero p {margin: .4rem 0 0 0; opacity: .92; font-size: 1.05rem;}

    .stat-card {
        background: linear-gradient(145deg, #1e1b4b, #312e81);
        border: 1px solid rgba(255,255,255,.08);
        border-radius: 16px;
        padding: 1.1rem 1.3rem;
        color: white;
        box-shadow: 0 6px 18px rgba(0,0,0,.18);
    }
    .stat-card .label {font-size: .8rem; text-transform: uppercase; letter-spacing: .08em; opacity: .7;}
    .stat-card .value {font-size: 1.7rem; font-weight: 700; margin-top: .2rem;}

    .section-title {font-size: 1.35rem; font-weight: 700; margin-bottom: .2rem;}
    .section-sub {opacity: .65; margin-bottom: 1rem;}

    .file-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: .65rem .9rem; margin-bottom: .45rem;
        border-radius: 12px;
        background: rgba(99,102,241,.08);
        border: 1px solid rgba(99,102,241,.18);
        font-size: .92rem;
    }
    .file-row .name {font-weight: 600;}
    .file-row .meta {opacity: .6; font-size: .78rem;}

    div.stButton > button {
        border-radius: 12px;
        font-weight: 600;
        padding: .55rem 1.4rem;
        border: none;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        transition: transform .15s ease, box-shadow .15s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(99,102,241,.4);
        color: white;
    }
    .footer {text-align:center; opacity:.5; margin-top:2.5rem; font-size:.85rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def safe_path(name: str):
    """Return a path inside BASE_DIR, stripping any folder components."""
    name = (name or "").strip()
    if not name:
        return None
    clean = Path(name).name
    if clean in ("", ".", ".."):
        return None
    return BASE_DIR / clean


def human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def list_files():
    files = [p for p in BASE_DIR.iterdir() if p.is_file()]
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)


def stat_card(label: str, value: str):
    st.markdown(
        f"""<div class="stat-card"><div class="label">{label}</div>
        <div class="value">{value}</div></div>""",
        unsafe_allow_html=True,
    )


def section(title: str, subtitle: str):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">{subtitle}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Operations (same logic as the original CLI version)
# ---------------------------------------------------------------------------
def create_view():
    section("✨ Create a File", "Give it a name, add some content, and save.")
    name = st.text_input("File name", placeholder="notes.txt")
    data = st.text_area("File content", height=220, placeholder="Start typing here...")

    if st.button("Create File", key="create_btn"):
        path = safe_path(name)
        if path is None:
            st.warning("Please enter a valid file name.")
        elif path.exists():
            st.error(f"❌ A file named **{path.name}** already exists.")
        else:
            try:
                path.write_text(data, encoding="utf-8")
                st.success(f"✅ File **{path.name}** created successfully!")
                st.balloons()
            except Exception as err:
                st.error(f"An error occurred: {err}")


def read_view():
    section("📖 Read a File", "Pick a file to view its content.")
    files = list_files()
    if not files:
        st.info("No files yet. Create one first!")
        return

    selected = st.selectbox("Choose a file", [f.name for f in files])
    path = safe_path(selected)

    if path and path.exists():
        try:
            content = path.read_text(encoding="utf-8")
            info = path.stat()
            c1, c2 = st.columns(2)
            c1.metric("Size", human_size(info.st_size))
            c2.metric("Last modified", datetime.fromtimestamp(info.st_mtime).strftime("%d %b %Y, %H:%M"))
            st.text_area("Content", content, height=280, disabled=True)
            st.download_button("⬇️ Download file", content, file_name=path.name)
        except UnicodeDecodeError:
            st.error("This file is not a readable text file.")
        except Exception as err:
            st.error(f"An error occurred: {err}")
    else:
        st.error("No such file exists.")


def update_view():
    section("✏️ Update a File", "Rename it, append to it, or overwrite it.")
    files = list_files()
    if not files:
        st.info("No files yet. Create one first!")
        return

    selected = st.selectbox("Choose a file", [f.name for f in files], key="upd_select")
    path = safe_path(selected)
    operation = st.radio(
        "Operation",
        ["Rename file", "Append content", "Overwrite content"],
        horizontal=True,
    )

    try:
        if operation == "Rename file":
            new_name = st.text_input("New file name", placeholder="new_name.txt")
            if st.button("Rename", key="rename_btn"):
                new_path = safe_path(new_name)
                if new_path is None:
                    st.warning("Please enter a valid new name.")
                elif new_path.exists():
                    st.error("❌ A file with that name already exists.")
                else:
                    path.rename(new_path)
                    st.success(f"✅ Renamed to **{new_path.name}**")
                    st.rerun() if False else None

        elif operation == "Append content":
            data = st.text_area("Text to append", height=180)
            if st.button("Append", key="append_btn"):
                with open(path, "a", encoding="utf-8") as fs:
                    fs.write("\n" + data)
                st.success("✅ Content appended successfully!")

        else:
            data = st.text_area("New content (replaces everything)", height=180)
            if st.button("Overwrite", key="overwrite_btn"):
                path.write_text(data, encoding="utf-8")
                st.success("✅ File overwritten successfully!")
    except Exception as err:
        st.error(f"An error occurred: {err}")


def delete_view():
    section("🗑️ Delete a File", "This action cannot be undone.")
    files = list_files()
    if not files:
        st.info("No files to delete.")
        return

    selected = st.selectbox("Choose a file", [f.name for f in files], key="del_select")
    confirm = st.checkbox(f"Yes, I want to permanently delete **{selected}**")

    if st.button("Delete File", key="delete_btn"):
        if not confirm:
            st.warning("Please tick the confirmation box first.")
        else:
            try:
                safe_path(selected).unlink()
                st.success("🗑️ File deleted successfully!")
            except Exception as err:
                st.error(f"An error occurred: {err}")


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>📁 File Manager Pro</h1>
        <p>Create, read, update and delete files — beautifully, in your browser.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## 🧭 Menu")
    menu = st.radio(
        "Choose an action",
        ["✨ Create", "📖 Read", "✏️ Update", "🗑️ Delete"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("Built with Python & Streamlit")

# Stats row (computed fresh each run)
files = list_files()
total_size = sum(f.stat().st_size for f in files)
latest = (
    datetime.fromtimestamp(files[0].stat().st_mtime).strftime("%d %b, %H:%M")
    if files else "—"
)

s1, s2, s3 = st.columns(3)
with s1:
    stat_card("Total files", str(len(files)))
with s2:
    stat_card("Storage used", human_size(total_size))
with s3:
    stat_card("Last activity", latest)

st.write("")

main_col, side_col = st.columns([2, 1], gap="large")

with main_col:
    if menu == "✨ Create":
        create_view()
    elif menu == "📖 Read":
        read_view()
    elif menu == "✏️ Update":
        update_view()
    else:
        delete_view()

with side_col:
    section("📂 Your Files", "Most recently modified first")
    current = list_files()
    if not current:
        st.caption("Nothing here yet.")
    else:
        for f in current[:12]:
            info = f.stat()
            st.markdown(
                f"""<div class="file-row">
                <div><div class="name">📄 {f.name}</div>
                <div class="meta">{datetime.fromtimestamp(info.st_mtime).strftime('%d %b %Y, %H:%M')}</div></div>
                <div class="meta">{human_size(info.st_size)}</div></div>""",
                unsafe_allow_html=True,
            )

st.markdown(
    '<div class="footer">Made with ❤️ using Python & Streamlit</div>',
    unsafe_allow_html=True,
)