from config import ALLOWED_EXTENSIONS


def allowed_file(filename):                                        
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_size(fl):
    size = 2 * 1024 * 1024
    return fl < size
