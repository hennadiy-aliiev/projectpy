import os
from datetime import datetime

from flask import render_template, flash, redirect, url_for, \
    request, session, g, flash, send_from_directory, Response
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename

from app import app, db, lm                      
from config import SALT_EMAIL_KEY, SALT_RECOVERY_KEY, UPLOAD_FOLDER, \
    RELATIVE_UPLOAD_FOLDER, DEFAULT_AVATAR, POSTS_PER_PAGE, MAX_SEARCH_RESULTS
from .forms import SignInForm, SignUpForm, EmailForm, PasswordForm, EditForm, PostForm, SearchForm
from .models import User, Post
from .util.avatars import allowed_file, allowed_size
from .util.emails import signup_notification, reset_notification, follower_notification
from .util.online_users import mark_online, get_user_last_activity, get_online_users
from .util.security import ts
from .util.redirects import get_redirect_target, redirect_back


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()                                    
        db.session.add(g.user)                                        
        db.session.commit()                        
        g.search_form = SearchForm()
        mark_online(g.user.nickname) 


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('sign_in'))


@app.route('/signin', methods=['GET', 'POST'])                             
def sign_in():
    next = get_redirect_target()
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = SignInForm()                                                           
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()     
        if user is None:
            flash('Email not found!', 'danger')
            return redirect(url_for('sign_in'))
        if user.email_confirmed:                              
            if user.is_correct_password(form.password.data):
                login_user(user)
                return redirect_back('sign_in')
            flash('Incorrect password!', 'danger')
            return redirect_back('sign_in') 
        flash('This account is not activated! Check your email box for verification letter.', 'info')
    
    return render_template('signin.html', next=next, title='SignIn', form=form)


@app.route('/signup', methods=['GET', 'POST'])                                 
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            flash('This email is already in use!', 'warning')
            return redirect(url_for('sign_up')) 
        nickname = form.email.data.split('@')[0]
        nickname = User.make_unique_nickname(nickname)            
        user = User(email=form.email.data, password=form.password.data, nickname=nickname)
        
        db.session.add(user)
        db.session.commit()
        
        token = ts.dumps(user.email, salt=SALT_EMAIL_KEY)
        
        confirm_url = url_for('confirm_email', token=token, _external=True)
        
        signup_notification(user, confirm_url)
        
        flash('Email confirmation was sent to your entered email.', 'info')             
        return redirect(url_for('sign_in'))
    
    return render_template('signup.html', title='SignUp', form=form)


@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = ts.loads(token, salt=SALT_EMAIL_KEY, max_age=86400)
    except:
        abort(404)
    user = User.query.filter_by(email=email).first_or_404()
    user.email_confirmed = True
    db.session.add(user)
    db.session.commit()
    flash('Your account verification has been successfully processed. WELCOME!', 'success')
    return redirect(url_for('sign_in'))


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):  

    online_users = get_online_users()
    
    new_online_users = {online_user.decode('utf-8') for online_user in online_users}
    
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, timestamp=datetime.utcnow(), author=g.user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!', 'success')
        return redirect(url_for('index'))    
    posts = Post.query.order_by(Post.timestamp.desc()). \
            paginate(page, POSTS_PER_PAGE, False)
    
    return render_template('index.html', title='HAB', user=g.user, 
                            online_users=new_online_users, form=form, posts=posts)


@app.route('/search', methods=['POST'])
@login_required
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_results', query=g.search_form.search.data))


@app.route('/search_results/<query>')                                             
@login_required
def search_results(query):
    results = Post.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    
    return render_template('search_results.html', query=query, results=results)


@app.route('/reset', methods=['GET', 'POST'])
def reset():
    form = EmailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()   
        if user is None:
            flash('Email not found!', 'danger')
            return redirect(url_for('reset'))
        
        token = ts.dumps(user.email, salt=SALT_RECOVERY_KEY)
        
        recover_url = url_for('reset_with_token', token=token, _external=True)
        
        reset_notification(user, recover_url)                          
        
        flash('Password reset request was sent to your entered email.', 'info')  
        return redirect(url_for('sign_in'))
    
    return render_template('reset.html', title='Reset', form=form)


@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    try:
        email = ts.loads(token, salt=SALT_RECOVERY_KEY, max_age=86400)
    except:
        abort(404)
    form = PasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first_or_404()
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        flash('Your password has been successfully changed. WELCOME!', 'success')
        return redirect(url_for('sign_in'))
    
    return render_template('reset_with_token.html', title='Reset', form=form, token=token)


@app.route('/user/<nickname>')                                              
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page=1):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User {} not found!'.format(nickname), 'danger')
        return redirect(url_for('index'))
    posts = user.posts.order_by(Post.timestamp.desc()). \
            paginate(page, POSTS_PER_PAGE, False)
    
    return render_template('user.html', title='Profile', user=user, posts=posts)


@app.route('/edit', methods=['GET', 'POST'])                              
@login_required
def edit():                                                     
    form = EditForm()
    new_nickname = form.nickname.data
    user = User.query.filter_by(nickname=new_nickname).first()
    if form.validate_on_submit():
        if user is not None and g.user.nickname != new_nickname:
            flash('This nickname is already in use!', 'warning')
            return render_template('edit.html', form=form)
        g.user.nickname = new_nickname
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.', 'success')
    elif request.method != 'POST':
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    
    return render_template('edit.html', title='Edit', user=g.user, form=form)


@app.route('/uploader', methods=['GET', 'POST'])                      
def upload_file():  
    if request.method == 'POST':
        # check if the post request has the file part                            
        if 'file' not in request.files:
            flash('No file part!', 'danger')                                               
            return redirect(url_for('edit'))
        f = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if f.filename == '':
            flash('No selected file!', 'danger') 
            return redirect(url_for('edit'))
        
        if f and allowed_file(f.filename):
            check_length = request.content_length
            if not allowed_size(check_length):
                flash('Your image size is too big!', 'warning')
                return redirect(url_for('edit'))
            filename = secure_filename(f.filename)
            
            check_name = '{}{}'.format(RELATIVE_UPLOAD_FOLDER, filename)  
            user = User.query.filter_by(avatar=check_name).first()
            if user is not None:     
                filename = User.make_unique_image_name(filename)
                       
            if g.user.avatar != DEFAULT_AVATAR:
                os.remove(os.path.join(os.getcwd(), 'app' + g.user.avatar))

            f.save(os.path.join(UPLOAD_FOLDER, filename))
            g.user.avatar = '{}{}'.format(RELATIVE_UPLOAD_FOLDER, filename)
            db.session.add(g.user)
            db.session.commit()
            flash('Your avatar was changed.', 'success')
            return redirect(url_for('edit'))
        flash('Your file extension is not allowed!', 'warning')
        return redirect(url_for('edit'))


@app.route('/subscriptions')                                                
@app.route('/subscriptions/<int:page>')
@login_required
def subscriptions(page=1):                                                     
    posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)    
    
    return render_template('subscriptions.html', title='Subscriptions', user=g.user, posts=posts)


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    post = Post.query.get(id)
    if post is None:
        flash('Post not found!', 'danger')
        return redirect(url_for('index'))
    if post.author.id != g.user.id:
        flash('You cannot delete this post!', 'warning')
        return redirect(url_for('index'))
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted.', 'success')
    return redirect(url_for('index'))


@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User {} not found!'.format(nickname), 'danger')
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t follow yourself!', 'warning')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.follow(user)
    if u is None:
        flash('Cannot follow {}!'.format(nickname), 'warning')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You are now following {}.'.format(nickname), 'success')
    
    follower_notification(user, g.user)
    
    return redirect(url_for('user', nickname=nickname))


@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User {} not found!'.format(nickname), 'danger')
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t unfollow yourself!', 'warning')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot unfollow {}!'.format(nickname), 'warning')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following {}.'.format(nickname), 'success')
    
    return redirect(url_for('user', nickname=nickname))
