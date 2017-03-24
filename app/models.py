import sys
import flask_whooshalchemy as whooshalchemy

from sqlalchemy.ext.hybrid import hybrid_property

from app import app, db, bcrypt


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
    )


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), index=True, unique=True)
    email_confirmed = db.Column(db.Boolean, default=False) 
    _password = db.Column(db.String(120))
    nickname = db.Column(db.String(64), index=True, unique=True)
    posts = db.relationship('Post', backref='author', lazy='dynamic')   
    avatar = db.Column(db.String(140), default='/static/uploads/default_av_image.png')
    about_me = db.Column(db.String(140))                              
    last_seen = db.Column(db.DateTime)
    followed = db.relationship(
        'User', 
        secondary=followers, 
        primaryjoin=(followers.c.follower_id == id), 
        secondaryjoin=(followers.c.followed_id == id), 
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
        )
                                                                        
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def _set_password(self, plaintext):
        self._password = bcrypt.generate_password_hash(plaintext)

    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname=nickname).first() is None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname=new_nickname).first() is None:
                break
            version += 1
        return new_nickname

    @staticmethod
    def make_unique_image_name(filename):                       
        version = 2
        while True:
            new_image_name = str(version) + filename
            check_new_name = '/static/uploads/{}'.format(new_image_name)
            if User.query.filter_by(avatar=check_new_name).first() is None:
                break
            version += 1
        return new_image_name

    def is_correct_password(self, plaintext):
        return bcrypt.check_password_hash(self._password, plaintext)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id 
                == user.id).count() > 0  

    def followed_posts(self):                         
        return Post.query.join(followers, (followers.c.followed_id == Post.user_id)) \
        .filter(followers.c.follower_id == self.id).order_by(Post.timestamp.desc())

    def get_id(self):
        try:
            return unicode(self.id)  
        except NameError:
            return str(self.id)  
            
    def __repr__(self):
        return '<User {}>'.format(self.email)


class Post(db.Model):
    __searchable__ = ['body']

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(500))                                      
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


whooshalchemy.whoosh_index(app, Post)
