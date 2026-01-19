import os
import re
from bs4 import BeautifulSoup

base_dir = "d:/업무/matari/챗봇_이스트라/HTML_Conversion"
qna_dir = os.path.join(base_dir, "크롤링_QnA")
selftest_dir = os.path.join(base_dir, "크롤링_selftest_MD")

def get_page_info(folder_path):
    index_path = os.path.join(folder_path, "index.html")
    if not os.path.exists(index_path):
        return None
    
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            title = soup.title.string if soup.title else os.path.basename(folder_path)
            # Clean title
            title = re.sub(r'Untitled_\d+', '', title).strip()
            if not title:
                title = os.path.basename(folder_path)
            return title
    except:
        return os.path.basename(folder_path)

def generate_card(title, link, category):
    badge_color = "bg-blue-100 text-blue-800" if category == "QnA" else "bg-green-100 text-green-800"
    return f"""
            <a href="{link}" class="card group">
                <div class="card-body">
                    <span class="badge {badge_color}">{category}</span>
                    <h3 class="card-title group-hover:text-blue-600 transition-colors">{title}</h3>
                    <div class="card-meta">
                        <span>View Document &rarr;</span>
                    </div>
                </div>
            </a>
    """

html_template_start = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>이스트라 챗봇 지식베이스</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
    <style>
        body {
            font-family: "Pretendard Variable", Pretendard, -apple-system, BlinkMacSystemFont, system-ui, Roboto, "Helvetica Neue", "Segoe UI", "Apple SD Gothic Neo", "Noto Sans KR", "Malgun Gothic", "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", sans-serif;
            background-color: #f3f4f6;
        }
        .card {
            background-color: white;
            border-radius: 0.75rem;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            transition: all 0.3s ease;
            display: flex;
            flex-direction: column;
            height: 100%;
        }
        .card:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }
        .card-body {
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            flex-grow: 1;
        }
        .card-title {
            font-size: 1.125rem;
            font-weight: 600;
            margin-top: 0.75rem;
            margin-bottom: 0.75rem;
            line-height: 1.5;
            color: #111827;
        }
        .card-meta {
            margin-top: auto;
            font-size: 0.875rem;
            color: #6b7280;
            display: flex;
            align-items: center;
        }
        .badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            width: fit-content;
        }
        .section-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #1f2937;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .section-title::before {
            content: '';
            display: block;
            width: 4px;
            height: 24px;
            background-color: #2563eb;
            border-radius: 2px;
        }
    </style>
</head>
<body>
    <header class="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <a href="#" class="flex items-center gap-2 text-xl font-bold text-blue-600">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a10 10 0 1 0 10 10 4 4 0 0 1-5-5 4 4 0 0 1-5-5c0-5.523 4.477-10 10-10z"></path><path d="M8.5 8.5v.01"></path><path d="M16 15.5v.01"></path><path d="M12 12v.01"></path><path d="M11 17a2 2 0 0 1 2 2"></path></svg>
                ESTLA Knowledge Base
            </a>
            <div class="flex-1 max-w-md mx-4">
                <div class="relative">
                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                            <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
                        </svg>
                    </div>
                    <input type="text" id="searchInput" class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm" placeholder="키워드로 검색해보세요 (예: 리모컨, 화면)">
                </div>
            </div>
            <nav class="hidden md:flex gap-6">
                <a href="#section-QnA" class="text-gray-600 hover:text-blue-600 font-medium transition-colors">QnA</a>
                <a href="#section-Selftest" class="text-gray-600 hover:text-blue-600 font-medium transition-colors">Selftest</a>
            </nav>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div id="noResults" class="hidden text-center py-12 text-gray-500">
            검색 결과가 없습니다.
        </div>
"""

html_content = html_template_start

# QnA Section
html_content += '<div id="section-QnA" class="mb-12 section-container"><h2 class="section-title">자주 묻는 질문 (QnA)</h2><div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 card-grid">'
if os.path.exists(qna_dir):
    for folder in sorted(os.listdir(qna_dir)):
        folder_path = os.path.join(qna_dir, folder)
        if os.path.isdir(folder_path):
            title = get_page_info(folder_path)
            if title:
                link = f"./크롤링_QnA/{folder}/index.html"
                html_content += generate_card(title, link, "QnA")
html_content += '</div></div>'

# Selftest Section
html_content += '<div id="section-Selftest" class="section-container"><h2 class="section-title">자가 진단 (Selftest)</h2><div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 card-grid">'
if os.path.exists(selftest_dir):
    for folder in sorted(os.listdir(selftest_dir)):
        folder_path = os.path.join(selftest_dir, folder)
        if os.path.isdir(folder_path):
            title = get_page_info(folder_path)
            if title:
                link = f"./크롤링_selftest_MD/{folder}/index.html"
                html_content += generate_card(title, link, "Selftest")
html_content += '</div></div>'

html_content += """
    </main>
    <footer class="bg-white border-t border-gray-200 mt-12">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 text-center text-gray-500 text-sm">
            &copy; 2024 ESTLA. All rights reserved.
        </div>
    </footer>

    <script>
        const searchInput = document.getElementById('searchInput');
        const cards = document.querySelectorAll('.card');
        const noResults = document.getElementById('noResults');
        const sections = document.querySelectorAll('.section-container');

        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            let hasVisibleCards = false;

            cards.forEach(card => {
                const title = card.querySelector('.card-title').textContent.toLowerCase();
                if (title.includes(searchTerm)) {
                    card.style.display = 'flex';
                    hasVisibleCards = true;
                } else {
                    card.style.display = 'none';
                }
            });

            // Hide empty sections
            sections.forEach(section => {
                const visibleCardsInSection = section.querySelectorAll('.card[style="display: flex"], .card:not([style*="display: none"])');
                if (visibleCardsInSection.length > 0) {
                    section.style.display = 'block';
                } else {
                    section.style.display = 'none';
                }
            });

            if (hasVisibleCards) {
                noResults.classList.add('hidden');
            } else {
                noResults.classList.remove('hidden');
            }
        });
    </script>
</body>
</html>
"""

with open(os.path.join(base_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(html_content)

print("Generated index.html successfully.")
