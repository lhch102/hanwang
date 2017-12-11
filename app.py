from flask import Flask, request, render_template

from controller.hanwang import hanwang

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@app.route('/signin', methods=['GET'])
def signin_form():
    return render_template('form.html')


@app.route('/signin', methods=['POST'])
def signin():
    userName = request.form['username']
    password = request.form['password']
    userListInfo = hanwang.getUser(userName, password)
    if type(userListInfo) == tuple:
        return render_template('signin-ok.html', userListInfo=userListInfo)
    else:
        return render_template('form.html', message=userListInfo, username=userName)


if __name__ == '__main__':
    app.run()
