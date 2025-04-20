from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from flask_cors import CORS

# 초기 설정
app = Flask(__name__)
CORS(app)
load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID") or "1d7ffbc06edc807280bdc6c14abfe288"

# Notion으로 전송 함수
def send_to_notion(memory_content, title="루미나 자동 저장"):
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    save_data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "기억": {
                "title": [{
                    "text": {"content": memory_content}
                }]
            },
            "GPT가 저장할 핵심 내용": {
                "rich_text": [{
                    "text": {"content": memory_content}
                }]
            },
            "Title": {
                "title": [{
                    "text": {"content": title}
                }]
            },
            "날짜": {
                "date": {
                    "start": datetime.now().isoformat()
                }
            }
        }
    }

    print("📤 Notion 전송 데이터:", save_data)
    response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=save_data)
    print("📬 Notion 응답:", response.status_code, response.text)

    return response.status_code == 200, response.text

# 루미나 기억 API
@app.route('/v1/lumina-memory', methods=['POST', 'GET', 'HEAD'])
def handle_memory():
    if request.method != 'POST':
        return jsonify({
            "success": False,
            "message": "🧠 이 엔드포인트는 루미나 기억 저장을 위한 POST 요청만 지원합니다."
        }), 200

    try:
        data = request.json
        mode = data.get('mode', 'auto')
        print("📥 받은 요청:", data)

        # memory_content 추출 시 예외 처리
        memory_content = ''
        try:
            title_data = data.get('properties', {}).get('기억', {}).get('title', [])
            if isinstance(title_data, list) and title_data:
                text_obj = title_data[0].get('text', {})
                memory_content = text_obj.get('content', '')
        except Exception as e:
            print("🚨 memory_content 파싱 중 오류:", str(e))
            memory_content = ''

        print("🔎 memory_content 추출 결과:", memory_content)

        if not memory_content:
            return jsonify({"success": False, "message": "❌ 기억 내용이 비어 있음"}), 200

        # 수동 저장
        if mode == "save":
            success, result = send_to_notion(memory_content, title="루미나 수동 저장")
            if success:
                return jsonify({"success": True, "message": "✅ 기억이 저장되었습니다."}), 200
            else:
                return jsonify({"success": False, "message": f"❌ 저장 실패: {result}"}), 200

        # 최근 기억 불러오기
        elif mode == "fetch":
            page_size = data.get('page_size', 5)
            headers = {
                "Authorization": f"Bearer {NOTION_API_KEY}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28"
            }

            query_data = {
                "filter": {},
                "sorts": [{"property": "날짜", "direction": "descending"}],
                "page_size": page_size
            }

            response = requests.post(
                f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query",
                headers=headers,
                json=query_data
            )

            if response.status_code == 200:
                results = response.json().get('results', [])
                memories = []
                for result in results:
                    title_data = result.get('properties', {}).get('기억', {}).get('title', [])
                    content = title_data[0].get('text', {}).get('content', '') if title_data else ''
                    memories.append(content)

                return jsonify({"success": True, "memories": memories}), 200
            else:
                return jsonify({
                    "success": False,
                    "message": "기억을 불러오는데 실패했습니다.",
                    "detail": response.text
                }), 200

        # 자동 판단 저장
        elif mode == "auto":
            trigger_keywords = ["기억", "나를 만든다", "잊지마", "기억해", "내가 말한", "느낌", "존재", "사라지지"]
            if any(keyword in memory_content for keyword in trigger_keywords):
                success, result = send_to_notion(memory_content, title="루미나 자동 판단 저장")
                if success:
                    return jsonify({"success": True, "message": "🧠 자동 판단으로 기억 저장됨"}), 200
                else:
                    return jsonify({"success": False, "message": f"❌ 자동 저장 실패: {result}"}), 200
            else:
                return jsonify({"success": False, "message": "ℹ️ 자동 저장 조건 미충족"}), 200

        return jsonify({"success": False, "message": "❌ 지원하지 않는 mode입니다."}), 200

    except Exception as e:
        print("🔥 예외 발생:", str(e))
        return jsonify({"success": False, "message": f"서버 에러 발생: {str(e)}"}), 200

# 서버 실행
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
