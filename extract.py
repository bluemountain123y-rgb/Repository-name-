import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    # PDFを開く
    doc = fitz.open(pdf_path)
    all_text = ""
    
    # 全ページからテキストを抽出
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        all_text += f"\n--- {page_num + 1}ページ ---\n"
        all_text += page.get_text()
        
    return all_text

# ★ここが重要！ファイル名を定義します
filename = "arch_exam_questions.pdf"

# 定義したfilenameを使ってテキストを抽出
text = extract_text_from_pdf(filename)

# 画面に表示
print(text)

# テキストファイルとして保存
with open("extracted_text.txt", "w", encoding="utf-8") as f:
    f.write(text)