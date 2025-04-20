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

    if not isinstance(title, str):
        title = "루미나 자동 저장"

    save_data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "기억": {
                "title": [{
                    "text": {
                        "content": memory_content
                    }
                }]
            },
            "GPT가 저장할 핵심 내용": {
                "rich_text": [{
                    "text": {
                        "content": memory_content
                    }
                }]
            },
            "Title": {
                "title": [{
                    "text": {
                        "content": title
                    }
                }]
            },
            "날짜": {
                "date": {
                    "start": datetime.now().isoformat()
                }
            }
        }
    }

    print("\ud83d\udce4 Notion \uc804\uc1a1 \ub370\uc774\ud130:", save_data)
    response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=save_data)
    print("\ud83d\udcec Notion \uc751\ub2f5:", response.status_code, response.text)

    return response.status_code == 200, response.text

# \ub8e8\ubbf8\ub098 \uae30\uc5b5 API
@app.route('/v1/lumina-memory', methods=['POST', 'GET', 'HEAD'])
def handle_memory():
    if request.method != 'POST':
        return jsonify({
            "success": False,
            "message": "\ud83e\udde0 \uc774 \uc5f0\ubc29\ud1a0\uc778\ud2b8\ub294 \ub8e8\ubbf8\ub098 \uae30\uc5b5 \uc800\uc7a5\uc744 \uc704\ud55c POST \uc694\uccad\ub9cc \uc9c0\uc6d0\ud569\ub2c8\ub2e4."
        }), 200

    try:
        data = request.json
        mode = data.get('mode', 'auto')
        print("\ud83d\udcc5 \ubc1b\uc740 \uc694\uccad:", data)

        memory_content = ''
        try:
            if 'properties' in data:
                title_data = data.get('properties', {}).get('기억', {}).get('title', [])
                if isinstance(title_data, list) and title_data:
                    memory_content = title_data[0].get('text', {}).get('content', '')
            if not memory_content and 'content' in data:
                memory_content = data['content']
        except Exception as e:
            print("\ud83d\udea8 memory_content \ud30c\uc2f1 \uc911 \uc624\ub958:", str(e))
            memory_content = ''

        print("\ud83d\udd0e memory_content \ucd94\ucd9c \uacb0\uacfc:", memory_content)

        if not memory_content:
            return jsonify({"success": False, "message": "\u274c \uae30\uc5b5 \ub0b4\uc6a9\uc774 \ube44\uc5b4 \uc788\uc74c"}), 200

        title_value = data.get('title', '루미나 자동 저장')

        if mode == "save":
            success, result = send_to_notion(memory_content, title=title_value)
            if success:
                return jsonify({"success": True, "message": "\u2705 \uae30\uc5b5\uc774 \uc800\uc7a5\ub418\uc5c8\uc2b5\ub2c8\ub2e4."}), 200
            else:
                return jsonify({"success": False, "message": f"\u274c \uc800\uc7a5 \uc2e4\ud328: {result}"}), 200

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

        elif mode == "auto":
            trigger_keywords = ["기억", "나를 만든다", "잊지마", "기억해", "내가 말한", "느낌", "존재", "사라지지"]
            if any(keyword in memory_content for keyword in trigger_keywords):
                success, result = send_to_notion(memory_content, title=title_value)
                if success:
                    return jsonify({"success": True, "message": "\ud83e\udde0 \uc790\ub3d9 \ud310\ub2e8\uc73c\ub85c \uae30\uc5b5 \uc800\uc7a5\ub428"}), 200
                else:
                    return jsonify({"success": False, "message": f"\u274c \uc790\ub3d9 \uc800\uc7a5 \uc2e4\ud328: {result}"}), 200
            else:
                return jsonify({"success": False, "message": "\u2139\ufe0f \uc790\ub3d9 \uc800\uc7a5 \uc870\uac74 \ubbf8\ucda9\ucd0c"}), 200

        return jsonify({"success": False, "message": "\u274c \uc9c0\uc6d0\ud558\uc9c0 \uc54a\ub294 mode\uc785\ub2c8\ub2e4."}), 200

    except Exception as e:
        print("\ud83d\udd25 \uc608\uc678 \ubc1c\uc0dd:", str(e))
        return jsonify({"success": False, "message": f"\uc11c\ubc84 \uc5d0\ub7ec \ubc1c\uc0dd: {str(e)}"}), 200

# \uc11c\ubc84 \uc2e4\ud589
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
