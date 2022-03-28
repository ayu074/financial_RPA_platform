function get_user_name() {
    var user_id = document.cookie.match(/(?<=owner=).*(?=;+?)/g)[0];
    var user_name = '登录';
    var username_xhr = new XMLHttpRequest();
    username_xhr.onreadystatechange = function () {
        if (username_xhr.readyState == 4 && username_xhr.status == 200) {
            user_name = username_xhr.responseText;
        }
    }
    username_xhr.open('get', '/getUserName?owner=' + user_id, false);
    username_xhr.send();
    return user_name;
}

function append_change_pwd_btn() {
    if (document.cookie != null) {
        var user_div = document.getElementById('user');
        user_div.removeAttribute('onclick')
        var change_pwd_btn = document.createElement('div');
        change_pwd_btn.setAttribute('class', 'dropdown-content');
        change_pwd_btn.setAttribute('onclick', "jump_to_url('/change_pwd')");
        change_pwd_btn.innerHTML = '修改密码';
        user_div.appendChild(change_pwd_btn);
        var logout_btn = document.createElement('div');
        logout_btn.setAttribute('class', 'dropdown-content');
        logout_btn.setAttribute('onclick', "jump_to_url('/logout')");
        logout_btn.setAttribute('style', "top: 200%;");
        logout_btn.innerHTML = '退出登录';
        user_div.appendChild(logout_btn);
        return 0;
    }
}

function jump_to_url(url_str, new_window='0') {
    if (new_window == 0) {
        return window.open(url_str);
    } else {
        return window.location.href = url_str;
    }
}

function get_current_module_prefix() {
    let current_url = window.location.href;
    let module_str = String(current_url).match(/(?<=http:\/\/.*?.\/).*?(?=\/.*)/)[0];
    return module_str;
}

function sleep(misec) {
    for(var t = Date.now(); Date.now() - t <= misec;);
}