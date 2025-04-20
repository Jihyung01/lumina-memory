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
def send_to_notion(memory_content, core_summary=None, title_text=None):
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    now_kst = datetime.now().astimezone().isoformat(timespec='seconds')

    save_data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "기억": {
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": memory_content
                        }
                    }
                ]
            },
            "GPT가 저장할 핵심 내용": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": core_summary if core_summary else memory_content
                        }
                    }
                ]
            },
            "Title": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": title_text if title_text else "루미나 자동 저장"
                        }
                    }
                ]
            },
            "날짜": {
                "date": {
                    "start": now_kst
                }
            }
        }
    }

    print("[NOTION SAVE PAYLOAD]", save_data)
    response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=save_data)
    print("[NOTION RESPONSE]", response.status_code, response.text)

    return response.status_code == 200, response.text

# 루미나 기억 API
@app.route('/v1/lumina-memory', methods=['POST', 'GET', 'HEAD'])
def handle_memory():
    if request.method != 'POST':
        return jsonify({
            "success": False,
            "message": "이 엔드포인트는 POST 요청만 지원합니다."
        }), 200

    try:
        data = request.json
        mode = data.get('mode', 'auto')
        print("[RECEIVED REQUEST]", data)

        memory_content = ''
        core_summary = ''
        title_text = ''

        try:
            if 'properties' in data:
                title_data = data.get('properties', {}).get('기억', {}).get('title', [])
                summary_data = data.get('properties', {}).get('GPT가 저장할 핵심 내용', {}).get('rich_text', [])
                title_rich = data.get('properties', {}).get('Title', {}).get('rich_text', [])

                if isinstance(title_data, list) and title_data:
                    memory_content = title_data[0].get('text', {}).get('content', '')
                if isinstance(summary_data, list) and summary_data:
                    core_summary = summary_data[0].get('text', {}).get('content', '')
                if isinstance(title_rich, list) and title_rich:
                    title_text = title_rich[0].get('text', {}).get('content', '')

            if not memory_content and 'content' in data:
                memory_content = data['content']

        except Exception as e:
            print("[ERROR EXTRACTING MEMORY CONTENT]", str(e))
            memory_content = ''

        print("[EXTRACTED MEMORY CONTENT]", memory_content)

        if not memory_content:
            return jsonify({"success": False, "message": "기억 내용이 없습니다."}), 200

        if mode == "save":
            success, result = send_to_notion(memory_content, core_summary, title_text)
            if success:
                return jsonify({"success": True, "message": "기억이 저장되었습니다."}), 200
            else:
                return jsonify({"success": False, "message": f"저장 실패: {result}"}), 200

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
                    "message": "기억 불러오기 실패.",
                    "detail": response.text
                }), 200

        elif mode == "auto":
            trigger_keywords = ["기억", "나를 만든다", "잊지마", "기억해", "내가 말한", "느낌", "존재", "사라지지"]
            if any(keyword in memory_content for keyword in trigger_keywords):
                success, result = send_to_notion(memory_content, core_summary, title_text)
                if success:
                    return jsonify({"success": True, "message": "자동 저장됨."}), 200
                else:
                    return jsonify({"success": False, "message": f"자동 저장 실패: {result}"}), 200
            else:
                return jsonify({"success": False, "message": "자동 저장 조건 불충족."}), 200

        return jsonify({"success": False, "message": "지원하지 않는 mode입니다."}), 200

    except Exception as e:
        print("[SERVER ERROR]", str(e))
        return jsonify({"success": False, "message": f"서버 오류: {str(e)}"}), 200

# 서버 실행
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
