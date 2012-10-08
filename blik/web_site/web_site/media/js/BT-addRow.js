$(document).ready(function() {
    $('#addParams').dataTable();
} );

function fnClickAddRow() {
    var spec_name  = $('#name_spec').val();
    var param_name = $('#param_name').val();

    var parent_spec = $('#parent_spec').val();
    var param_type = $('#param_type').val();
    var param_desc = $('#param_desc').val();
    var pos_value = $('#pos_value').val();
    var def_value = $('#def_value').val();

    //var err_class_1 = document.getElementById("err_class1")

    //insert row
    if (spec_name != '' && param_name != ''){
        //err_class_1.removeAttribute('class')
        $('#alert_2').remove();

        if (_checkArray(pos_value,def_value) == true){
           //check checked radio
            var radios = document.getElementsByTagName('input');
            var value;
            for (var i = 0; i < radios.length; i++) {
              if (radios[i].type === 'radio' && radios[i].checked) {
                man_value = radios[i].value;
              }
            }

           //generate #
            var table = document.getElementById("addParams")
            var rows = table.rows.length;
            var first_cell = table.rows[1].cells[0].innerHTML;

            if (rows == 2 && first_cell != 1){
               number = rows - 1
            }
            else{
               number = rows
            }   

            //add params to body table
            $('#addParams').dataTable().fnAddData( [
                param_name,
                param_type,
                param_desc,
                pos_value,
                def_value,
                man_value,
                innerHTML='<button id="delete_row"class="btn btn-mini btn-primary" onclick="delThisRow(this.parentNode.parentNode.rowIndex)"><i class="icon-remove" ></i> DEL </button>'] )

            //enable Save button
            $("#save_spec").removeAttr("disabled");
            _clear_form_elements()
        }
        else{
                $('#params_spec').append('<div id="alert_1" class="span4 alert alert-error"><button type="button" class="close" data-dismiss="alert">×</button><strong>Error!</strong> Default value are out of list of possible value!</div>');
        }
    }
    else{
        //err_class_1.setAttribute("class", "control-group error")
        if (document.getElementById("alert_2") == null){
            $('#params_spec').append('<div id="alert_2" class="span4 alert alert-error"><button type="button" class="close" data-dismiss="alert">×</button><strong>Error!</strong> Please, fill the required field.</div>');
        }
    }
}

function delThisRow(index) {
    jConfirm('<strong>Do you want delete record?</strong>', 'Confirmation Dialog', function(r) {
        if (r == true){
            $('#addParams').dataTable().fnDeleteRow( index-1 );
            //disable button 'Save' if not rows in table 
            if ($('#addParams').dataTable().fnGetData(0) == null){
                $("#save_spec").attr("disabled", "disabled");
            }
       }
    })
}

//disable or enable field 'default value'
function updateDefault(){
    if ($("#pos_value").val() != ''){
        $("#def_value").removeAttr("disabled");
    }
    else{
        $("#def_value").val('')
        $("#def_value").attr("disabled", "disabled");
    }
}


function saveSpecification(){
    var rows = $('#addParams tr').length;
    var raw_param_list = {}
    var param_spec_list = []

    //get data from table and push to list
    for (i=0; i<(rows-1); i++){
        var data = $('#addParams').dataTable().fnGetData(i)
           raw_param_list['param_name'] = data[0]
           raw_param_list['param_type'] = data[1]
           raw_param_list['description'] = data[2]
           raw_param_list['possible_values'] = data[3]
           raw_param_list['default_value'] = data[4]
           raw_param_list['mandatory'] = data[5]

        var encoded_param_list = $.toJSON(raw_param_list);
           param_spec_list.push(encoded_param_list)
    }

    var spec_name  = $('#name_spec').val();
    var parent_spec = $('#parent_spec').val();

    /*var spec_list = []
    var params_list = ['spec_name', 'parent_spec', 'param_spec']
    spec_list.push(spec_name)
    spec_list.push(parent_spec)
    spec_list.push(param_spec_list)

    for (i=0; i<=2; i++){
        num = i.toString()
        var hf+num = document.createElement("input");
            hf+num.setAttribute("type", "hidden");
            hf+num.setAttribute("name", params_list[i]);
            hf+num.setAttribute("value", spec_list[i]);

    }*/

    //create post form with hidden elements
    var hiddenField1 = document.createElement("input");
        hiddenField1.setAttribute("type", "hidden");
        hiddenField1.setAttribute("name", "spec_name");
        hiddenField1.setAttribute("value", spec_name);

    var hiddenField2 = document.createElement("input");
        hiddenField2.setAttribute("type", "hidden");
        hiddenField2.setAttribute("name", "parent_spec");
        hiddenField2.setAttribute("value", parent_spec);

    var hiddenField3 = document.createElement("input");
        hiddenField3.setAttribute("type", "hidden");
        hiddenField3.setAttribute("name", "param_spec");
        hiddenField3.setAttribute("value", param_spec_list);

    var form = document.createElement("form"); 
        form.setAttribute("method", "post");
        //form.setAttribute("action", "/create_spec_res/")

    form.appendChild(hiddenField1)
    form.appendChild(hiddenField2)
    form.appendChild(hiddenField3)

    form.submit();

}

function _clear_form_elements() {
    $("#form_param_spec").find(':input').each(function() {
        switch(this.type) {
           case 'text':
                $(this).val('');
                break;
        }
    });

    $("#def_value").attr("disabled", "disabled");
    $("#no").attr("checked", true);
    $("#param_type").val('dict');
}

//check default value in possible list
function _checkArray(arr1,arr2){
    var on = 0;
    for( var i = 0; i < arr2.length; i++ ){
        for( var j = 0; j < arr1.length; j++ ){
            if(arr1[j] === arr2[i]){
                on++
                break
            }
        }
    }

    if (on != arr2.length){
        return false
    }
    else{
        return true
    }
}