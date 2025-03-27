import random
import re
from flask import Flask, render_template, request, make_response
from faker import Faker

fake = Faker()

app = Flask(__name__)
application = app

images_ids = ['7d4e9175-95ea-4c5f-8be5-92a6b708bb3c',
              '2d2ab7df-cdbc-48a8-a936-35bba702def5',
              '6e12f3de-d5fd-4ebb-855b-8cbc485278b7',
              'afc2cfe7-5cac-4b80-9b9a-d5c65ef0c728',
              'cab5b7f2-774e-4884-a200-0c0180fa777f']

def generate_comments(replies=True):
    comments = []
    for i in range(random.randint(1, 3)):
        comment = { 'author': fake.name(), 'text': fake.text() }
        if replies:
            comment['replies'] = generate_comments(replies=False)
        comments.append(comment)
    return comments

def generate_post(i):
    return {
        'title': 'Заголовок поста',
        'text': fake.paragraph(nb_sentences=100),
        'author': fake.name(),
        'date': fake.date_time_between(start_date='-2y', end_date='now'),
        'image_id': f'{images_ids[i]}.jpg',
        'comments': generate_comments()
    }

posts_list = sorted([generate_post(i) for i in range(5)], key=lambda p: p['date'], reverse=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/posts')
def posts():
    return render_template('posts.html', title='Посты', posts=posts_list)

@app.route('/posts/<int:index>')
def post(index):
    p = posts_list[index]
    return render_template('post.html', title=p['title'], post=p)

@app.route('/about')
def about():
    return render_template('about.html', title='Об авторе')

@app.route('/url_params')
def url_params():
    args = request.args
    return render_template('url_params.html', args=args)

@app.route('/headers')
def headers():
    hdrs = request.headers
    return render_template('headers.html', headers=hdrs)

@app.route('/cookies')
def cookies():
    cookie_value = request.cookies.get("mycookie")
    resp = make_response(render_template('cookies.html', cookie_value=cookie_value))
    if cookie_value is None:
        resp.set_cookie("mycookie", "cookie_value")
    else:
        resp.delete_cookie("mycookie")
    return resp

@app.route('/form_data', methods=["GET", "POST"])
def form_data():
    form_data = None
    if request.method == "POST":
        form_data = request.form
    return render_template('form_data.html', form_data=form_data)


@app.route('/phone', methods=["GET", "POST"])
def phone():
    error = None
    formatted = None
    phone_input = ""
    if request.method == "POST":
        phone_input = request.form.get("phone", "")

        if re.search(r"[^0-9\s\(\)\-\.\+]", phone_input):
            error = "Недопустимый ввод. В номере телефона встречаются недопустимые символы."
        else:
            digits = re.sub(r"\D", "", phone_input)
            normalized = phone_input.strip()
            required = 11 if (normalized.startswith("+7") or normalized.startswith("8")) else 10
            if len(digits) != required:
                error = "Недопустимый ввод. Неверное количество цифр."
            else:
                if required == 11:
                    digits = digits[1:]
                formatted = "8-{}-{}-{}-{}".format(digits[:3], digits[3:6], digits[6:8], digits[8:10])
    return render_template('phone.html', error=error, formatted=formatted, phone_input=phone_input)

if __name__=="__main__":
    app.run(debug=True)
