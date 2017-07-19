/**
 * Created by jaewoo on 2017. 7. 19..
 */
var IMP = window.IMP;
IMP.init('imp63004671');

$(function () {
    $('#pointSelector').on('change', function () {
        $('#btn').show();
    });

    $('#btn').on('click', function () {
        var select_value = $('#pointSelector').val();

        // use the value here
        IMP.request_pay({
            pg: 'html5_inicis',
            pay_method: 'card',
            merchant_uid: 'merchant_' + new Date().getTime(),
            name: '주문명:결제테스트',
            amount: select_value,
            buyer_tel: '010-1234-5678'
        }, function (rsp) {
            var msg = '';
            if (rsp.success) {
                msg = '결제가 완료되었습니다.';
                msg += '고유ID : ' + rsp.imp_uid;
                msg += '상점 거래ID : ' + rsp.merchant_uid;
                msg += '결제 금액 : ' + rsp.paid_amount;
                msg += '카드 승인번호 : ' + rsp.apply_num;
            } else {
                msg = '결제에 실패하였습니다.';
                msg += '에러내용 : ' + rsp.error_msg;
            }

            alert(msg);
        });
    });
});