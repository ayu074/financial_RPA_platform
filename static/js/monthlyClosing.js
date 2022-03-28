function set_default_period() {
    // 猜测当前期间
    let curr_date = new Date();
    let curr_year = curr_date.getFullYear();
    let curr_month = curr_date.getMonth() + 1;
    if (curr_month == 1) {
        curr_month = 12;
        curr_year--;
    }else {
        curr_month--;
    }
        
    let year_selector = document.getElementById('select_year');
    for (i=2021; i<2026; i++) {
        let option_year = document.createElement('option');
        option_year.setAttribute('value', String(i));
        option_year.innerHTML = String(i);
        if (curr_year == i) {
            option_year.setAttribute('selected', 'selected');
        }
        year_selector.appendChild(option_year);
    }
    let month_selector = document.getElementById('select_month');
    for (i=1; i<13; i++) {
        let option_month = document.createElement('option');
        option_month.setAttribute('value', String(i));
        option_month.innerHTML = String(i);
        if (curr_month == i) {
            option_month.setAttribute('selected', 'selected');
        }
        month_selector.appendChild(option_month);
    }

}

class entity_task{
    constructor(raw_json, max_worker=2) {
        this.queue = [];
        this.max_worker = max_worker;
        this.current_worker = 0;
        this.done_task_count = 0;
        for (i=0; i<raw_json.length; i++) {
            this.queue[i] = {
                'id': raw_json[i]['r_id'],
                'status': -1,
            }
        }
    }

    get_operating_id() {
        if (this.current_worker < this.max_worker) {
            for (i=0; i<this.queue.length; i++) {
                if (this.queue[i]['status'] == -1) {
                    return this.queue[i]['id'];
                }
            }
            return null;
        }else {
        return -1;
        }
    }

    set_id_to_processing(process_id) {
        for(i=0; i<this.queue.length; i++){
            if (this.queue[i]['id'] == process_id) {
                this.queue[i]['status'] = 1;
                this.current_worker++;
                return 0;
            }
        }
        return -1;
    }

    set_id_to_init(init_id) {
        for(i=0; i<this.queue.length; i++){
            if (this.queue[i]['id'] == init_id) {
                this.queue[i]['status'] = 2;
                this.current_worker--;
                return 0;
            }
        }
        return -1;
    }

    set_id_to_finished(finished_id) {
        for(i=0; i<this.queue.length; i++) {
            if (this.queue[i]['id'] == finished_id) {
                this.queue[i]['status'] == 0;
                this.current_worker--;
                this.done_task_count++;
                return 0;
            }
        }
        return -1;
    }

    remove_id(del_id) { //todo 
        for(i=this.queue.length - 1; i>=0; i--) {
            if (this.queue[i]['id'] == del_id) {
                this.queue.splice(i, 1);
                return 0;
            }
        }
    }

}

function get_entity_list() {
    var get_entity_list_url = 'get_entity_list';
    var get_entity_list_request = new XMLHttpRequest();
    var entity_list_raw_json;
    get_entity_list_request.open('get', get_entity_list_url, false);
    get_entity_list_request.onreadystatechange = function() {
        if (get_entity_list_request.readyState == 4 && get_entity_list_request.status == 200) {
            entity_list_raw_json = JSON.parse(get_entity_list_request.responseText);
        }
    }
    get_entity_list_request.send();
    return entity_list_raw_json;
}

function get_function_list(entity_id) {
    var get_function_list_url = 'get_function_list';
    var get_function_list_request = new XMLHttpRequest();
    var function_json;
    if (entity_id != null) {
        get_function_list_url = get_function_list_url + '?entity_id=' + entity_id;
    }
    get_function_list_request.open('get', get_function_list_url, false);
    get_function_list_request.onreadystatechange = function() {
        if (get_function_list_request.readyState == 4 && get_function_list_request.status == 200) {
            function_json = JSON.parse(get_function_list_request.responseText);

        }
    }
    get_function_list_request.send();
    return function_json;
}

function get_query_value(query_name) {
    var reg = new RegExp("(^|&)" + query_name + "=([^&]*)(&|$)", "i")
    var r = window.location.search.substr(1).match(reg);
    if ( r != null) {
        return decodeURI(r[2]);
    }else {
        return null;
    }
}

function build_select_buttom(buttom_id) {
    var select_buttom = document.createElement('div');
    select_buttom.setAttribute('class', 'ckbx-style-15');
    var select_buttom_input = document.createElement('input');
    select_buttom_input.setAttribute('type', 'checkbox');
    select_buttom_input.setAttribute('class', 'ckbx-input');
    select_buttom_input.setAttribute('id', buttom_id);
    select_buttom_input.setAttribute('selected', '1');
    select_buttom_input.setAttribute('name', 'ckbx-style-15');
    //select_buttom_input.setAttribute('onclick', 'change_button_status(this);event.stopPropagation()');
    select_buttom_input.onclick = function (e) {
        e.stopPropagation();
        change_button_status(select_buttom_input);
    }
    var select_buttom_label = document.createElement('label');
    select_buttom_label.setAttribute('for', buttom_id);
    select_buttom.appendChild(select_buttom_input);
    select_buttom.appendChild(select_buttom_label);
    return select_buttom;
}

function change_button_status(curr_element) {
    var curr_selected_status = curr_element.getAttribute('selected');
    if (curr_selected_status == '0') {
        curr_element.setAttribute('selected', '1');
        clear_entity_info(curr_element);
    } else {
        curr_element.setAttribute('selected', '0');
    }
    return false; //stop propagation;
}

function change_function_status(func_ele) {
    // todo: 考虑上下联动
    var function_selected = func_ele.getAttribute('selected');
    if (function_selected == '0') {
        func_ele.setAttribute('selected', '1');
        func_ele.innerHTML = String(func_ele.innerHTML).replace('√', '×')
        func_ele.setAttribute('style', 'border: 1px dotted grey; color: grey;');
    }else{
        func_ele.setAttribute('selected', '0');
        func_ele.innerHTML = String(func_ele.innerHTML).replace('×', '√')
        func_ele.setAttribute('style', 'border: 1px solid rgb(0, 75, 0); color: green;');
    }
}

function expand_entity_info(entity_name_ele) {
    var entity_line_ele = entity_name_ele.parentNode;
    if (entity_line_ele.getAttribute('expanded') == '1') {
        entity_line_ele.setAttribute('expanded', '0');
        var line_id = entity_line_ele.getAttribute('id').replace('l', '');
        entity_func_list = get_function_list(line_id);
        var func_line = document.createElement('div');
        func_line.setAttribute('class', 'entity-col-func');
        func_line.setAttribute('unselectable', 'on');
        func_line.setAttribute('onselectstart', 'return false;');
        var func_wrapper = document.createElement('div');
        func_wrapper.setAttribute('class', 'entity-col-func-wrapper');
        for (i=0; i<entity_func_list.length; i++) {
            func_wrapper.appendChild(build_function_btn(line_id, entity_func_list[i]));
        }
        var close_btn = document.createElement('div');
        close_btn.setAttribute('class', 'entity-col-func-close');
        close_btn.setAttribute('unselectable', 'on');
        close_btn.setAttribute('onselectstart', 'return false;');
        close_btn.setAttribute('onclick', 'clear_entity_info(this)');
        close_btn.innerHTML = '取消选择并收起';
        func_line.appendChild(func_wrapper);
        func_line.appendChild(close_btn);
        entity_line_ele.appendChild(func_line);
        var line_children = entity_line_ele.children;
        for (i=0; i<line_children.length; i++) {
            if (line_children[i].getAttribute('class') == 'entity-col-desc'){
                var input_btn = line_children[i].firstChild.firstChild;
                if (input_btn.getAttribute('selected') == '1') {
                    input_btn.click();
                }
            }
        }
    }
}

function clear_entity_info(entity_line_close_ele) {
    var target_ele = entity_line_close_ele;
    while (target_ele.getAttribute("class") != 'entity-line') {
        target_ele = target_ele.parentNode;
        target_ele.setAttribute('expanded', '1')
    }
    var child_list = target_ele.children;
    for (i=0; i<child_list.length; i++) {
        if (child_list[i].getAttribute('class') == 'entity-col-func') {
            child_list[i].remove();
            return false;
        }
    }
}

function build_function_btn(entity_id, single_function_json) {
    var function_icon = document.createElement('div');
    function_icon.setAttribute('class', 'filter-function')
    if (entity_id != null){
        function_icon.setAttribute('id', entity_id + '-' + single_function_json['r_id']);
    }else {
        function_icon.setAttribute('id', single_function_json['r_id']);
    }
    function_icon.setAttribute('onclick', 'change_function_status(this)');
    function_icon.setAttribute('selected', '0');
    function_icon.innerHTML = '&nbsp' + single_function_json['r_chs_name'] + '&nbsp&nbsp&radic;&nbsp&nbsp';
    return function_icon;
}

function init_closing_data() {
    var entity_json = get_entity_list();
    var entity_table = document.getElementById('entity-table');
    for (i=0; i<entity_json.length; i++) {
        var entity_line = document.createElement('div');
        entity_line.setAttribute('id', 'l' + entity_json[i]['r_id']);
        entity_line.setAttribute('class', 'entity-line');
        entity_line.setAttribute('expanded', '1');
        entity_line.setAttribute('unselectable', 'on');
        entity_line.setAttribute('onselectstart', 'return false;');
        var entity_code = document.createElement('div');
        entity_code.setAttribute('class', 'entity-col-code');
        entity_code.innerHTML = entity_json[i]['r_code'];
        var entity_name = document.createElement("div");
        entity_name.setAttribute('class', 'entity-col-name');
        entity_name.innerHTML = entity_json[i]['r_chs_name'];
        entity_name.setAttribute('onclick', 'expand_entity_info(this)')
        var entity_name_arrow = document.createElement('span');
        entity_name_arrow.setAttribute('class', 'entity-col-name-arrow');
        entity_name_arrow.innerHTML = '&dArr;&nbsp;&nbsp;&nbsp;';
        entity_name.insertBefore(entity_name_arrow, entity_name.lastChild);
        var entity_desc = document.createElement('div');
        entity_desc.setAttribute('class', 'entity-col-desc');
        select_b = build_select_buttom(entity_json[i]['r_id']);
        entity_desc.appendChild(select_b);
        entity_line.appendChild(entity_code);
        entity_line.appendChild(entity_name);
        entity_line.appendChild(entity_desc);
        entity_table.appendChild(entity_line);
        if (entity_json[i]['r_is_sub'] == '0') {
            select_b.children[0].click();
        }

    }
    var init_function_json = get_function_list(null);
    var function_wrapper = document.getElementById('function-wrapper');
    for (i=0; i<init_function_json.length; i++) {
        function_wrapper.appendChild(build_function_btn(null, init_function_json[i]));
    }
    return entity_json;
}

function show_select_text(target_ele) {
    target_ele.innerHTML = '全选/不选';
}
function unshow_select_text(target_ele) {
    target_ele.innerHTML = '是否结账';
}
function select_all() {
    var all_inputs = document.getElementsByClassName('ckbx-input');
    for (i=0; i<all_inputs.length; i++){
    }
    var all_selected = 0;
    for (i=0; i<all_inputs.length; i++){
        if (all_inputs[i].getAttribute('selected') == '1') {
            all_selected = 1;
            break;
        }
    }
    if (all_selected == 0) {
        for(j=0; j<all_inputs.length; j++){
            if (all_inputs[j].getAttribute('selected') == '0'){
            all_inputs[j].click();
            }
        }
    }else {
        for(j=0; j<all_inputs.length; j++){
            if (all_inputs[j].getAttribute('selected') == '1'){
            all_inputs[j].click();
            }
        }
    }
}

function build_voucher_single(entity_ele, current_task) {
    let entity_id = entity_ele.getAttribute('id');
    let build_request = new XMLHttpRequest();
    var result_text;
    build_request.open('POST', 'build_voucher', true);
    build_request.setRequestHeader('content-type', 'application/x-www-form-urlencoded');
    build_request.onreadystatechange = function() {
        if (build_request.readyState == 4 && build_request.status == 200) {
            result_text = build_request.responseText;
            if (result_text == '0') {
                entity_ele.innerHTML = '已成功';
                current_task.set_id_to_finished(entity_id);
                return 0;
            }else {
                entity_ele.innerHTML = '重新获取';
                current_task.set_id_to_init(entity_id);
                entity_ele.setAttribute('onclick', 'build_voucher_single(this, current_task)');
                return -1;
            }
        }
    }
    var entity_line = document.getElementById('l' + entity_id);
    if (entity_line.getAttribute('expanded') == '1') {
        var gen_func_list = document.getElementById('function-wrapper').children;
        var func_str = '';
        for (f=0; f<gen_func_list.length; f++) {
            if (gen_func_list[f].getAttribute('selected') == '0') {
                func_str = func_str + gen_func_list[f].getAttribute('id') + ';';
            }
        }
    }else {
        var gen_func_list = entity_line.lastChild.firstChild.children;
        var func_str;
        for (f=0; f<gen_func_list.length; f++) {
            if (gen_func_list[f].getAttribute('selected') == '0') {
                func_str = func_str + gen_func_list[f].getAttribute('id').split('-')[1] + ';';
            }
        }
    }

    var closing_payload;
    closing_payload = 'entity_id=' + entity_id +
                     '&select_year=' + document.getElementById('select_year').value + 
                     '&select_month=' + document.getElementById('select_month').value +
                     '&workorder_id=' + get_query_value('workorder_id') +
                     '&func_list_str=' + func_str;
    build_request.send(closing_payload);
    entity_ele.innerHTML = '正在获取';
    current_task.set_id_to_processing(entity_id);
}

function submit_closing(current_task) {
    var all_entity_eles = document.getElementsByClassName('ckbx-input');

    var generate_work = new XMLHttpRequest();
    generate_work.open('POST', 'generate_workorder', false);
    generate_work.setRequestHeader('content-type', 'application/x-www-form-urlencoded');
    generate_work.onreadystatechange = function() {
        if (generate_work.readyState == 4 && generate_work.status == 200) {
            console.log(generate_work.responseText);
        }
    }
    generate_work.send('select_year=' + document.getElementById('select_year').value + 
    '&select_month=' + document.getElementById('select_month').value +
    '&workorder_id=' + get_query_value('workorder_id'));

    for (i=all_entity_eles.length - 1; i>=0; i--) {
        if (all_entity_eles[i].getAttribute('selected') == '1') {
            current_task.remove_id(all_entity_eles[i].getAttribute('id'));
            document.getElementById('l' + all_entity_eles[i].getAttribute("id")).remove();

        }else {
            all_entity_eles[i].parentNode.parentNode.setAttribute('id', all_entity_eles[i].getAttribute("id"));
            all_entity_eles[i].parentNode.parentNode.innerHTML = '正在排队...';
        }
    }
    var pull_all_entities = setInterval(function() {
        if (current_task.done_task_count == current_task.queue.length) {
            clearInterval(pull_all_entities);
            return window.location.href = '/voucherView?workorder_id=' + get_query_value('workorder_id');
        }else if (current_task.get_operating_id() == -1){}
        else{
            build_voucher_single(document.getElementById(current_task.get_operating_id()), current_task);
        }
    }, 1000)

}