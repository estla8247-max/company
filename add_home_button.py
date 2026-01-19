import os

base_dir = "d:/업무/matari/챗봇_이스트라/HTML_Conversion"

home_button_html = """
    <!-- Floating Home Button -->
    <a href="../../index.html" style="position: fixed; bottom: 20px; right: 20px; width: 50px; height: 50px; background-color: #2563eb; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); text-decoration: none; transition: transform 0.2s; z-index: 100;" onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
    </a>
</body>
"""

count = 0

for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file == "index.html" and root != base_dir:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if button already exists
                if "Floating Home Button" not in content:
                    new_content = content.replace("</body>", home_button_html)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Added home button to: {file_path}")
                    count += 1
                else:
                    print(f"Home button already exists in: {file_path}")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

print(f"Total files updated: {count}")
