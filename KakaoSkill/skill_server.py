import os
import urllib.parse
import re
import difflib
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import asyncio
import httpx

from fastapi.responses import FileResponse
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
# Determine the absolute path to the directory containing this script
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(CURRENT_DIR, "..", "HTML_Conversion")

if not os.path.exists(BASE_DIR):
    BASE_DIR = os.path.join(CURRENT_DIR, "HTML_Conversion")

RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8081")
HOST_BASE_URL = f"{RENDER_EXTERNAL_URL}/static"

# --- Data Models ---

class UserRequest(BaseModel):
    timezone: str
    params: Dict[str, str]
    block: Dict[str, str]
    utterance: str
    lang: Optional[str] = None
    user: Optional[Dict[str, Any]] = None

class Action(BaseModel):
    name: str
    clientExtra: Optional[Dict[str, Any]] = None
    params: Dict[str, str]
    id: str
    detailParams: Dict[str, Any]

class KakaoRequest(BaseModel):
    intent: Dict[str, Any]
    userRequest: UserRequest
    bot: Dict[str, Any]
    action: Action
    contexts: List[Any]

# --- Content Indexer ---

class ContentIndexer:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.index = []
        self.reload_index()

    def extract_summary(self, file_path):
        """
        Extracts a brief summary from the HTML file.
        It reads the file, strips HTML tags, and returns the first 800 chars.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Remove style and script tags first
                content = re.sub(r'<style.*?>.*?</style>', '', content, flags=re.DOTALL)
                content = re.sub(r'<script.*?>.*?</script>', '', content, flags=re.DOTALL)
                
                # Remove meta-info div specifically (contains Original Post link)
                content = re.sub(r'<div class="meta-info">.*?</div>', '', content, flags=re.DOTALL)

                # Remove tables to avoid messy text
                content = re.sub(r'<table.*?>.*?</table>', '', content, flags=re.DOTALL)
                
                # Simple regex to strip HTML tags
                text = re.sub('<[^<]+?>', ' ', content)
                # Remove extra whitespace
                text = ' '.join(text.split())
                
                # Truncate
                max_len = 800
                if len(text) > max_len:
                    # Try to find the last period before max_len
                    last_period = text.rfind('.', 0, max_len)
                    if last_period != -1:
                        return text[:last_period+1]
                    return text[:max_len] + "..."
                return text
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return "내용을 미리볼 수 없습니다."

    def reload_index(self):
        self.index = []
        if not os.path.exists(self.base_dir):
            print(f"Warning: Base directory {self.base_dir} does not exist.")
            return

        categories = {
            "QnA": "크롤링_QnA",
            "Selftest": "크롤링_selftest_MD",
            "Products": "크롤링_Products"
        }

        for category_name, folder_name in categories.items():
            cat_path = os.path.join(self.base_dir, folder_name)
            if not os.path.exists(cat_path):
                continue
            
            for post_title in os.listdir(cat_path):
                post_dir = os.path.join(cat_path, post_title)
                index_file = os.path.join(post_dir, "index.html")
                
                if os.path.isdir(post_dir) and os.path.exists(index_file):
                    # Construct a relative web path
                    safe_folder = urllib.parse.quote(folder_name)
                    safe_title = urllib.parse.quote(post_title)
                    web_path = f"/{safe_folder}/{safe_title}/index.html"
                    
                    summary = self.extract_summary(index_file)

                    self.index.append({
                        "title": post_title,
                        "category": category_name,
                        "path": web_path,
                        "full_path": index_file,
                        "summary": summary,
                        "link": HOST_BASE_URL + web_path
                    })
        print(f"Indexed {len(self.index)} documents.")

    def search(self, query: str) -> List[Dict]:
        if not query:
            return []
        
        query = query.lower().strip()
        results = []
        seen_titles = set()

        def add_result(item):
            if item['title'] not in seen_titles:
                results.append(item)
                seen_titles.add(item['title'])
        
        # 1. Exact Title Match (Priority)
        for item in self.index:
            if query == item['title'].lower():
                add_result(item)
                return results # Return immediately if exact match found

        # 2. Exact Substring Match
        for item in self.index:
            if query in item['title'].lower():
                add_result(item)
        
        # 3. Token Match (AND logic)
        tokens = query.split()
        if len(tokens) > 1:
            for item in self.index:
                if all(token in item['title'].lower() for token in tokens):
                    add_result(item)

        # 4. Fuzzy Match (difflib)
        if len(results) < 3:
            titles = [item['title'] for item in self.index]
            matches = difflib.get_close_matches(query, titles, n=5, cutoff=0.4)
            for match in matches:
                for item in self.index:
                    if item['title'] == match:
                        add_result(item)
        
        return results

    def get_by_category(self, category: str) -> List[Dict]:
        return [item for item in self.index if item['category'] == category]

indexer = ContentIndexer(BASE_DIR)

# --- Response Helpers ---

def simple_text(text: str):
    return {
        "simpleText": {"text": text}
    }

def list_card(title: str, items: List[Dict]):
    """
    Creates a Kakao ListCard.
    items should be a list of dicts with 'title', 'description', 'link'.
    """
    kakao_items = []
    for item in items[:5]: # ListCard supports max 5 items
        kakao_items.append({
            "title": item['title'],
            "description": item.get('category', ''),
            "action": "message",
            "messageText": item['title'] # Clicking sends the title as a message
        })
        
    card = {
        "header": {
            "title": title
        },
        "items": kakao_items
    }
    
    if len(items) > 5:
        card["buttons"] = [
            {
                "label": "더 보기",
                "action": "message",
            "messageText": f"{title} 더 보여줘" # Placeholder for pagination
            }
        ]
        
    return {
        "listCard": card
    }

def carousel_basic_card(items: List[Dict]):
    """
    Creates a Carousel of BasicCards.
    """
    cards = []
    for item in items[:10]: 
        # Truncate summary for card description
        summary = item.get('summary', '')
        if len(summary) > 80:
            summary = summary[:80] + "..."
            
        cards.append({
            "title": item['title'],
            "description": summary if summary else item.get('category', ''),
            "buttons": [
                {
                    "action": "webLink",
                    "label": "자세히 보기",
                    "webLinkUrl": item['link']
                }
            ]
        })
        
    return {
        "carousel": {
            "type": "basicCard",
            "items": cards
        }
    }

def basic_card(item: Dict):
    # Truncate summary for card description
    summary = item.get('summary', '')
    if len(summary) > 80:
        summary = summary[:80] + "..."
        
    # Safety check for link
    link = item.get('link', '#')
    if 'link' not in item:
        print(f"Warning: Item missing link: {item}")

    return {
        "basicCard": {
            "title": item['title'],
            "description": summary if summary else item.get('category', ''),
            "buttons": [
                {
                    "action": "webLink",
                    "label": "자세히 보기",
                    "webLinkUrl": link
                }
            ]
        }
    }

# --- Endpoints ---

def get_welcome_response():
    return {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": "안녕하세요 이스트라입니다.\n원하시는 키워드를 입력하거나\n버튼을 선택해주세요."
                    }
                }
            ],
            "quickReplies": [
                {"messageText": "챗봇 사용법", "action": "message", "label": "챗봇 사용법"},
                {"messageText": "홈페이지 이동", "action": "message", "label": "홈페이지"},
                {"messageText": "배송조회", "action": "message", "label": "배송조회"},
                {"messageText": "회사 소개", "action": "message", "label": "회사소개"},
                {"messageText": "QnA 리스트 보여줘", "action": "message", "label": "자주 묻는 질문"},
                {"messageText": "자가 진단 리스트 보여줘", "action": "message", "label": "자가 진단"},
                {"messageText": "상담원 연결", "action": "message", "label": "상담원 연결"}
            ]
        }
    }

@app.post("/api/welcome")
async def welcome(request: Request):
    return get_welcome_response()

@app.post("/api/fallback")
async def fallback(request: Request):
    try:
        body = await request.json()
        user_request = body.get("userRequest", {})
        utterance = user_request.get("utterance", "").strip()
        
        print(f"User Utterance: {utterance}")

        # 0. Handle Home/Start Keywords
        if any(keyword == utterance for keyword in ["시작", "홈으로", "처음으로", "start", "home"]):
             return get_welcome_response()

        # 0-1. Handle Chatbot Usage
        if "챗봇 사용법" in utterance or "사용법" in utterance:
            return {
                "version": "2.0",
                "template": {
                    "outputs": [
                        simple_text(
                            "💡 [이스트라 챗봇 사용법]\n\n"
                            "1. 궁금한 단어를 입력해보세요.\n"
                            "   예) '리모컨', '화면 설정', 'AS'\n\n"
                            "2. 아래 메뉴 버튼을 눌러보세요.\n"
                            "   자주 묻는 질문이나 자가 진단을\n"
                            "   쉽게 확인할 수 있습니다.\n\n"
                            "3. 해결이 안 되시면 '상담원 연결'을\n"
                            "   눌러주세요."
                        )
                    ]
                }
            }

        # 0-2. Handle Pagination (More Results)
        # Pattern: "{query} 더 보여줘" or "{query} 검색 결과 더 보여줘"
        if "더 보여줘" in utterance:
            # Extract query
            query = utterance.replace(" 검색 결과 더 보여줘", "").replace(" 더 보여줘", "").strip()
            
            # Re-search
            results = indexer.search(query)
            
            # Get next 5 items (index 5 to 10)
            next_items = results[5:10]
            
            if next_items:
                return {
                    "version": "2.0",
                    "template": {
                        "outputs": [
                            simple_text(f"'{query}' 검색 결과 더 보기 (6~{5+len(next_items)}위)"),
                            list_card(f"'{query}' 더 보기", next_items)
                        ]
                    }
                }
            else:
                 return {
                    "version": "2.0",
                    "template": {
                        "outputs": [
                            simple_text("더 이상 보여줄 내용이 없습니다.")
                        ]
                    }
                }

        # 1. Handle Category Requests (Explicit Mappings)
        # Prioritize specific "Selftest" keywords first to avoid "리스트" ambiguity
        if any(keyword in utterance for keyword in ["자가 진단", "Selftest", "진단", "테스트"]):
            items = indexer.get_by_category("Selftest")
            return {
                "version": "2.0",
                "template": {
                    "outputs": [
                        simple_text("자가 진단 리스트입니다.\n원하시는 항목을 선택해주세요."),
                        list_card("자가 진단", items)
                    ]
                }
            }

        if any(keyword in utterance for keyword in ["QnA", "자주 묻는 질문", "질문", "전체 목록", "리스트"]):
            items = indexer.get_by_category("QnA")
            return {
                "version": "2.0",
                "template": {
                    "outputs": [
                        simple_text("자주 묻는 질문 리스트입니다.\n원하시는 항목을 선택해주세요."),
                        list_card("자주 묻는 질문", items)
                    ]
                }
            }
            
        if "상담원" in utterance:
             return {
                "version": "2.0",
                "template": {
                    "outputs": [
                        simple_text("상담원 연결을 원하시면 아래 버튼을 눌러주세요."),
                        {
                            "basicCard": {
                                "title": "상담원 연결",
                                "description": "평일 09:00 ~ 18:00 (점심시간 12:00 ~ 13:00)",
                                "buttons": [
                                    {
                                        "action": "webLink",
                                        "label": "카카오톡 상담하기",
                                        "webLinkUrl": "http://pf.kakao.com/_RxffxmT/chat" # Corrected Kakao Channel Link
                                    }
                                ]
                            }
                        }
                    ]
                }
            }

        # New Handlers for Homepage, Delivery, Company Intro
        if "홈페이지" in utterance:
            return {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "basicCard": {
                                "title": "이스트라 홈페이지",
                                "description": "이스트라의 다양한 제품을 만나보세요.",
                                "buttons": [
                                    {
                                        "action": "webLink",
                                        "label": "홈페이지 바로가기",
                                        "webLinkUrl": "https://estla.co.kr/"
                                    }
                                ]
                            }
                        }
                    ]
                }
            }

        if "배송조회" in utterance or "배송 조회" in utterance or utterance == "배송":
             return {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "basicCard": {
                                "title": "배송 조회",
                                "description": "주문하신 상품의 배송 현황을 확인하세요.",
                                "buttons": [
                                    {
                                        "action": "webLink",
                                        "label": "배송 조회하기",
                                        "webLinkUrl": "https://estla.co.kr/211"
                                    }
                                ]
                            }
                        }
                    ]
                }
            }

        if "회사" in utterance or "소개" in utterance:
             return {
                "version": "2.0",
                "template": {
                    "outputs": [
                        simple_text("이스트라는 TV 전문 브랜드로서, '기본에 충실하자'라는 슬로건 아래 합리적인 가격과 최고의 품질, 그리고 진정성 있는 서비스를 제공합니다.\n\n2019년 설립 이후 스마트 TV 시장을 선도하며, 국내 최초 전 부품 5년 무상 A/S를 실시하는 등 고객 만족을 위해 최선을 다하고 있습니다."),
                        {
                            "basicCard": {
                                "title": "이스트라 브랜드 스토리",
                                "description": "이스트라의 이야기를 더 자세히 알아보세요.",
                                "buttons": [
                                    {
                                        "action": "webLink",
                                        "label": "브랜드 스토리 보기",
                                        "webLinkUrl": "https://estla.co.kr/brandstory"
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
            
        if any(keyword in utterance for keyword in ["상품", "제품", "모델"]):
            items = indexer.get_by_category("Products")
            return {
                "version": "2.0",
                "template": {
                    "outputs": [
                        simple_text("이스트라의 주요 제품 리스트입니다.\n원하시는 항목을 선택해주세요."),
                        list_card("이스트라 제품", items)
                    ]
                }
            }

        # 2. Handle Search
        results = indexer.search(utterance)
        
        if results:
            # If single match, provide a more conversational summary
            if len(results) == 1:
                item = results[0]
                return {
                    "version": "2.0",
                    "template": {
                        "outputs": [
                            simple_text(f"'{item['title']}'에 대해 찾아보았습니다.\n\n{item['summary']}\n\n자세한 내용은 아래 '자세히 보기' 버튼을 눌러 확인해주세요."),
                            basic_card(item)
                        ]
                    }
                }
            
            # Multiple matches -> Show ListCard
            return {
                "version": "2.0",
                "template": {
                    "outputs": [
                        simple_text(f"'{utterance}'와 관련된 문서를 {len(results)}개 찾았습니다.\n원하시는 내용을 선택해주세요."),
                        list_card(f"'{utterance}' 검색 결과", results)
                    ]
                }
            }
        
        # 3. No Results - True Fallback
        return {
            "version": "2.0",
            "template": {
                "outputs": [
                    simple_text(f"'{utterance}'에 대한 내용을 찾지 못했습니다.\n다른 키워드로 검색해보시거나 메뉴를 선택해주세요.")
                ],
                "quickReplies": [
                    {
                        "messageText": "홈으로",
                        "action": "message",
                        "label": "홈으로"
                    },
                    {
                        "messageText": "QnA 리스트 보여줘",
                        "action": "message",
                        "label": "전체 목록 보기"
                    }
                ]
            }
        }

    except Exception as e:
        import traceback
        with open("error.log", "w", encoding="utf-8") as f:
            f.write(f"Error: {e}\n")
            traceback.print_exc(file=f)
        return {
            "version": "2.0",
            "template": {
                "outputs": [simple_text("오류가 발생했습니다.")]
            }
        }

# --- Keep-Alive Mechanism ---
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(keep_alive())

async def keep_alive():
    while True:
        await asyncio.sleep(600)  # 10 minutes
        url = os.getenv("RENDER_EXTERNAL_URL")
        if url:
            health_url = f"{url}/health"
            try:
                async with httpx.AsyncClient() as client:
                    await client.get(health_url)
                print(f"Keep-alive ping sent to {health_url}")
            except Exception as e:
                print(f"Keep-alive ping failed: {e}")

@app.get("/health")
async def health_check():
    return {"status": "alive"}

if __name__ == "__main__":
    # Mount static files to serve HTML content locally for testing
    from fastapi.staticfiles import StaticFiles
    if os.path.exists(BASE_DIR):
    # Custom Static File Serving to handle Korean paths correctly
    @app.get("/static/{file_path:path}")
    async def serve_static(file_path: str):
        try:
            # Manually decode the path
            decoded_path = urllib.parse.unquote(file_path)
            full_path = os.path.join(BASE_DIR, decoded_path)
            
            if os.path.exists(full_path) and os.path.isfile(full_path):
                return FileResponse(full_path)
            else:
                print(f"File not found: {full_path}")
                return {"error": "File not found"}
        except Exception as e:
             print(f"Error serving file: {e}")
             return {"error": str(e)}

    print(f"Serving static files from {BASE_DIR} at /static (Custom Handler)")
    
    uvicorn.run(app, host="0.0.0.0", port=8081)
