import os
import re
import shutil
from bs4 import BeautifulSoup

base_dir = "d:/업무/matari/챗봇_이스트라/HTML_Conversion/크롤링_QnA"

def get_new_title(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            for p in soup.find_all('p'):
                text = p.get_text().strip()
                text = re.sub(r'[\u200b\ufeff]', '', text)
                if text and len(text) > 2 and not text.startswith("Untitled"):
                    return text.split('\n')[0][:50].strip()
            return None
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def update_html_title(file_path, new_title):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace title tag
        content = re.sub(r'<title>.*?</title>', f'<title>{new_title}</title>', content)
        # Replace h1 tag
        content = re.sub(r'<h1>Untitled_.*?</h1>', f'<h1>{new_title}</h1>', content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

print("Renaming...")
for folder_name in os.listdir(base_dir):
    if folder_name.startswith("Untitled_"):
        folder_path = os.path.join(base_dir, folder_name)
        index_path = os.path.join(folder_path, "index.html")
        
        if os.path.exists(index_path):
            new_title = get_new_title(index_path)
            if new_title:
                clean_title = re.sub(r'[\\/*?:"<>|]', "", new_title)
                new_folder_path = os.path.join(base_dir, clean_title)
                
                # Rename directory
                try:
                    if os.path.exists(new_folder_path):
                        print(f"Skipping {folder_name} -> {clean_title} (Target exists)")
                    else:
                        os.rename(folder_path, new_folder_path)
                        # Update HTML content
                        new_index_path = os.path.join(new_folder_path, "index.html")
                        update_html_title(new_index_path, clean_title)
                        print(f"Renamed: {folder_name} -> {clean_title}")
                except Exception as e:
                    print(f"Error renaming {folder_name}: {e}")
