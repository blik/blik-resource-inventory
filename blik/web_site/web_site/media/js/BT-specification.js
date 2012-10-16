$(document).ready(function() {
    $('#addParams').dataTable();
} );

function search(spec_type){
    if ($("#spec_search").val() != ''){
    var form = document.createElement("form"); 
        form.setAttribute("method", "GET");
       // alert($("#spec_type").val())
            var hiddenField = document.createElement("input");
                hiddenField.setAttribute("type", "hidden");
                hiddenField.setAttribute("name", "spec_type");
                hiddenField.setAttribute("value", spec_type);
            var hiddenField1 = document.createElement("input");
                hiddenField1.setAttribute("type", "hidden");
                hiddenField1.setAttribute("name", "s");
                hiddenField1.setAttribute("value", $("#spec_search").val());                

            form.appendChild(hiddenField);
            form.appendChild(hiddenField1);
            form.submit();
    }
    else
        $('#search_err').append('<div id="alert_1" class="span7 alert alert-error"><button type="button" class="close" data-dismiss="alert">×</button><strong>Error!</strong> Please, input the search data!</div>');
}

////////////TODO//////////////////
function getSpecForCreate(spec_name){
    window.location = "/specification_res/?" + escape(spec_name);
}

function addParamToTable() {
    if(_checkErrorAdd() == true){
        //check checked radio
        if ($("input[@name=optionsRadios]:checked").attr('id') == 'yes'){
            var mandatory = 'Yes'
        }
        else{
            mandatory = 'No'
        }
        //add params to body table
        $('#addParams').dataTable().fnAddData( [
            $('#param_name').val(),
            $('#param_type').val(),
            $('#param_desc').val(),
            $('#pos_value').val(),
            $('#def_value').val(),
            mandatory,
            '<center><button id="delete_row"class="btn btn-mini btn-danger" onclick="delParamRow(this.parentNode.parentNode.parentNode.rowIndex)"><i class="icon-remove" ></i></button> <a id="edit_row" class="btn btn-mini btn-warning" onClick="editParamRow(this.parentNode.parentNode.parentNode.rowIndex);"><i class="icon-edit"></i></a> <button id="info"class="btn btn-mini btn-success" onclick=""><i class="icon-plus-sign" ></i></button><center>'] )

        //enable Save button
        $("#save_spec").removeAttr("disabled");

        _clear_form_elements();
        }
}

function delParamRow(index) {
    jConfirm('<strong>Do you want delete parameter?</strong>', 'Confirmation Dialog', function(r) {
        if (r == true){
            var oTable = document.getElementById('addParams');
            var rowLength = oTable.rows.length;
                oTable.deleteRow(index);
                //disable button 'Save' if not rows in table 
                if (rowLength == 1){
                    $("#save_spec").attr("disabled", "disabled");
                }
                else{
                    $("#save_spec").removeAttr("disabled");
                }
       }
    })
}

function editParamRow(index){
   var oTable = document.getElementById('addParams');
   var oCells = oTable.rows.item(index).cells;
        $("#param_name").val(oCells.item(0).innerHTML)
        $("#param_type").val(oCells.item(1).innerHTML)
        $("#param_desc").val(oCells.item(2).innerHTML)
        $("#pos_value").val(oCells.item(3).innerHTML)
        $("#def_value").val(oCells.item(4).innerHTML)

        if (oCells.item(5).innerHTML == 'No'){
            $("#no").attr("checked", true);
        }
        else{
            $("#yes").attr("checked", true);
        }
        updateDefault();

        $("#save_spec").attr("disabled", "disabled");
        $("#update_spec").removeAttr("disabled")
        $("#add_spec").attr("disabled", "disabled");
       //lock all button in table
        $("#tab_params_spec").find(':button').each(function() {
            $(this).attr("disabled", "disabled");
        });

        //saving index of row which is edited
        $("#index").val(index)
}

function updateParam(){
    if (_checkErrorAdd() == true) {
        var oTable = $("#addParams").dataTable();
        
        var index = $("#index").val();
        var oTable = document.getElementById('addParams');
        var oCells = oTable.rows.item(index).cells;
            //set edited param to table cells
            oCells.item(0).innerHTML = $("#param_name").val();
            oCells.item(1).innerHTML = $("#param_type").val();
            oCells.item(2).innerHTML = $("#param_desc").val();
            oCells.item(3).innerHTML = $("#pos_value").val();
            oCells.item(4).innerHTML = $("#def_value").val();

            if($("input[@name=optionsRadios]:checked").attr('id') == 'yes'){
                oCells.item(5).innerHTML = "Yes";
            }
            else{
                oCells.item(5).innerHTML = "No";
            }

            _clear_form_elements();

            $("#update_spec").attr("disabled", "disabled");
            $("#add_spec").removeAttr("disabled");
            $("#save_spec").removeAttr("disabled");
            //enable all buttons in table
            $("#tab_params_spec").find(':button').each(function() {
                $(this).removeAttr("disabled");
            });
    }
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

function saveSpecification(spec_type){
    var raw_param_list = {};
    var param_spec_list = [];

    if (_checkRequiredSave() == true) {
        //get data from table and push to json list
        var oTable = document.getElementById('addParams');
        var rowLength = oTable.rows.length;
            for (i=1; i<rowLength; i++){
                var oCells = oTable.rows.item(i).cells;
                    raw_param_list['param_name'] = oCells.item(0).innerHTML;
                    raw_param_list['param_type'] = oCells.item(1).innerHTML;
                    raw_param_list['description'] = oCells.item(2).innerHTML;
                    raw_param_list['possible_values'] = oCells.item(3).innerHTML;
                    raw_param_list['default_value'] = oCells.item(4).innerHTML;
                    raw_param_list['mandatory'] = oCells.item(5).innerHTML;

                var encoded_param_list = $.toJSON(raw_param_list);
                    param_spec_list.push(encoded_param_list);
            }
        //get data from form
        var data_list = []
            data_list.push($('#spec_name').val());
            data_list.push(spec_type)
            data_list.push($('#parent_spec').val());
            data_list.push($('#spec_desc').val());
            data_list.push($('#connion_type').val());
            data_list.push($('#conned_type').val());
            data_list.push($('#allowed_types').val());
            data_list.push(param_spec_list);

        var params = ['spec_name', 'spec_type', 'parent_spec', 'spec_desc', 'connion_type', 'conned_type', 'allowed_types', 'param_spec'];
        //create post form
        var form = document.createElement("form"); 
            form.setAttribute("method", "post");

            for (i=0; i<=7; i++){
                var hiddenField = 'hiddenField' + i.toString()
                var hiddenField = document.createElement("input");
                    hiddenField.setAttribute("type", "hidden");
                    hiddenField.setAttribute("name", params[i]);
                    hiddenField.setAttribute("value", data_list[i]);

                form.appendChild(hiddenField);
            }
        form.submit();
    }
}

function delSpecRow(del_id){
    jConfirm('<strong>Do you want delete specification?</strong>', 'Confirmation Dialog', function(r) {
        if (r == true){
            var form = document.createElement("form");
                form.setAttribute("method", "POST");
            var hiddenField = document.createElement("input");
                hiddenField.setAttribute("type", "hidden");
                hiddenField.setAttribute("name", "del_id");
                hiddenField.setAttribute("value", del_id);
            form.appendChild(hiddenField);
            form.submit();
        }
    });
}

function getSpecForEdit(spec_id, spec_type){
    if (spec_type == 'resource')
        window.location = "/specification_res/?spec_id=" + escape(spec_id);
    else if (spec_type == 'connection')
        window.location = "/specification_conn/?spec_id=" + escape(spec_id);
    else if (spec_type == 'collection')
        window.location = "/specification_coll/?spec_id=" + escape(spec_id);
}

function getSpecForInfo(spec_id){
    //alert(spec_id)
    form = document.createElement("form"); 
     form.setAttribute("method", "GET");

            var hf = document.createElement("input");
                hf.setAttribute("type", "hidden");
                hf.setAttribute("name", 'id_spec');
                hf.setAttribute("value", spec_id);
            form.appendChild(hf);
            //form.submit();
            
    //window.location = "/modal_spec_res/?" + packed;
    //$('#infoModal').modal('show')
}

function _clear_form_elements() {
    $("#form_param_spec").find(':input').each(function() {
        $(this).val('');
    });

    $("#def_value").attr("disabled", "disabled");
    $("#no").attr("checked", true);
    $("#param_type").val('dict');
}

function _checkRequiredSave() {
    var err = 0;
    $("#form_spec").find('.required').each(function() {
        if ($(this).val() == ''){
            if (document.getElementById("alert_2") == null){
                $('#field_err_2').append('<div id="alert_2" class="span6 alert alert-error"><button type="button" class="close" data-dismiss="alert">×</button><strong>Error!</strong> Please, fill the required field.</div>');  
            }
            err++
        }           
    });
    if (err == 0)
        return true
    else
        return false
}

function _checkErrorAdd(){
    if ($('#name_spec').val() != '' && $('#param_name').val() != ''){
        $('#alert_2').remove();

            if (_checkArray($('#pos_value').val(), $('#def_value').val()) == true){

                return true
            }
            else{
                $('#field_err').append('<div id="alert_1" class="span9 alert alert-error"><button type="button" class="close" data-dismiss="alert">×</button><strong>Error!</strong> Default value are out of list of possible value!</div>');
            }
    }
    else{
        if (document.getElementById("alert_2") == null){
            $('#field_err').append('<div id="alert_2" class="span6 alert alert-error"><button type="button" class="close" data-dismiss="alert">×</button><strong>Error!</strong> Please, fill the required field.</div>');
        }
    }
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

    if (on != arr2.length)
        return false
    else
        return true
}