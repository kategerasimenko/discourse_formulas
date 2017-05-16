function validate() {
    valid = true;
    var val = document.forms["fileform"]["file"].value;
    var ext = val.substring(val.lastIndexOf('.') + 1).toLowerCase();
    if (val == ''){
        $("#notice").text("Выберите файл!");
        $("#notice").show();
        // your validation error action
        valid = false;
    }
    else if (ext != 'txt') {
        $("#notice").text("Неверный формат файла. Необходимо загружать файл в формате txt.");
        $("#notice").show();
        valid = false;
    }
    else {
        var size = document.forms["fileform"]["file"].files[0].size;
        if (size > 500*1024) {
            $("#notice").text("Слишком большой файл! Размер файла не должен превышать 5 Мб.");
            $("#notice").show();
            valid = false;   
        }
    }    
    return valid; //true or false
}