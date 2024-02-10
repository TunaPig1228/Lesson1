from flask import Flask, request
import google.generativeai as genai

app = Flask(__name__)

@app.route('/',methods=["POST"])
def query():
    # 从请求中获取 JSON 数据
    query = request.get_json()['query']
    genai.configure(api_key = 'AIzaSyCv7-MKV9NqO6DqRXYu4GXysWeSnGBEijk')
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(query)
    # 处理接收到的数据（这里简单地将数据返回）
    return jsonify(response.text)

@app.route('/',methods=["GET"])
def test():
    return 'success'
