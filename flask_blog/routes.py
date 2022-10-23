import os
import secrets
from datetime import datetime
from PIL import Image
from flask import *
from flask_mail import Message
from flask_blog import app, db, login_manager, mail
from flask_blog.forms import (RegistrationForm, LoginForm, UpdateAccountForm, 
                                PostForm, CommentForm, UpdatePostForm, RequestResetForm, ResetPasswordForm)
from flask_blog.models import User, Post, Comment
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

# create user loader for the login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id) 

@app.route("/")
@app.route("/home")
def home_page():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    date_format = "%Y-%d-%m %H:%M:%S.%f"
    return render_template('home.html', posts=posts, date_format=date_format, a=datetime)

@app.route("/about")
def about_page():
    return render_template('about.html')

@app.route("/sign_up", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():       
        new_user = User(
            email = form.email.data,
            username = form.username.data,
            password = generate_password_hash(password=form.password.data, method="pbkdf2:sha256", salt_length=8)
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Your acount has been created. You can login now !!!.', 'success')
        
        return redirect(url_for('sign_in'))

    return render_template('register.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def sign_in():
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=form.remember.data)
            global next_page
            return redirect(next_page) if next_page else redirect(url_for('home_page'))
        else:
            flash("Invalid email or password !!!", "danger")
    
    if request.method == 'GET':
        next_page = request.args.get('next')
        
    return render_template('login.html', form=form)

@app.route('/logout')
def sign_out():
    logout_user()
    flash("You've been logged out !!!", 'success')
    return redirect(url_for('home_page'))

def save_photo(form_photo):
    random_hex = secrets.token_hex(8)
    
    # separating file extention from the filename using the os module
    _, f_ext = os.path.splitext(form_photo.filename)
    
    # creating random filenames for each users file to avoid similar filenames
    photo_fn = f"{random_hex}{f_ext}"

    # creating the path for the folder where user images will be stored 
    photo_path = os.path.join(app.root_path, 'static/images', photo_fn)

    # resizing image(in terms of the space it occupies on the HD) to increase efficiency of the website using the PIL(pillow) module.
    output_size = (125, 125)
    i = Image.open(form_photo)
    i.thumbnail(output_size)

    ##### deleting proflie photo after it has been replaced with another one #####
    if form_photo and current_user.image_file != 'default.jpg':
        previous_img_f = current_user.image_file
        previous_img_path = os.path.join(app.root_path, 'static/images', previous_img_f)
        os.remove(previous_img_path)

    # saving photo at the specified location
    i.save(photo_path)
    
    return photo_fn 

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    # autofilling form with user data
    form = UpdateAccountForm(
        email = current_user.email,
        username = current_user.username
    )
    if form.validate_on_submit():
        if form.photo.data:
            photo_fn = save_photo(form.photo.data)
            current_user.image_file = photo_fn
            db.session.commit()
            c = True
        
        a = current_user.email
        b = current_user.username
        current_user.email = form.email.data
        current_user.username = form.username.data
        db.session.commit()
        if a != form.email.data or b != form.username.data or c: 
            flash('Your account info has been updated !!!', 'success')
    image_file = url_for('static', filename=f'images/{current_user.image_file}') 
    return render_template('account.html', image_file=image_file, form=form)

@app.route("/make-post", methods=['GET', 'POST'])
@login_required
def make_post():
    form = PostForm()
    if form.validate_on_submit():
        new_post = Post(
            content = form.content.data,
            author = current_user
        )
        db.session.add(new_post)
        db.session.commit()
        flash('Your Post has been made !!!', 'success')
        return redirect(url_for('home_page'))
    return render_template('make_post.html', form=form)

@app.route("/edit-post/<int:post_id>", methods=['GET', 'POST'])
def edit_post(post_id):
    post_to_edit = Post.query.get(post_id)
    form = UpdatePostForm(
        content = post_to_edit.content
    )
    if form.validate_on_submit():
        post_to_edit.content = form.content.data
        db.session.commit()
        return redirect(url_for('home_page'))
    return render_template('edit_post.html', form=form, post=post_to_edit)

@app.route("/view-post/<int:post_id>", methods=['GET', 'POST'])
def view_post(post_id):
    form = CommentForm()
    requested_post = db.session.query(Post).get(post_id)
    if form.validate_on_submit():
        if current_user.is_authenticated:
            new_comment = Comment(
                parent_post = requested_post,
                comment_author = current_user,
                text = form.comment.data
            )
            db.session.add(new_comment)
            db.session.commit()
            flash("Your comment has been added!!!", "success")
            return redirect(url_for('view_post', post_id=requested_post.id))
        else:
            flash("You need to login to comment!!!", "danger")
    
    return render_template('view_post.html', form=form, post=requested_post)

@app.route("/delete-post/<int:post_id>", methods=['GET', 'POST'])
def delete_post(post_id):
    post_to_delete = Post.query.get(post_id)
    if request.method == 'POST':
        db.session.delete(post_to_delete)
        db.session.commit()
    flash("Your post has been deleted!!!", "success")
    return redirect(url_for('home_page'))

@app.route("/delete-comment/<int:comment_id>/<int:post_id>", methods=['GET', 'POST'])
def delete_comment(comment_id, post_id):
    comment_to_delete = Comment.query.get(comment_id)
    db.session.delete(comment_to_delete)
    db.session.commit()
    flash("Your comment has been deleted!!!", "success")
    return redirect(url_for('view_post', post_id=post_id))

@app.route("/user/<string:username>")
def user_posts(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(author=user).\
            order_by(Post.date_posted.desc()).\
            paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)

def send_reset_mail(user):
    '''creating a function to send mails to users using the flask mail class'''
    token = user.get_reset_token()
    msg = Message("Password Reset Request", 
    sender="avogadromartins@gmail.com", 
    recipients=[user.email])
    msg.body = f"""To reset your password visit the following Link
{ url_for('reset_token', token=token, _external=True) }

if you did not make this request then simply ignore this email and no changes will be made
"""
    mail.send(msg)

@app.route("/Reset-Password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect('home_page')
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_mail(user)
        flash("An email has been sent to you with instructions to reset your password", 'info')
        return redirect(url_for('sign_in'))
    return render_template('reset_request.html', form=form)

@app.route("/Reset-Password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    form = ResetPasswordForm()
    if current_user.is_authenticated:
        return redirect('home_page')
    user = User.verify_reset_token(token)
    if user == None:
        flash('This is an invalid or expired token', 'danger')
        return redirect(url_for('reset_request'))
    if form.validate_on_submit():       
        user.password = generate_password_hash(password=form.password.data, method="pbkdf2:sha256", salt_length=8)
        db.session.commit()
        flash('Your password has been changed. You can login now !!!.', 'success')
        return redirect(url_for("sign_in"))
    return render_template('reset_token.html', form=form)


