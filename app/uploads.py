import time
import os
from sqlalchemy.exc import IntegrityError

from flask import current_app, flash
from werkzeug.utils import secure_filename

from app import db
from app.models import UploadedImage
from config import basedir


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def set_filename(filename):
    list = filename.rsplit('.', 1)
    return list[0] + '_' + str(int(time.time()) % 100000) + '.' + list[1]


def check_files(images):
    for img in images:
        if not allowed_file(img.filename):
            flash('png, jpg, jpeg, gif 형식으로 올려주시기 바랍니다.')
            return False
    return True


def upload_files(images, service_id=-1, event_id=-1, ads_id=-1, hos_id=-1):
    for img in images:
        filename = secure_filename(img.filename)
        if allowed_file(filename):
            target = os.path.join(basedir, 'app/static/img/uploads/')
            if not os.path.isdir(target):
                os.mkdir(target)
            filename = set_filename(filename)
            img.save("/".join([target, filename]))

            if service_id >= 0:
                img_url = UploadedImage(filename=filename, service_id=service_id)
            elif event_id >= 0:
                img_url = UploadedImage(filename=filename, event_id=event_id)
            elif ads_id >= 0:
                if UploadedImage.query.filter_by(ad_id=ads_id).first():
                    img_url = UploadedImage.query.filter_by(ad_id=ads_id).first()
                    img_url.filename = filename
                else:
                    img_url = UploadedImage(filename=filename, ad_id=ads_id)
            else:
                img_url = UploadedImage(filename=filename, hos_id=hos_id)
            db.session.add(img_url)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
