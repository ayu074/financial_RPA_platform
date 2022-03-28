function set_module_spec() {
    var module_name = document.getElementById('module_name').innerHTML;
    // 存管费利息计提模块, 暂时弃用
    if (module_name == 'interestAccrual') {
        var interest_ledger = document.createElement('div');
        interest_ledger.id = 'ledger';
        interest_ledger.class = 'filter-btn';
        interest_ledger.style = 'text-align:center; display: block; margin-right: 3%; float:right; width:5%; padding:3px;';
        interest_ledger.innerHTML = '台账';
        var interest_table = document.getElementsByClassName('worksheet-head')[0];
        var interest_worksheet = document.getElementById('worksheet');
        interest_worksheet.insertBefore(interest_table,interest_create_new);
        return 0;
    }
}