from flask import render_template
from website.website import app
from db.db_creator import User
from db.db_main import DataBaseMain


db_main = DataBaseMain()

@app.route('/')
def hello_world():
    return "My website"

@app.route("/user/<id>")
def make_checking(id):
    table_user = db_main.get_values_user(id)
    print(table_user)
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    if table_user:
        index, name, link_imdb, link_image, date_birth, date_death, desc = table_user
        return f"Check username: {id}; description: {desc}"
    return 'Empty values'