from flask import Flask, request
import google.generativeai as genai
import re

def chinese_to_arabic(chinese_number):
    chinese_dict = {'零': 0,'一': 1,'二': 2,'三': 3,'四': 4,'五': 5,'六': 6,'七': 7,'八': 8,'九': 9,'壹': 1,'貳': 2,'參': 3,'叁': 3,'肆': 4,'駟': 4,'伍': 5,'陸': 6,'柒': 7,'捌': 8,'玖': 9}
    big_unit_dict = {'萬': 10000, '億': 100000000, '兆': 1000000000000}
    small_unit_dict = {'十': 10, '百': 100, '千': 1000, '拾': 10, '佰': 100, '仟': 1000}

    total = 0
    current_total = 0
    chinese_number = ''.join(str(chinese_dict.get(char, char)) for char in chinese_number)
    chinese_number = chinese_number.replace(",", "")
    if not chinese_number.isdigit():
        for char in chinese_number:
            if char in big_unit_dict:
                current_number = chinese_number.split(char)[0]
                chinese_number = chinese_number.split(char)[1]
                if current_number.isdigit():
                    total += int(current_number) * big_unit_dict[char]
                else:
                    for ch in current_number:
                        if ch in small_unit_dict:
                            current_total += int(current_number.split(ch)[0]) * small_unit_dict[ch]
                            current_number = current_number.split(ch)[1]
                    total += current_total * big_unit_dict[char]
        print(total)
        current_total = 0
        for ch in chinese_number:
            if ch in small_unit_dict:
                current_total += int(chinese_number.split(ch)[0]) * small_unit_dict[ch]
                chinese_number = chinese_number.split(ch)[1]
        total += current_total
    else:
        total = chinese_number
    return str(total)

def find_and_convert_numbers(article):
    # 定义正则表达式，匹配包含阿拉伯数字和中文单位的数字
    regex = re.compile(r'(?:[零一二三四五六七八九壹貳參叁肆駟伍陸柒捌玖\d,]+[兆億萬千仟百佰拾十]*)+')

    # 在文本中搜索匹配的数字
    matches = regex.findall(article)
    # 显示找到的数字
    if matches:
        for match in matches:
            arabic_number = chinese_to_arabic(match)
            article = article.replace(match, arabic_number)
    return article
    
app = Flask(__name__)

@app.route('/',methods=["POST"])
def query():
    # 从请求中获取 JSON 数据
    query = request.form.get('query')
    query = find_and_convert_numbers(query)
    //print(query)
    //genai.configure(api_key = 'AIzaSyCv7-MKV9NqO6DqRXYu4GXysWeSnGBEijk')
    //model = genai.GenerativeModel('gemini-pro')
    //response = model.generate_content(query)
    //data_json = response.text
    # 处理接收到的数据（这里简单地将数据返回）
    return query

@app.route('/',methods=["GET"])
def test():
    return 'success'
