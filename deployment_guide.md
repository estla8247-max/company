# 이스트라 챗봇 배포 가이드

## 1. Git에 코드 업로드

### 1.1 GitHub 저장소 생성
1. [GitHub](https://github.com)에 로그인
2. 우측 상단 **+** 버튼 → **New repository** 클릭
3. Repository name: `estla-chatbot` (원하는 이름)
4. **Create repository** 클릭

### 1.2 로컬 프로젝트 업로드
> [!IMPORTANT]
> **필수 업로드 폴더**:
> - `KakaoSkill`: 챗봇 서버 코드
> - `HTML_Conversion`: 챗봇이 보여줄 데이터 (HTML)
>
> `MD_Source`는 원본 데이터이므로 함께 올리는 것을 권장하지만, 챗봇 구동에 필수적인 것은 아닙니다.

```bash
cd d:/업무/matari/챗봇_이스트라
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/estla8247-max/company.git
git push -u origin main
```

---

## 2. Render 설정

### 2.1 Render 계정 및 서비스 생성
1. [Render](https://render.com)에 GitHub 계정으로 로그인
2. **Dashboard** → **New +** → **Web Service** 클릭
3. GitHub 연결 후 `estla-chatbot` 저장소 선택

### 2.2 Web Service 설정`
| 항목 | 값 |
|------|-----|
| **Name** | `estla-chatbot` |
| **Region** | Singapore (Asia) 권장 |
| **Branch** | `main` |
| **Root Directory** | `KakaoSkill` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn skill_server:app --host 0.0.0.0 --port $PORT` |

### 2.3 환경 변수 설정
**Environment** 탭에서 추가:
- `RENDER_EXTERNAL_URL`: 배포 후 자동 생성되는 URL (예: `https://estla-chatbot.onrender.com`)

### 2.4 배포 완료 확인
- 배포 완료 후 `https://YOUR_APP.onrender.com/health` 접속
- `{"status": "alive"}` 응답 확인

---

## 3. 카카오 i 오픈빌더 설정

### 3.1 채널 생성 (없는 경우)
1. [카카오 비즈니스](https://business.kakao.com) 접속
2. **카카오톡 채널** 생성 또는 기존 채널 선택

### 3.2 오픈빌더 접속
1. [카카오 i 오픈빌더](https://i.kakao.com) 접속
2. 채널 연결 후 챗봇 생성

### 3.3 스킬 등록
1. 좌측 메뉴 **스킬** → **생성** 클릭
2. 스킬 정보 입력:

| 항목 | 값 |
|------|-----|
| **스킬명** | 이스트라 챗봇 스킬 |
| **설명** | 제품/QnA/자가진단 안내 |

3. **스킬 URL 추가**:
   - **Welcome (환영 메시지)**: `https://YOUR_APP.onrender.com/api/welcome`
   - **Fallback (폴백)**: `https://YOUR_APP.onrender.com/api/fallback`

### 3.4 시나리오 설정
1. **시나리오** → **폴백 블록** 선택
2. **스킬 데이터 사용** 체크 → 등록한 스킬의 `fallback` URL 선택
3. **웰컴 블록**도 동일하게 `welcome` URL 연결

### 3.5 배포
1. 우측 상단 **배포** 버튼 클릭
2. 카카오톡에서 채널 검색 후 테스트

---

## 4. 카카오 챗봇 이미지 사이즈 가이드

| 카드 타입 | 권장 비율 | 권장 사이즈 | 최대 용량 |
|-----------|-----------|-------------|-----------|
| **Basic Card** | 2:1 | 800 x 400 px | 5MB |
| **Commerce Card** | 2:1 | 800 x 400 px | 5MB |
| **List Card (썸네일)** | 1:1 | 400 x 400 px | 5MB |
| **Carousel (이미지형)** | 2:1 | 800 x 400 px | 5MB |

> [!TIP]
> 이미지 파일 형식: JPG, PNG 권장. GIF 지원되나 용량 주의.

---

## 5. 문제 해결

### Render 무료 플랜 슬립 모드
- 15분 동안 요청이 없으면 서버가 슬립 상태로 전환됨
- 현재 코드에 Keep-Alive 로직이 포함되어 있어 10분마다 자동 ping 발송

### 스킬 연결 오류
- Render 콘솔에서 로그 확인
- 카카오 오픈빌더의 **스킬 테스트** 기능으로 직접 요청/응답 확인

---

## 6. 현재 프로젝트 구조

```
챗봇_이스트라/
├── KakaoSkill/              # 메인 서버 코드 (Render에 배포)
│   ├── skill_server.py
│   ├── requirements.txt
│   └── test_chatbot.html
├── HTML_Conversion/         # 챗봇이 참조하는 HTML 콘텐츠
├── MD_Source/               # 원본 MD 파일 (배포 불필요)
│   ├── 크롤링_Products/
│   ├── 크롤링_QnA/
│   └── 크롤링_selftest_MD/
```
