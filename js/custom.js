$(document).ready(function() {
    $('#encrypt').on('submit', function(e) {
        e.preventDefault();
        var data = $('#plaintext').val();
        var key = $('#plaintext-key').val();
        var direction = $('#dir1').val();
        $.ajax({
            url:'http://localhost:8080/encrypt',
            method:'POST',
            data:{
                data:data,
                key:key,
                direction:direction
            },
            dataType:"json",
            success:function() {
                console.log('success'); 
            }
        });     
    });
    $('#decrypt').on('submit', function(e) {
        e.preventDefault();
        var data = $('#ciphertext').val();
        var key = $('#ciphertext-key').val();
        var direction = $('#dir2').val();
        $.ajax({
            url:'http://localhost:8080/decrypt',
            method:'POST',
            data:{
                data:data,
                key:key,
                direction:direction
            },
            dataType:"json",
            success:function() {
                console.log('success'); 
            }
        });     
    });
}); 