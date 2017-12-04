function renderHTML(response, direction){
    if(typeof response === 'undefined' || !response) return;
    var arr = response.split('\'');
    var data = arr[3];
    if(arr[1] == "data"){
        $("#plaintext").attr("placeholder","");
        $("#ciphertext").css("border","2px solid #ccc");
        $("#plaintext").css("border","2px solid #ccc");
        switch(direction){
            case 'e':
                $("#ciphertext").val(data);
                break;
            case 'd':
                $("#plaintext").val(data);
                break;
        }
    }
    else{ //padding error
        //alert(data);
        if(direction='d'){
            $("#ciphertext").css("border","2px solid #f10a0a");
            $("#plaintext").css("border","2px solid #f10a0a");
            $("#plaintext").val("");
            $("#ciphertext").effect("pulsate", {times:3});
            $("#plaintext").attr("placeholder",data);
        }
    }

}
function exists(data){
    if(data.length > 0) return true;
    alert("Please enter text");
    return false;
}
function validKey(key){
    if(key.length == 16 || key.length == 24 || key.length == 32) return true;
    alert("AES key must be either 16, 24, or 32 bytes long");
    return false;
}
$(document).ready(function() {
    $('#encrypt').on('submit', function(e) {
        e.preventDefault();
        var data = $('#plaintext').val();
        var key = $('#plaintext-key').val();
        if(validKey(key) && exists(data)){
            var direction = $('#dir1').val();
            $.ajax({
                url:'http://localhost:8080/encrypt',
                method:'POST',
                data:{
                    data:data,
                    key:key,
                    direction:direction,
                },
                dataType:"json",
                success:function(data, status) {
                // for our purposes, all responses are errors.
                },
                error: function (err){ 
                    renderHTML(err.responseText, direction);
                }
            });
        }
    });
    $('#decrypt').on('submit', function(e) {
        e.preventDefault();
        var data = $('#ciphertext').val();
        var key = $('#ciphertext-key').val();
        var direction = $('#dir2').val();
        if(validKey(key) && exists(data)){
            $.ajax({
                url:'http://localhost:8080/decrypt',
                method:'POST',
                data:{
                    data:data,
                    key:key,
                    direction:direction
                },
                dataType:"json",
                success:function(data, status) {
                // for our purposes, all responses are errors.
                },
                error: function (err){ 
                    renderHTML(err.responseText, direction);
                }
            });  
        }   
    });
    $('#clearAll').on('click',function(e){
        e.preventDefault();
        $('#ciphertext').val("");
        $('#plaintext').val("");
        $('#ciphertext-key').val("");
        $('#plaintext-key').val("");
    });
}); 