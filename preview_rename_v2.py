import os
import re
from bs4 import BeautifulSoup

base_dir = "d:/업무/matari/챗봇_이스트라/HTML_Conversion/크롤링_QnA"

def get_new_title(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            
            # Find the first paragraph that has meaningful content
            for p in soup.find_all('p'):
                text = p.get_text().strip()
                # Remove ZWSP and other invisible chars
                text = re.sub(r'[\u200b\ufeff]', '', text)
                
                # Check if text has at least some Korean or English characters
                if text and len(text) > 2 and not text.startswith("Untitled"):
                    # Use the first sentence or up to 50 chars
                    return text.split('\n')[0][:50].strip()
            
            return None
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

print("Proposed Renames:")
for folder_name in os.listdir(base_dir):
    if folder_name.startswith("Untitled_"):
        folder_path = os.path.join(base_dir, folder_name)
        index_path = os.path.join(folder_path, "index.html")
        
        if os.path.exists(index_path):
            new_title = get_new_title(index_path)
            if new_title:
                clean_title = re.sub(r'[\\/*?:"<>|]', "", new_title)
                print(f"'{folder_name}' -> '{clean_title}'")
            else:
                print(f"'{folder_name}' -> ??? (Could not extract title)")
