function set_card(card_detail) {
    /*
    通过接口获取模块信息，模块信息标准如下：
    {
        id: str;
        name: str;
        desc: str;
        url: str;
        img_locale: str;
    }
    */
    //构造卡片轮廓
    let func_card = document.createElement('div');
    func_card.setAttribute('class', 'card');
    func_card.setAttribute('id', card_detail['id'])
    //生成卡片抬头
    let func_title = document.createElement('h2');
    func_title.setAttribute('class', 'func-title');
    func_title.innerHTML = card_detail['name'];
    //生成卡片解释
    let func_detail = document.createElement('p');
    func_detail.setAttribute('class', 'func-detail');
    func_detail.innerHTML = card_detail['desc'];
    //生成卡片链接
    let func_link = document.createElement('p');
    func_link.setAttribute('class', 'func-link');
    let func_a = document.createElement('a');
    func_a.href = card_detail['url'];
    func_a.innerHTML = '点击进入';
    func_link.appendChild(func_a);
    //生成卡片图片
    let func_img = document.createElement('img')
    func_img.setAttribute('class', 'func-img');
    func_img.src = card_detail['img_locale'];
    //拼接卡片
    func_card.appendChild(func_title);
    func_card.appendChild(func_detail);
    func_card.appendChild(func_link);
    func_card.appendChild(func_img);
    return func_card;
}

function get_card_list() {
    // var test_card_list = [
    //     {
    //         'id': '001',
    //         'name': '总部增值税收缴',
    //         'desc': '自动收缴总部部门的增值税、附加税余额，并生成往来',
    //         'url': '/vatCollection/main',
    //         'img_locale': '/static/img/tax.png'
    //     },
    //     {
    //         'id': '002',
    //         'name': '利息、存管费计提',
    //         'desc': '根据金仕达每日余额生成存管费、利息凭证及报表',
    //         'url': '/interestAccrual/main',
    //         'img_locale': '/static/img/interest.png'
    //     }
    // ];
    var test_card_list;
    var card_request = new XMLHttpRequest();
    card_request.open('GET', '/getModule', true)
    card_request.onreadystatechange = function() {
        if (card_request.readyState == 4 && card_request.status == 200) {
            test_card_list = JSON.parse(card_request.responseText);
            let func_area = document.getElementById('func-area');
            for(i=0; i<test_card_list.length; i++) {
                let new_card = set_card(test_card_list[i]);
                func_area.appendChild(new_card);
            }
        }
    }
    card_request.send();
    return 0;
}