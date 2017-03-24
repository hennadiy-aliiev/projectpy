from itsdangerous import URLSafeTimedSerializer

from app import app
from config import SECRET_KEY                     


ts = URLSafeTimedSerializer(SECRET_KEY)
