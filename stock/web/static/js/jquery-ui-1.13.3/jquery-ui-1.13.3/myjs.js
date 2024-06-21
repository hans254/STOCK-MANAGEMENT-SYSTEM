$(document).ready(function(){
    $('.table').paging({limit: 6});
    NProgress.start();
    NProgress.done();
    $(".datetimeinput").datepicker({changeYear: true, changeMonth: true, dateformat: yy-m-dd});

    
})