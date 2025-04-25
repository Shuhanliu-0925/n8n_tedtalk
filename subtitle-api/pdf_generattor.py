from fpdf import FPDF, HTMLMixin
from PIL import Image
from io import BytesIO
import requests
import json
import os
import re

class PDF(FPDF, HTMLMixin):
    def header(self):
        if self.page_no() == 1:
            self.set_font("DejaVu", "B", 16)
            self.cell(0, 10, "TED TALK", new_x="LMARGIN", new_y="NEXT", align="C")
            self.ln(2)

    def add_title(self, title):
        cleaned_title = title.split("|")[0].strip()
        self.set_font("DejaVu", "B", 14)
        self.multi_cell(0, 8, cleaned_title, align="C")
        self.ln(3)

    def add_image(self, url, video_url=None):
        url = url.replace("vi_webp", "vi").replace(".webp", ".jpg")
        response = requests.get(url)
        img = Image.open(BytesIO(response.content)).convert("RGB")

        w, h = img.size
        aspect_ratio = h / w
        new_width = 100
        new_height = int(new_width * aspect_ratio)

        img_path = "thumbnail_temp.jpg"
        img.save(img_path, format="JPEG")

        self.image(img_path, x=(210 - new_width) / 2, w=new_width, h=new_height, link=video_url)
        self.ln(6)  # 圖片下方間距縮小

    def add_content(self, content):
        self.set_font("DejaVu", "", 11)
        paragraphs = content.strip().split("\n")

        for p in paragraphs:
            if p.strip():  # 避免空段
                self.multi_cell(0, 6, p.strip(), align="J")  # J = justify
                self.ln(4)  # 段落間距


    def add_vocab_section(self, vocab_text):
        self.add_page()
        self.set_font("DejaVu", "B", 12)
        self.cell(0, 10, "Vocabulary Section", new_x="LMARGIN", new_y="NEXT")
        self.set_font("DejaVu", "", 11)
        self.multi_cell(0, 6, vocab_text.strip())
        self.ln(5)

def split_tasks(content):
    task1_start = content.find("Task 1:")
    task2_start = content.find("Task 2:")

    if task1_start == -1 or task2_start == -1:
        return content, ""

    paragraph = content[task1_start + len("Task 1: Paragraph"):task2_start].strip()
    vocab = content[task2_start + len("Task 2: Vocabulary Teaching"):].strip()
    return paragraph, vocab

def sanitize_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "_", title.split("|")[0].strip())

# 假設你想清除所有欄位中的 ### 和 ** 標記
def clean_markdown(text):
    if not isinstance(text, str):
        return text
    text = re.sub(r'\*{1,2}', '', text)     # 移除 * 和 ** 標記
    text = re.sub(r'#{1,6}\s*', '', text)   # 移除 # 開頭的 Markdown 標題
    return text

def main():
    with open("temp/merged_result.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    data["content"] = clean_markdown(data.get("content", ""))
    paragraph, vocab = split_tasks(data["content"])
    filename = sanitize_filename(data["title"]) + ".pdf"

    output_dir = "pdf"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)  # 底部邊距
    pdf.set_margins(left=25, top=20, right=25)     # 設定左右與上方邊距
    pdf.add_font("DejaVu", "", "font/DejaVuSans.ttf")
    pdf.add_font("DejaVu", "B", "font/DejaVuSans-Bold.ttf")

    pdf.add_page()
    pdf.add_title(data["title"])
    pdf.add_image(data["thumbnail_url"], video_url=data.get("video_url"))
    pdf.add_content(paragraph)
    pdf.add_vocab_section(vocab)

    pdf.output(output_path)

if __name__ == "__main__":
    main()
