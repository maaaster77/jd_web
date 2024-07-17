from jd import app

#

#
#
# class BlackKeyword(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), nullable=False, unique=True)
#     is_selected = db.Column(db.Boolean, default=False)
#
#     def __repr__(self):
#         return f'<BlackKeyword {self.name}>'
#
#
# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))
#
#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         user = User.query.filter_by(username=username).first()
#         if user and user.password == password:
#             login_user(user)
#             return redirect(url_for('index'))
#     return render_template('login.html')
#
#
# @app.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for('index'))
#
#
# @app.route('/update_keyword_selection', methods=['POST'])
# def update_keyword_selection():
#     keyword_id = request.form['keyword_id']
#     is_selected = request.form['is_selected'] == 'true'
#     keyword = Keyword.query.get(keyword_id)
#     keyword.is_selected = is_selected
#     db.session.commit()
#     return jsonify({'message': 'Keyword selection updated'})
#
#
# @app.route('/add_keyword', methods=['POST'])
# def add_keyword():
#     name = request.form['name']
#     keyword = BlackKeyword(name=name)
#     db.session.add(keyword)
#     db.session.commit()
#     return jsonify({'message': 'Keyword added'})
#
#
# @app.route('/delete_keyword', methods=['POST'])
# def delete_keyword():
#     keyword_id = request.form['keyword_id']
#     keyword = Keyword.query.get(keyword_id)
#     db.session.delete(keyword)
#     db.session.commit()
#     return jsonify({'message': 'Keyword deleted'})
#
#
# @app.route('/')
# def index():
#     keywords = BlackKeyword.query.all()
#     return render_template('blackwords.html', keywords=keywords)
app.ready()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
