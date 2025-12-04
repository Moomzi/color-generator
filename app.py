import os
from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)

# DeepSeek API配置（你需要替换成自己的API Key）
DEEPSEEK_API_KEY = "sk-5c4a3ba374a74d5285a79dd5fc3c2a52"  # 替换这里
API_URL = "https://api.deepseek.com/v1/chat/completions"

def generate_color_prompt(keywords):
    """构建专业提示词"""
    return f"""
你是一名专业的色彩设计师，拥有10年品牌设计经验。请为以下设计需求生成专业配色方案：

**设计需求**：{keywords}

**具体要求**：
1. 生成5套不同风格的配色方案
2. 每套方案必须包含：
   - 主色（Primary）：品牌主色调，HEX格式
   - 辅助色1（Secondary 1）：支持主色，HEX格式
   - 辅助色2（Secondary 2）：背景或次要元素，HEX格式
   - 强调色（Accent）：吸引注意力的亮点色，HEX格式
3. 色彩搭配要符合色彩心理学和设计原则

**输出格式要求**（必须是严格的JSON数组，每个对象包含以下字段）：
[
  {{
    "name": "富有创意的方案名称",
    "primary": "#3A86FF",
    "secondary1": "#FFBE0B", 
    "secondary2": "#FB5607",
    "accent": "#8338EC",
    "description": "详细说明色彩理念和情感传达",
    "use_case": "建议的应用场景"
  }}
]

注意：只输出JSON，不要有任何额外文字！
"""

@app.route('/')
def home():
    """主页"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """生成配色方案API"""
    try:
        data = request.json
        keywords = data.get('keywords', '').strip()
        
        if not keywords:
            return jsonify({"success": False, "error": "请输入关键词"})
        
        # 构建API请求
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": generate_color_prompt(keywords)}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        # 调用DeepSeek API
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # 解析JSON
            try:
                color_schemes = json.loads(content)
                return jsonify({"success": True, "schemes": color_schemes})
            except json.JSONDecodeError:
                # 如果解析失败，尝试清理响应
                cleaned_content = content.strip().replace('```json', '').replace('```', '')
                color_schemes = json.loads(cleaned_content)
                return jsonify({"success": True, "schemes": color_schemes})
                
        else:
            return jsonify({
                "success": False, 
                "error": f"API调用失败: {response.status_code}",
                "details": response.text
            })
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT",5001))
    app.run(host='0.0.0.0',port=port,debug=False)