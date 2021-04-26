import uuid
from os.path import getsize

from flask import Flask, request, render_template, make_response, redirect, send_from_directory

from data import db_session
from data.friendships import Friendship
from data.project import Project
from data.projectsform import AddProject
from data.user_sessions import UserSession
from data.users import User

db_session.global_init("db/development.db")
db_sess = db_session.create_session()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
visits_count = 0


def check_if_user_signed_in(cookies, db_sess):
    '''
    проверка на вход пользователя
    '''
    return User.check_cookies(cookies, db_sess)


@app.route("/sign_in_user", methods=['POST'])
def sign_in_user():
    """
    вход пользователя
    """
    global visits_count
    current_user = check_if_user_signed_in(request.cookies, db_sess)
    if current_user:
        return redirect("/apps")
    else:
        res = User.authenticate_user(request.form["login"], request.form["password"], db_sess)
        user = res[0]
        user_session = res[1]
        if None == user:
            return redirect("/sign_in/user_not_found")
        else:
            res = make_response(redirect("/"))
            res.set_cookie("user_secret", str(user_session.value),
                           max_age=60 * 60 * 24 * 365 * 2)
            return res


@app.route('/')
def landing():
    '''
    главная страница
    '''
    return redirect("/sign_in/Необходимо авторизоваться")


@app.route("/sign_in/<status>")
def sign_in(status):
    """
    окно входа в случае ошибки
    """
    param = {
        "status": status
    }
    current_user = check_if_user_signed_in(request.cookies, db_sess)
    if current_user:
        return redirect("/apps")
    else:
        param['yousername'] = "Ученик Яндекс.Лицея"
        param['title'] = 'Домашняя страница'
        param["array"] = [1, 2, 3, 4, 5]
        param["array_length"] = len(param["array"])
    return render_template('index.html', **param)


@app.route('/sign_up')
def sign_up():
    '''
    регистрация
    '''
    current_user = check_if_user_signed_in(request.cookies, db_sess)
    if current_user:
        return redirect("/apps")

    param = {}
    return render_template('sign_up.html', **param)


@app.route("/sign_up_user", methods=["post"])
def sign_up_user():
    """
    добавление регистрационных данных пользователся в базу данных
    """
    current_user = check_if_user_signed_in(request.cookies, db_sess)
    if current_user:
        return redirect("/apps")

    res = User.create(request.form["login"], request.form["password"], db_sess)
    user_session = res[1]
    http_res = make_response(redirect("/"))
    http_res.set_cookie("user_secret", str(user_session.value),
                        max_age=60 * 60 * 24 * 365 * 2)
    return http_res


def human_read_format(size):
    """
    перевод размера файла в человеко читабельный вид
    """
    if size < 1024:
        return f'{round(size)}Б'
    elif 1024 <= size < 1024 ** 2:
        return f'{round(size / 1024)}КБ'
    elif 1024 ** 2 <= size < 1024 ** 3:
        return f'{round(size / 1024 ** 2)}МБ'
    elif 1024 ** 3 <= size < 1024 ** 4:
        return f'{round(size / 1024 ** 3)}ГБ'


@app.route("/apps")
def apps():
    """
    магазин приложений
    """
    current_user = check_if_user_signed_in(request.cookies, db_sess)
    if not current_user:
        return redirect("/")
    projects = db_sess.query(Project).all()
    params = {
        "current_user": current_user,
        "projects": projects
    }
    return render_template("apps.html", **params)


@app.route("/app/<project_id>")
def app_detail(project_id):
    """
    страница приложения
    """
    current_user = check_if_user_signed_in(request.cookies, db_sess)
    if not current_user:
        return redirect("/")
    project = db_sess.query(Project).filter(Project.id == project_id).first()
    params = {
        "current_user": current_user,
        "project": project
    }
    return render_template("app_detail.html", **params)


@app.route("/download/<project_id>")
def download_app(project_id):
    '''
    скачивание приложения
    '''
    project = db_sess.query(Project).filter(Project.id == project_id).first()
    filename = project.file_path
    return send_from_directory(directory="media", filename=filename)


@app.route("/load_project", methods=['POST', 'GET'])
def load():
    """
    загрузка приложения на сервер
    """
    current_user = check_if_user_signed_in(request.cookies, db_sess)
    if request.method == 'GET':
        form = AddProject()
        Project()
        return render_template("my_prog.html", form=form)
    elif request.method == 'POST':
        f = request.files['file'].read()
        p = request.files['photo'].read()
        file_list = []
        file_name = f'{str(uuid.uuid4())}.{request.files["file"].filename.split(".")[-1]}'
        photo_name = request.files["photo"].filename
        if len(file_list) == 0: file_list.append(0)
        with open(f'static/img/{photo_name}', 'wb') as photo_file:
            photo_file.write(p)
        with open(f'media/{file_name}', 'wb') as file:
            file.write(f)
        file_size = human_read_format(getsize(f'static/img/{photo_name}'))
        form = AddProject()
        prog = Project(
            project_name=form.project_name.data,
            text=form.text.data,
            file_path=file_name,
            photo=photo_name,
            size=file_size
        )
        db_sess.add(prog)
        db_sess.commit()
        return redirect('/')


@app.route("/scoreboard")
def scoreboard():
    """
    страница со списком пользователей
    """
    current_user = check_if_user_signed_in(request.cookies, db_sess)
    params = {
        "users": User.all(db_sess),
        "current_user": current_user
    }
    return render_template("users.html", **params)


@app.route("/friends")
def friends():
    """
    ваши друзья
    """
    current_user = check_if_user_signed_in(request.cookies, db_sess)
    if not current_user:
        return redirect("/sign_in/для добавления в друзья нужно войти")
    params = {
        "users": map(lambda x: User.friendship_asked(x, db_sess), current_user.friends(db_sess)),
        "current_user": current_user
    }
    return render_template("friends.html", **params)


@app.route("/users/add_user/<user_id>")
def friend_user(user_id):
    """
    логика добавления друзей
    """
    current_user = check_if_user_signed_in(request.cookies, db_sess)
    if not current_user:
        return redirect("/sign_in/для добавления в друзья нужно войти")

    user = User.find_by_id(user_id, db_sess)

    Friendship.create_friendship(current_user, user, db_sess)

    params = {
        "users": map(lambda x: User.friendship_asked(x, db_sess), current_user.friends(db_sess)),
        "current_user": current_user
    }
    return render_template("friends.html", **params)


@app.route("/users/sign_out")
def sign_out():
    """
    выход пользователя
    """
    current_user = UserSession.sign_out(request.cookies, db_sess)
    return redirect("/")


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
