import os
import re
from bs4 import BeautifulSoup

base_dir = "d:/업무/matari/챗봇_이스트라/HTML_Conversion/크롤링_QnA"

def get_new_title(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            
            # Find the first paragraph that is not empty and not just whitespace
            for p in soup.find_all('p'):
                text = p.get_text().strip()
                if text and not text.startswith("Untitled"):
                    # Use the first sentence or up to 30 chars
                    return text.split('\n')[0][:50].strip()
            
            # If no p tag, try to infer from content?
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
                # Clean filename
                clean_title = re.sub(r'[\\/*?:"<>|]', "", new_title)
                print(f"'{folder_name}' -> '{clean_title}'")
            else:
                print(f"'{folder_name}' -> ??? (Could not extract title)")
