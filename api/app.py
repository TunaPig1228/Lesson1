from flask import Flask, request
import google.generativeai as genai
import re

def is_float(string):
    try:
        float_value = float(string)
        return True
    except ValueError:
        return False
        
def chinese_to_arabic(chinese_number):
    chinese_dict = {'零': 0,'一': 1,'二': 2,'三': 3,'四': 4,'五': 5,'六': 6,'七': 7,'八': 8,'九': 9,'壹': 1,'貳': 2,'參': 3,'叁': 3,'肆': 4,'駟': 4,'伍': 5,'陸': 6,'柒': 7,'捌': 8,'玖': 9}
    big_unit_dict = {'萬': 10000, '億': 100000000, '兆': 1000000000000}
    small_unit_dict = {'十': 10, '百': 100, '千': 1000, '拾': 10, '佰': 100, '仟': 1000}

    total = 0
    current_total = 0
    chinese_number = ''.join(str(chinese_dict.get(char, char)) for char in chinese_number)
    chinese_number = chinese_number.replace(",", "")
    if not is_float(chinese_number) and chinese_number:
        for char in chinese_number:
            if char in big_unit_dict:
                current_number = chinese_number.split(char)[0]
                chinese_number = chinese_number.split(char)[1]
                if is_float(current_number):
                    total += float(current_number) * big_unit_dict[char]
                else:
                    for ch in current_number:
                        if ch in small_unit_dict:
                            current_total += float(current_number.split(ch)[0]) * small_unit_dict[ch]
                            current_number = current_number.split(ch)[1]
                    total += current_total * big_unit_dict[char]
        current_total = 0
        for ch in chinese_number:
            if ch in small_unit_dict:
                current_total += float(chinese_number.split(ch)[0]) * small_unit_dict[ch]
                chinese_number = chinese_number.split(ch)[1]
        total += current_total
        total = str(total)
        if is_float(total) and float(total)>1000:
            total = str(round(float(total)/1000, 1)).replace(".0", "") + '仟'
    else:
        total = chinese_number

    return total

def find_and_convert_numbers(article):
    # 定义正则表达式，匹配包含阿拉伯数字和中文单位的数字
    regex = re.compile(r'(?:[零一二三四五六七八九壹貳參叁肆駟伍陸柒捌玖\d]+[,.]*[兆億萬千仟百佰拾十]*)+')
    replace_text_dict = {'營業損益': '營業收入'}
    for key, value in replace_text_dict.items():
        article = article.replace(key, value)
    article = re.sub(r'\((-?\d+([.,]*\d+){2})\)', lambda match: '-' + match.group(1), article)
    # 在文本中搜索匹配的数字
    matches = regex.findall(article)
    # 显示找到的数字
    if matches:
        for match in matches:
            arabic_number = chinese_to_arabic(match)
            article = article.replace(match, arabic_number)
    return article
    
app = Flask(__name__)

@app.route('/fast_data',methods=["POST"])
def fast_data():
    # 从请求中获取 JSON 数据
    query = request.form.get('query')
    query = find_and_convert_numbers(query)
    genai.configure(api_key = 'AIzaSyCv7-MKV9NqO6DqRXYu4GXysWeSnGBEijk')
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(query)
    data_json = response.text
    # 处理接收到的数据（这里简单地将数据返回）
    return data_json

@app.route('/get_quarter_data',methods=["POST"])
def get_quarter_data():
    # 从请求中获取 JSON 数据
    code = request.form.get('code')
    current_ym = {'y': int(request.form.get('y')), 'm': int(request.form.get('m'))}
    pre_quarter = current_ym
    pre_year_quarter = current_ym
    if current_ym['m'] == 1:
        pre_quarter = {'y': current_ym['y']-1, 'm': 4}
        pre_year_quarter = {'y': current_ym['y']-1, 'm': 1}
    elif current_ym['m'] == 2:
        pre_quarter = {'y': current_ym['y'], 'm': 1}
        pre_year_quarter = {'y': current_ym['y']-1, 'm': 2}
    elif current_ym['m'] == 3:
        pre_quarter = {'y': current_ym['y'], 'm': 2}
        pre_year_quarter = {'y': current_ym['y']-1, 'm': 3}
    elif current_ym['m'] == 4:
        pre_quarter = {'y': current_ym['y'], 'm': 3}
        pre_year_quarter = {'y': current_ym['y']-1, 'm': 4}

    history_quarter = {'pre_quarter': pre_quarter}
    history_quarter_value = {'pre_quarter': '', 'sum_pre_quarter': '', 'pre_year_quarter': '', 'sum_pre_year_quarter': ''}
    url = 'https://mops.twse.com.tw/mops/web/ajax_t163sb01'

    def get_sum_quarter_data(yy, mm):
        for _ in range(2):
            need_keys = ['營業收入', '營業毛利', '營業利益', '每股盈餘']
            need_dict = {'營業收入': '', '營業毛利': '', '營業利益': '', '每股盈餘': ''}
            data = {
                'firstin': '1',
                'co_id': code,
                'year': yy,
                'season': mm
            }
            res = requests.post(url, data=data)
            tree = html.fromstring(res.text)
            try:
                for key in need_keys:
                    value = tree.xpath(f'//td[contains(text(), "{key}")]/following-sibling::td[1]')[0].text.replace(',', '')
                    if is_float(value):
                        need_dict[key] = str(round(float(value), 2))
                    else:
                        need_dict[key] = ''
                return need_dict
            except:
                continue
        return need_dict
    for quarter_name, quarter in history_quarter.items():
        sum_quarter_data_dict = get_sum_quarter_data(str(quarter['y']).zfill(3), str(quarter['m']).zfill(2))
        if quarter['m'] == 1:
            history_quarter_value[quarter_name] = sum_quarter_data_dict
        else:
            history_quarter_value['sum_' + quarter_name] = sum_quarter_data_dict
    return current_ym

@app.route('/',methods=["GET"])
def test():
    return 'success'
