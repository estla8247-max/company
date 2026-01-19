import os
import shutil
import re

base_dir = "d:/업무/matari/챗봇_이스트라/HTML_Conversion/크롤링_QnA"

renames = {
    "Untitled_1768746923": "LED TV란",
    "Untitled_1768746925": "이미지 답변_3189442",
    "Untitled_1768746927": "이미지 답변_3108465"
}

def update_html_title(file_path, new_title):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = re.sub(r'<title>.*?</title>', f'<title>{new_title}</title>', content)
        content = re.sub(r'<h1>Untitled_.*?</h1>', f'<h1>{new_title}</h1>', content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

for old_name, new_name in renames.items():
    old_path = os.path.join(base_dir, old_name)
    new_path = os.path.join(base_dir, new_name)
    
    if os.path.exists(old_path):
        try:
            if os.path.exists(new_path):
                print(f"Target {new_name} already exists. Skipping.")
            else:
                os.rename(old_path, new_path)
                update_html_title(os.path.join(new_path, "index.html"), new_name)
                print(f"Renamed {old_name} -> {new_name}")
        except Exception as e:
            print(f"Error renaming {old_name}: {e}")
    else:
        print(f"Source {old_name} not found.")
