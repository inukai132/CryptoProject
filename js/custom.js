/* utility functions */

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
function base64toHEX(base64) {
  var raw = atob(base64);
  var HEX = '';
  for (i = 0; i < raw.length; i++){
    var _hex = raw.charCodeAt(i).toString(16)
    HEX += (_hex.length==2?_hex:'0'+_hex);
    HEX += ' ';
  }
  return HEX.toUpperCase();
}
function hexToBase64(hexstring) {
    return btoa(hexstring.match(/\w{2}/g).map(function(a) {
        return String.fromCharCode(parseInt(a, 16));
    }).join(""));
}

/* interpreting and rendering response from server.py */
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

/* global variables */
var isHex=false;
var isBase=true;

$(document).ready(function() {

    /* toHex and toBase events */
    $('#toHex').on('click', function(){
        if(!isHex && isBase && $("#ciphertext").val() != ""){
            $("#ciphertext").val(base64toHEX($("#ciphertext").val()));
            isHex = true;
            isBase = false; 
        }
    })
    $('#toBase').on('click', function(){
        if(isHex && !isBase && $("#ciphertext").val() != ""){
            $("#ciphertext").val(hexToBase64($("#ciphertext").val()));
            isBase = true;
            isHex = false; 
        }
    })

    /* encrypting */
    $('#encrypt').on('submit', function(e) {
        isBase = true;
        isHex = false;
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

    /* decrypting */
    $('#decrypt').on('submit', function(e) {
        if(isHex && !isBase){
            $("#ciphertext").val(hexToBase64($("#ciphertext").val()));
            isBase = true;
            isHex = false; 
        }
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

    /* clear all button */
    $('#clearAll').on('click',function(e){
        e.preventDefault();
        $('#ciphertext').val("");
        $('#plaintext').val("");
        $('#ciphertext-key').val("");
        $('#plaintext-key').val("");
    });
}); 
