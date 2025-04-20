from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv(
    "NOTION_DATABASE_ID") or "1d7ffbc06edc807280bdc6c14abfe288"


@app.route('/v1/lumina-memory', methods=['POST'])
def handle_memory():
    try:
        data = request.json
        mode = data.get('mode')
        print("📥 받은 요청:", data)

        headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

        if mode == "save":
            memory_content = data.get('properties', {}).get('기억', {}).get(
                'title', [{}])[0].get('text', {}).get('content', '')

            if not memory_content:
                return jsonify({"error": "❌ 기억 내용이 비어 있음"}), 400

            save_data = {
                "parent": {
                    "database_id": NOTION_DATABASE_ID
                },
                "properties": {
                    "기억": {
                        "title": [{
                            "text": {
                                "content": memory_content
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

            print("📤 Notion 전송 데이터:", save_data)

            response = requests.post("https://api.notion.com/v1/pages",
                                     headers=headers,
                                     json=save_data)

            print("📬 Notion 응답:", response.status_code, response.text)

            return jsonify({
                "success": response.status_code == 200,
                "message": response.text
            })

        elif mode == "fetch":
            page_size = data.get('page_size', 5)

            query_data = {
                "filter": {},
                "sorts": [{
                    "property": "날짜",
                    "direction": "descending"
                }],
                "page_size": page_size
            }

            response = requests.post(
                f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query",
                headers=headers,
                json=query_data)

            if response.status_code == 200:
                results = response.json().get('results', [])
                memories = []

                for result in results:
                    title_data = result.get('properties',
                                            {}).get('기억', {}).get('title', [])
                    content = title_data[0].get('text', {}).get(
                        'content', '') if title_data else ''
                    memories.append(content)

                return jsonify({"memories": memories})
            else:
                return jsonify({"error": "기억을 불러오는데 실패했습니다."}), 500

        return jsonify({"error": "❌ 지원하지 않는 mode입니다."}), 400

    except Exception as e:
        print("🔥 예외 발생:", str(e))
        return jsonify({"error": f"서버 에러 발생: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
