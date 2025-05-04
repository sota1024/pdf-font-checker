import streamlit as st
import fitz  # PyMuPDF
import zipfile
import tempfile
from pathlib import Path

st.title("📂 PDFフォントチェック（簡易版）")

uploaded_files = st.file_uploader(
    "PDF または ZIP をアップロードしてください",
    type=["pdf", "zip"],
    accept_multiple_files=True
)

# ファイル解凍＆抽出
def extract_files(uploaded, temp_dir_path):
    extracted_paths = []
    for file in uploaded:
        if file.name.endswith(".zip"):
            with zipfile.ZipFile(file) as zip_ref:
                zip_ref.extractall(temp_dir_path)
                extracted_paths.extend(Path(temp_dir_path).rglob("*.pdf"))
        elif file.name.endswith(".pdf"):
            path = Path(temp_dir_path) / file.name
            with open(path, "wb") as f:
                f.write(file.read())
            extracted_paths.append(path)
    return extracted_paths

# フォントの有無を確認
def check_fonts(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            if page.get_fonts():  # 1ページでもフォントが見つかればOK
                return True
        return False
    except:
        return False

# メイン処理
if uploaded_files:
    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_paths = extract_files(uploaded_files, temp_dir)

        # ファイル情報をまとめる
        file_infos = [{
            "path": p,
            "filename": p.name,
            "has_fonts": check_fonts(p)
        } for p in pdf_paths]

        # 並び順選択
        sort_option = st.selectbox(
            "並び順を選んでください",
            ("入力順", "ファイル名順", "チェック有無（フォントなし優先）")
        )

        if sort_option == "ファイル名順":
            file_infos.sort(key=lambda x: x["filename"].lower())
        elif sort_option == "チェック有無（フォントなし優先）":
            file_infos.sort(key=lambda x: not x["has_fonts"], reverse=True)

        # 表示（チェック状態：フォントなし = True）
        st.subheader("🗂 ファイル一覧")
        for info in file_infos:
            st.checkbox(
                label=info["filename"],
                value=not info["has_fonts"],
                key=f"checkbox_{info['filename']}"
            )
