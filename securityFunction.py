import os
import sys
import re
import base64
import hashlib
import random
import time

from flask import request, redirect

from SqlFunction import create_session, generate_key
from SqlFunction import tUser
from redisFunction import set_redis_connection, shut_all_redis_connection


def hash_password(clean_password: str) -> str:
    """
    double md5
    :param clean_password: de-salted pwd
    :return:
    """
    md5 = hashlib.md5()
    md5.update(clean_password.encode('utf-8'))
    second_str = md5.hexdigest()
    md5.update(second_str.encode('utf-8'))
    return md5.hexdigest()


def decode_salt_password(raw_password: str, prefix_salt=4) -> str:
    """
    default: 4 digits random prefix salt
    :param raw_password: posted str from website
    :param prefix_salt:
    :return:
    """
    salted_pwd = str(base64.urlsafe_b64decode(raw_password))
    clean_pwd = salted_pwd[prefix_salt:]
    return clean_pwd[2:-1]


def _add_user(user_name: str, user_chs_name: str, default_pwd='1') -> int:
    """
    only applied in scripted
    :param user_name:
    :param default_pwd:
    :return:
    """
    add_user_session = create_session()
    try:
        add_user_session.add(tUser(r_id=generate_key(),
                                   r_name=user_name,
                                   r_chs_name=user_chs_name,
                                   r_hash_pwd=hash_password(default_pwd)))
        add_user_session.commit()
        add_user_session.close()
        return 0
    except Exception as e:
        print(e)
        return -1


def update_pwd(raw_password: str, user_id: str) -> int:
    curr_raw_pwd = decode_salt_password(raw_password=raw_password)
    curr_md5 = hash_password(curr_raw_pwd)
    update_pwd_session = create_session()
    try:
        update_pwd_session.query(tUser).filter(tUser.r_name == user_id).update(
            {tUser.r_hash_pwd: str(curr_md5)}
        )
        update_pwd_session.commit()
        update_pwd_session.close()
        return 0
    except Exception as e:
        print(e)
        return -1


def check_pwd(raw_password: str, user_id: str) -> int:
    """

    :param raw_password:
    :param user_id: distinct user name
    :return:
    """
    curr_raw_pwd = decode_salt_password(raw_password=raw_password)
    curr_md5 = hash_password(curr_raw_pwd)
    pwd_check_session = create_session()
    local_md5 = pwd_check_session.query(tUser.r_hash_pwd).filter(tUser.r_id == user_id).first()
    pwd_check_session.close()
    if local_md5:
        if local_md5[0] == curr_md5:
            return 0
        else:
            return 1
    else:
        return -1


def generate_cookies(user_id: str) -> str:
    prefix = str(random.randint(1000, 9999))
    appendix = str(int(time.time()))
    cookies_md5 = hashlib.md5()
    cookies_md5.update(str(prefix + appendix).encode('utf-8'))
    cookies_str = cookies_md5.hexdigest()
    redis_session = set_redis_connection()
    redis_session.set(user_id, cookies_str)
    # redis_session.set(user_id, cookies_str, ex=19600)
    shut_all_redis_connection()
    return cookies_str


def check_cookies(user_id: str, user_cookies: str) -> int:
    redis_session = set_redis_connection()
    if redis_session.get(user_id) == user_cookies:
        result = 0
    else:
        result = -1
    shut_all_redis_connection()
    return result


def set_auto_login(ip: str, user_id: str) -> int:
    redis_session = set_redis_connection()
    redis_session.set(ip, user_id)
    shut_all_redis_connection()
    return 0


def clean_auto_login(ip: str) -> int:
    redis_session = set_redis_connection()
    redis_session.delete(ip)
    shut_all_redis_connection()
    return 0


def get_auto_login_owner(ip: str) -> [str, None]:
    redis_session = set_redis_connection()
    user_id = redis_session.get(ip)
    if user_id:
        return user_id
    else:
        return None


def login_status_check():
    owner = request.cookies.get('owner')
    token = request.cookies.get('token')
    if owner is None:
        return redirect('/login')
    else:
        if check_cookies(owner, token) != 0:
            return redirect('/login')


def viewer_auth_check(user_id) -> int:
    user_session = create_session()
    user_info = user_session.query(tUser).filter(tUser.r_id == user_id).first()
    if not user_info:
        return -1
    if not user_info.r_admin_auth:
        return -1
    if 'viewer' in user_info.r_admin_auth:
        user_session.close()
        return 0
    else:
        user_session.close()
        return -1


if __name__ == '__main__':
    pass