
# app.py
from flask import Flask, render_template_string, request
import requests
import re
import html

app = Flask(__name__)

html_template = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نظام تقييم الإجابات الذكي</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
        
        :root {
            --primary-color: #4a90e2;
            --secondary-color: #50e3c2;
            --background-color: #f0f4f8;
            --text-color: #333;
            --card-bg: #ffffff;
            --success-color: #27ae60;
            --error-color: #e74c3c;
        }

        body {
            font-family: 'Tajawal', Arial, sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
            line-height: 1.6;
            margin: 0;
            padding: 0;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow-x: hidden;
        }

        .background {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: -1;
            background: linear-gradient(45deg, #4a90e2, #50e3c2);
            opacity: 0.1;
        }

        .bubble {
            position: absolute;
            border-radius: 50%;
            background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0));
            animation: float 10s infinite ease-in-out;
        }

        @keyframes float {
            0%, 100% { transform: translateY(0) rotate(0deg); }
            50% { transform: translateY(-20px) rotate(180deg); }
        }

        .container {
            max-width: 800px;
            width: 90%;
            background-color: var(--card-bg);
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .container::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(
                to bottom right,
                rgba(74, 144, 226, 0.1),
                rgba(80, 227, 194, 0.1)
            );
            transform: rotate(30deg);
            z-index: 0;
            transition: transform 0.5s ease;
        }

        .container:hover::before {
            transform: rotate(35deg) scale(1.1);
        }

        h1 {
            color: var(--primary-color);
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            position: relative;
            z-index: 1;
        }

        h1::after {
            content: '';
            display: block;
            width: 50px;
            height: 4px;
            background: var(--secondary-color);
            margin: 10px auto;
            border-radius: 2px;
            transition: width 0.3s ease;
        }

        .container:hover h1::after {
            width: 100px;
        }

        form {
            display: grid;
            gap: 20px;
            position: relative;
            z-index: 1;
        }

        label {
            font-weight: bold;
            margin-bottom: 5px;
            display: block;
            transition: color 0.3s ease;
        }

        input[type="text"], input[type="number"], textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: all 0.3s ease;
            background-color: rgba(255, 255, 255, 0.8);
        }

        input[type="text"]:focus, input[type="number"]:focus, textarea:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.2);
            outline: none;
            background-color: #ffffff;
        }

        input[type="submit"] {
            background-color: var(--primary-color);
            color: white;
            border: none;
            padding: 12px 20px;
            font-size: 18px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            position: relative;
            overflow: hidden;
        }

        input[type="submit"]::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            transition: width 0.6s ease, height 0.6s ease;
        }

        input[type="submit"]:hover::before {
            width: 300px;
            height: 300px;
        }

        .result, .error {
            text-align: center;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
            transition: all 0.3s ease;
            position: relative;
            z-index: 1;
        }

        .result {
            background-color: rgba(39, 174, 96, 0.1);
            border: 1px solid var(--success-color);
            color: var(--success-color);
        }

        .error {
            background-color: rgba(231, 76, 60, 0.1);
            border: 1px solid var(--error-color);
            color: var(--error-color);
        }

        .grade {
            font-size: 36px;
            font-weight: bold;
            color: var(--success-color);
            margin: 20px 0;
            transition: all 0.3s ease;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }

        a {
            display: inline-block;
            margin-top: 20px;
            color: var(--primary-color);
            text-decoration: none;
            transition: all 0.3s ease;
            font-weight: bold;
            position: relative;
        }

        a::after {
            content: '';
            position: absolute;
            width: 100%;
            height: 2px;
            bottom: -2px;
            left: 0;
            background-color: var(--primary-color);
            transform: scaleX(0);
            transition: transform 0.3s ease;
        }

        a:hover::after {
            transform: scaleX(1);
        }

        .loading {
            display: none;
            text-align: center;
            margin-top: 20px;
        }

        .loading::after {
            content: '';
            display: inline-block;
            width: 30px;
            height: 30px;
            border: 4px solid var(--primary-color);
            border-top: 4px solid transparent;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .container > * {
            animation: fadeIn 0.5s ease-out forwards;
        }

        @media (max-width: 600px) {
            .container {
                padding: 20px;
            }

            h1 {
                font-size: 2em;
            }

            input[type="submit"] {
                font-size: 16px;
            }
        }
    </style>
    <script>
        function showLoading() {
            document.getElementById('submitBtn').style.display = 'none';
            document.getElementById('loading').style.display = 'block';
        }

        document.addEventListener('DOMContentLoaded', (event) => {
            const form = document.querySelector('form');
            if (form) {
                const inputs = form.querySelectorAll('input, textarea');
                inputs.forEach(input => {
                    input.addEventListener('focus', () => {
                        input.parentElement.classList.add('active');
                    });
                    input.addEventListener('blur', () => {
                        if (input.value === '') {
                            input.parentElement.classList.remove('active');
                        }
                    });
                });
            }

            const background = document.createElement('div');
            background.classList.add('background');
            document.body.appendChild(background);

            for (let i = 0; i < 20; i++) {
                const bubble = document.createElement('div');
                bubble.classList.add('bubble');
                bubble.style.left = `${Math.random() * 100}%`;
                bubble.style.top = `${Math.random() * 100}%`;
                bubble.style.width = `${Math.random() * 100 + 50}px`;
                bubble.style.height = bubble.style.width;
                bubble.style.animationDelay = `${Math.random() * 10}s`;
                background.appendChild(bubble);
            }

            const formElements = document.querySelectorAll('input, textarea, button');
            formElements.forEach(element => {
                element.addEventListener('mouseover', () => {
                    element.style.transform = 'scale(1.05)';
                    element.style.boxShadow = '0 5px 15px rgba(0,0,0,0.1)';
                });
                element.addEventListener('mouseout', () => {
                    element.style.transform = 'scale(1)';
                    element.style.boxShadow = 'none';
                });
            });

            const title = document.querySelector('h1');
            const titleText = title.textContent;
            title.textContent = '';
            let i = 0;
            const typeWriter = () => {
                if (i < titleText.length) {
                    title.textContent += titleText.charAt(i);
                    i++;
                    setTimeout(typeWriter, 100);
                }
            };
            typeWriter();
        });
    </script>
</head>
<body>
    <div class="container">
        {% if error %}
            <h1>حدث خطأ</h1>
            <div class="error">
                <p>{{ error }}</p>
                <a href="/">العودة للصفحة الرئيسية</a>
            </div>
        {% elif result %}
            <h1>نتيجة التقييم</h1>
            <div class="result">
                <p class="grade">{{ result.grade }}</p>
                <p class="explanation">{{ result.explanation | safe }}</p>
                <a href="/">تقييم إجابة جديدة</a>
            </div>
        {% else %}
            <h1>نظام تقييم الإجابات الذكي</h1>
            <form method="POST" onsubmit="showLoading()">
                <div>
                    <label for="question">السؤال:</label>
                    <textarea id="question" name="question" required></textarea>
                </div>
                <div>
                    <label for="full_mark">الدرجة الكاملة:</label>
                    <input type="number" id="full_mark" name="full_mark" required>
                </div>
                <div>
                    <label for="model_answer">الإجابة النموذجية:</label>
                    <textarea id="model_answer" name="model_answer" required></textarea>
                </div>
                <div>
                    <label for="student_answer">إجابة الطالب:</label>
                    <textarea id="student_answer" name="student_answer" required></textarea>
                </div>
                <input type="submit" value="تقييم الإجابة" id="submitBtn">
            </form>
            <div id="loading" class="loading"></div>
        {% endif %}
    </div>
</body>
</html>
"""
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        api_data = {
            "question": request.form['question'],
            "full_mark": request.form['full_mark'],
            "model_answer": request.form['model_answer'],
            "student_answer": request.form['student_answer']
        }

        api_url = "https://911a-35-189-175-66.ngrok-free.app/grade"
        try:
            response = requests.post(api_url, json=api_data, timeout=20)  
            response.raise_for_status()
            result = response.json()

            if 'explanation' in result:
                explanation = result['explanation']
                grade = extract_grade(explanation)
                formatted_explanation = format_explanation(explanation)
                return render_template_string(html_template, result={'grade': grade, 'explanation': formatted_explanation})
            else:
                return render_template_string(html_template, error="الاستجابة لا تحتوي على بيانات صحيحة.")
        except requests.exceptions.Timeout:
            return render_template_string(html_template, error="خطأ: انتهى وقت الاتصال بالخادم.")
        except requests.exceptions.ConnectionError:
            return render_template_string(html_template, error="خطأ في الاتصال بالخادم. يرجى التحقق من عنوان API.")
        except requests.RequestException as e:
            return render_template_string(html_template, error=f"خطأ في الاتصال بـ API: {str(e)}")

    return render_template_string(html_template)


def extract_grade(explanation):
    grade_match = re.search(r'الدرجة:\s*(\d+)\s*من\s*(\d+)', explanation)
    if grade_match:
        return f"{grade_match.group(1)}/{grade_match.group(2)}"
    return "غير محدد"

def extract_similarity(explanation):
    similarity_match = re.search(r'نسبة التشابه:\s*(\d+)%', explanation)
    if similarity_match:
        return similarity_match.group(1) + "%"
    return "غير محدد"

def format_explanation(explanation):
    explanation = html.escape(explanation)
    explanation = explanation.replace('\n', '<br>')
    
    headers = ['الدرجة:', 'نسبة التشابه:', 'السبب:', 'النقاط الصحيحة:', 'النقاط الخاطئة:', 'التحليل:', 'ملاحظة:']
    for header in headers:
        explanation = explanation.replace(header, f'<strong>{header}>')
    
    return explanation

if __name__ == '__main__':
    app.run(debug=True)