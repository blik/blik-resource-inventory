var NODE = '';
var SELECTED_NAME = '';
var SPEC_PARAM_LIST = [];
var PARENT_LIST = [];
var ITEMS = [];

$(document).ready(function() {
    function onSelect(e) {
        NODE = e.node;
        SELECTED_NAME = this.text(e.node).replace(/^\s+|\s+$/g,""); //split space
        getParamsSpec(e.node) 
    };

    $("#treeView").kendoTreeView({ 
        template: kendo.template($("#treeview-template").html()),
        select: onSelect });
    $('#addParams').dataTable();
    $('#callback-toggle-button').toggleButtons();

});

function select_name(){
var x = document.getElementById("parent_spec").selectedIndex;
var y = document.getElementById("parent_spec").options;
$("#allowed_types").val('');
if (y[x].id != 'root_opt'){
$.ajax({
    type: "GET",
    url: "/tree_menu/",
    data: "spec_id="+y[x].id,
    success: function(data){
            ITEMS = [];
            var treeView = $("#treeView").kendoTreeView({template: kendo.template($("#treeview-template").html())}).data("kendoTreeView");
            ITEMS.push({ id: 'root_node', text: 'List of specification parameters',items: []});
            ITEMS[0].items = data.params_list.params_spec;
            //clear treeView
            $(".k-treeview").data("kendoTreeView").remove(".k-item");
            treeView.append(ITEMS);
            $(".k-first .k-in").dblclick()

            SPEC_PARAM_LIST = [];
            SPEC_PARAM_LIST = data.spec_param_list.params_spec;

           // $("#allowed_types").val(data.allowed_types);

///////////////////////////////////////// for create connection spec
            if (data.spec_param_list.connected_type != null)
                $("#conned_type").val(data.spec_param_list.connected_type);
            if (data.spec_param_list.connecting_type != null)
                $("#connion_type").val(data.spec_param_list.connecting_type);

    },
    error: function(xhr, str){
       alert('Возникла ошибка: ' + xhr.responseText);
    }

    })
}
else
    $(".k-treeview").data("kendoTreeView").remove(".k-item");
}

var transfer = new Object();
var ALLOWED_COLL_LIST = [];
var ASSIGNED_COLL_LIS = [];
function init(spec_param_list, items, parent_spec, type, res_param_dict, allowed_coll, assigned_coll){
    // init TreeMenu for specification and resource
//    if (type == 'element'){
//        RES_PARAM_DICT.additional_parameters = res_param_dict;
//        $("#res_name").attr('disabled', true);
//        $("#coll_allow_type").val(spec_param_list.allowed_types);
//        //$("#connected_type").val(spec_param_list.connected_type);
//        //$("#connecting_type").val(spec_param_list.connecting_type);
//
//        var treeView = $("#treeViewRes").kendoTreeView({template: kendo.template($("#treeview-template").html())}).data("kendoTreeView");
//
//        // for resource
//        if (document.getElementById('test') != undefined){
//            transfer = $('#test').bootstrapTransfer(
//                    {'target_id': 'multi-select-input',
//                    'height': '8em',
//                    'hilite_selection': true});
//
//            transfer.populate(allowed_coll);
//            transfer.set_values(assigned_coll);
//            ALLOWED_COLL_LIST = allowed_coll;
//            ASSIGNED_COLL_LIS = assigned_coll;
//        }
//
//    }
//    else{
//        // for collection specification
//        $("#parent_spec").attr('disabled', true);
//        $("#allowed_types").val(spec_param_list.allowed_types);
//
//        var treeView = $("#treeView").kendoTreeView({template: kendo.template($("#treeview-template").html())}).data("kendoTreeView");
//    }
//
//    // show on name of element
//    $("#root_opt").html(parent_spec);
//
//    SPEC_PARAM_LIST = spec_param_list.params_spec;
//    ITEMS.push({ id: 'root_node', text: 'List of specification parameters555',items: []}); //expanded: true,
//
//    if (items != undefined){
//        ITEMS[0].items = items;
//        treeView.append(ITEMS);
//        $(".k-first .k-in").dblclick()
//    }
}

function search(spec_type){
    //if ($("#spec_search").val() != ''){
        var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", "spec_type");
                hiddenField.setAttribute("value", spec_type);
        var hiddenField1 = document.createElement("input");
            hiddenField1.setAttribute("type", "hidden");
            hiddenField1.setAttribute("name", "s");
            hiddenField1.setAttribute("value", $("#spec_search").val());                
        var form = document.createElement("form"); 
            form.setAttribute("method", "GET");
            form.appendChild(hiddenField);
            form.appendChild(hiddenField1);
            form.submit();

    /*
     var data_dict = {};
     data_dict['spec_type'] = spec_type;
     data_dict['s'] = $("#spec_search").val();
     $.ajax({
        type: "GET",
        url: "/spec_search_res/",
        data: data_dict,
        success: function(items){ alert('ok')}
        })*/

    //}
    //else
    //    $('#search_err').append('<div id="alert_1" class="span7 alert alert-error">' +
    //        '<button type="button" class="close" data-dismiss="alert">×</button>' +
    //        '<strong>Error!</strong> Please, input the search data!</div>');
}

////////////TODO//////////////////
function getSearchName(spec_name){
    //window.location = "/specification_res/?" + escape(spec_name);
    //alert(spec_name)
    //if (spec_name != '')
    //    $("#spec_name").val(spec_name)
}

var SELECTED_NODE = '';
SPEC_PARAM_LIST = [];
function addSpecParam() {
    var param_name = $('#param_name').val();
    var spec_name = $('#spec_name').val();
    var pos_value = $('#pos_value').val();
    var def_value = $('#def_value').val();
    //alert('123')
    if(_checkErrorAdd(param_name,spec_name, pos_value,def_value) == true){
        var treeview = $("#treeView").data("kendoTreeView");
        SELECTED_NODE = treeview.select();
        var name = SELECTED_NAME.match(/\w+/);
        if (SELECTED_NODE.length == 0 || name == 'List'){// || selectedNode.id == undefined) {

            //_addParentParamSpec();
            if (_addParentParamSpec() != false){
                //alert('parent')
                //alert('SPEC_PARAM_LIST: '+ $.toJSON(SPEC_PARAM_LIST))
                if ($('.k-first')[0] != undefined)
                    treeview.append({text: param_name}, $('.k-first')); //add parent to root node
                else{
                    treeview.append({ id: 'root_node', text: 'List of specification parameters'});
                    treeview.append({text: param_name}, $('.k-first'));
                }
            }
        }
        // add children
        else{
            PARENT_LIST = [];
            PARENT_LIST.push(SELECTED_NAME);
            _getParent(SELECTED_NODE[0]);

            _addChildToParent(treeview);
            //if (_addChildToParent() != false){
                //alert(_addChildToParent)
                //treeview.append({text: param_name }, selectedNode);
                //alert('SPEC_PARAM_LIST: '+ $.toJSON(SPEC_PARAM_LIST))
            //}
        }

        $("#save_spec").removeAttr("disabled");
        _clear_form_elements();
    }
}

function _addParentParamSpec(){
    var spec_param_dict = {};
    var param_name = $("#param_name").val();

    if ($("#mandatory").attr('checked') != undefined)
        var mandatory = true;
    else
        mandatory = false;

    for (var i=0; i<SPEC_PARAM_LIST.length; i++){
        if (param_name == SPEC_PARAM_LIST[i].param_name){
            jAlert('Parameter "'+param_name+'" is present!');
            return false
        }
        //alert(param_name)

    }
    spec_param_dict['param_name'] = param_name;
    //alert('SPEC_PARAM_LIST'+ $.toJSON(SPEC_PARAM_LIST[1].param_name))
    spec_param_dict['param_type'] = $("#param_type").val();
    spec_param_dict['description'] = $("#param_desc").val();
    spec_param_dict['possible_values'] = $("#pos_value").val();
    spec_param_dict['default_value'] = $("#def_value").val();
    spec_param_dict['mandatory'] = mandatory;
    //spec_param_dict['children_spec'] = []
    SPEC_PARAM_LIST.push(spec_param_dict)
}

function _getParent(node){
    var name = node.parentNode.parentNode.textContent.match(/\w+/);
    if (name != 'List'){ //node.parentNode.parentNode.id != 'treeView'
        PARENT_LIST.push(name);
        _getParent(node.parentNode.parentNode)
    }
    //alert('parent_list!'+ $.toJSON(PARENT_LIST))
}

function _addChildToParent(treeView){
    var child_param_dict = {};

    if ($("#mandatory").attr('checked') != undefined)
        var mandatory = true;
    else
        mandatory = false;

    child_param_dict['param_name'] = $("#param_name").val();
    child_param_dict['param_type'] = $("#param_type").val();
    child_param_dict['description'] = $("#param_desc").val();
    child_param_dict['possible_values'] = $("#pos_value").val();
    child_param_dict['default_value'] = $("#def_value").val();
    child_param_dict['mandatory'] = mandatory;

    _addChild(PARENT_LIST, SPEC_PARAM_LIST,child_param_dict, treeView)
}

function _addChild(parent_list, spec_param_list, child_param_dict, treeView){
    var parent_name = parent_list.pop();
    for (var i=0; i<spec_param_list.length; i++){
        //search parent
        if (spec_param_list[i].param_name != parent_name){
            continue;
        }
        else{
            if (spec_param_list[i].param_name == SELECTED_NAME){
                for (var k=0; k<spec_param_list[i].children_spec.length; k++){
                    if (child_param_dict.param_name == spec_param_list[i].children_spec[k].param_name){
                        jAlert('Parameter "'+child_param_dict.param_name+'" is present for "' + SELECTED_NAME +'"!');
                        return
                    }
                }
                // add child to parent in treeMenu
                var param_name = $("#param_name").val();
                treeView.append({text: param_name }, SELECTED_NODE);
                spec_param_list[i].children_spec.push(child_param_dict);
            }
            else
               _addChild(parent_list, spec_param_list[i].children_spec, child_param_dict, treeView)
        }
    }
}

function addChildNode(){
    $('#alert_2').remove();
    PARENT_LIST = []
    PARENT_LIST.push(SELECTED_NAME);
    $(".k-state-selected").dblclick(); //expand parent node
    _getParent(NODE);
    _isParent(PARENT_LIST, SPEC_PARAM_LIST)
}

function _isParent(parent_list, spec_param_list){        
    var parent = parent_list.pop();
    for (var i=0; i<spec_param_list.length; i++){
        if (spec_param_list[i].param_name != parent){
            continue;
        }
        else{
            if (spec_param_list[i].param_name == SELECTED_NAME){
                if (spec_param_list[i].param_type == 'dict' || spec_param_list[i].param_type == 'list'){

                    var keys = Object.keys(spec_param_list[i]);
                    if (keys.length < 7)
                        spec_param_list[i]['children_spec'] = []; //add key for created children

                    _clear_form_elements();
                    $("#add_spec").removeAttr("disabled");
                    $("#update_spec").attr("disabled", "disabled");
                }
                else
                    $('#field_err').append('<div id="alert_2" class="span9 alert alert-error">' +
                        '<button type="button" class="close" data-dismiss="alert">×</button>' +
                        '<strong>Error! </strong>Type is not "list" or "dict".</div>');
            }
            else
                _isParent(parent_list, spec_param_list[i].children_spec);
        }
    }
}

function updateParamSpec(){
    var param_name = $('#param_name').val();
    var spec_name = $('#spec_name').val();
    var pos_value = $('#pos_value').val();
    var def_value = $('#def_value').val();

    if (_checkErrorAdd(param_name,spec_name, pos_value,def_value) == true) {
        PARENT_LIST = [];
        PARENT_LIST.push(SELECTED_NAME);
        _getParent(NODE);
        _updateParam(PARENT_LIST, SPEC_PARAM_LIST);
        alert('SPEC_PARAM_LIST: '+ $.toJSON(SPEC_PARAM_LIST))
        $.gritter.add({
            title:  'Blik inventory',
            text:   'Updated successfully!',
            sticky: false
        });
        $("#save_spec").removeAttr("disabled");
    }
}

function _updateParam(parent_list, spec_param_list){
    var parent = parent_list.pop()
    for (var i=0; i<spec_param_list.length; i++){
        if (spec_param_list[i].param_name != parent){
            continue;
        }
        else{
            if (spec_param_list[i].param_name == SELECTED_NAME){

                if ($("#mandatory").attr('checked') != undefined)
                    var mandatory = true;
                else
                    mandatory = false;

                spec_param_list[i].param_name = $("#param_name").val();
                spec_param_list[i].param_type = $("#param_type").val();
                spec_param_list[i].description = $("#param_desc").val();
                spec_param_list[i].possible_values = $("#pos_value").val();
                spec_param_list[i].default_value = $("#def_value").val();
                spec_param_list[i].mandatory = mandatory;

            }
            else
                _updateParam(parent_list, spec_param_list[i].children_spec);
        }
    }
}

//disable or enable field 'default value'
function updateDefault(pos_value,def_value){
    if ($("#"+pos_value+"").val() != ''){
        $("#"+def_value+"").removeAttr("disabled");
    }
    else{
        $("#"+def_value+"").val('');
        $("#"+def_value+"").attr("disabled", "disabled");
    }
}

function saveSpecification(spec_type){
    if (_checkRequiredSave() == true) {

        var data_dict = {};
            data_dict['spec_id'] = $('#spec_id').val();
            data_dict['spec_name'] = $('#spec_name').val();
            data_dict['spec_type'] = spec_type;
            data_dict['spec_desc'] = $('#spec_desc').val();
            data_dict['parent_spec'] = $('#parent_spec').val();
            data_dict['connion_type'] = $('#connion_type').val();
            data_dict['conned_type'] = $('#conned_type').val();
            data_dict['allowed_types'] = $('#allowed_types').val();
            data_dict['param_spec'] = $.toJSON(SPEC_PARAM_LIST);
            //alert('data_dict:'+ $.toJSON(data_dict))

    $.ajax({
        type: "POST",
        url: "/save_spec/",
        data: data_dict,
        success: function(){
            //alert('ok')
            jAlert('Specification saved successfully!', 'Success', function(){
                if (spec_type == 'resource'){
                    window.location = "/specification_res/"; //"/specification_res/?spec_id=" + escape(spec_id);
                    //alert(spec_id)
                    
                }
                else if (spec_type == 'collection')
                    window.location = "/specification_coll/";
                else if (spec_type == 'connection')
                    window.location = "/specification_conn/"
            })

        },
        error: function(xhr, str,f,t){
            alert(xhr.responseText)
            str = xhr.responseText;
            re = /Exception Value/;
//BIException at /save_spec/
//[Blik Inventory Exception] Specification type <spec_type> is not supported!

            //alert(t) replace(/^\s+|\s+$/g,"")
            //for (i=0; i<xhr.length; i++){
            found = str.match(re);

            //alert(found)
            //jAlert(found, 'Error');
            //    alert(xhr[i])
            //}
               //alert('Возникла ошибка: ' + $.toJSON(xhr));
        }
        })

    }
}

function delSpecRow(del_id){
    jConfirm('<strong>Do you want delete element?</strong>', 'Confirmation Dialog', function(r) {
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

function delParamSpec(){
    jConfirm('<strong>Do you want delete parameter?</strong>', 'Confirmation Dialog', function(r) {
        if (r == true){
            PARENT_LIST = [];
            PARENT_LIST.push(SELECTED_NAME);
            _getParent(NODE);
            _delParam(PARENT_LIST, SPEC_PARAM_LIST);

            _clear_form_elements();
            $("#update_spec").attr('disabled', true)
            $("#save_spec").removeAttr('disabled');
            $("#add_spec").removeAttr('disabled');

            $("#param_name").focus();


            var treeview = $("#treeView").data("kendoTreeView");
            treeview.remove($(treeview.select()).closest(".k-item"));
        }
    })
}

function _delParam(parent_list, spec_param_list, parent_spec_param){
    var parent = parent_list.pop();
    for (var i=0; i<spec_param_list.length; i++){
        if (spec_param_list[i].param_name != parent)
            continue;
        else{
            if (spec_param_list[i].param_name == SELECTED_NAME){
                if (parent_spec_param != undefined){
                    //del children_spec from parent
                    parent_spec_param.children_spec.splice(i,1);
                    if (parent_spec_param.children_spec == '')
                        delete parent_spec_param['children_spec']; //del key @children_spec from parent
                }
                //del parent from root_node
                else
                    spec_param_list.splice(i,1)
            }
            else
                _delParam(parent_list, spec_param_list[i].children_spec, spec_param_list[i])
        }
    }
}

function getParamsSpec(selectedNode){
    var name = selectedNode.textContent.match(/\w+/);

    if (name == 'List'){
        _clear_form_elements();
        $("#add_spec").removeAttr("disabled");
        $("#update_spec").attr("disabled", "disabled");
    }
    //get param from children
    else{
        $("#add_spec").attr("disabled", "disabled");
        $("#update_spec").removeAttr("disabled");

        PARENT_LIST = [];
        PARENT_LIST.push(SELECTED_NAME);
        _getParent(NODE);
        _getParam(PARENT_LIST,SPEC_PARAM_LIST);
        //alert('1')

    }
}

function _getParam(parent_list, spec_param_list){
    "display parent & child items on TreeMenu. Hide & show parameters."
    var parent = parent_list.pop();
    for (var i=0; i<spec_param_list.length; i++){
        if (spec_param_list[i].param_name != parent)
            continue;
        else{
            if (spec_param_list[i].param_name == SELECTED_NAME){
                // display parent & child items on specification form
                $("#param_name").val(spec_param_list[i].param_name);
                $("#param_type").val(spec_param_list[i].param_type);
                $("#param_desc").val(spec_param_list[i].description);
                $("#pos_value").val(spec_param_list[i].possible_values);
                $("#def_value").val(spec_param_list[i].default_value);

                if(spec_param_list[i].mandatory == true)
                    $("#mandatory").attr('checked',true).trigger('change');
                else
                    $("#mandatory").attr('checked',false).trigger('change');
            }
            // call recursive
            else
                _getParam(parent_list, spec_param_list[i].children_spec)
        }
    }
}

//-----------------------------------helps functions-----------------------------------//
//check default value in possible list
function _checkArray(arr1,arr2){
    var on = 0;
    for( var i = 0; i < arr2.length; i++ ){
        for( var j = 0; j < arr1.length; j++ ){
            if(arr1[j] === arr2[i]){
                on++;
                break
            }
        }
    }

    if (on != arr2.length)
        return false;
    else
        return true
}

function _clear_form_elements() {
    $("#form_param_spec").find(':input').each(function() {
        $(this).val('');
    });

    $("#child_def_value").attr("disabled", "disabled");
    $("#def_value").attr("disabled", "disabled");
    $("#mandatory").attr('checked',false).trigger('change');
    $("#param_type").val('string');
}

function _checkRequiredSave() {
    var err = 0;
    $("#form_spec").find('.required').each(function() {
        if ($(this).val() == ''){
            if (document.getElementById("alert_2") == null){
                $('#field_err_2').append('<div id="alert_2" class="span6 alert alert-error">' +
                    '<button type="button" class="close" data-dismiss="alert">×</button>' +
                    '<strong>Error!</strong> Please, fill the required field.</div>');
            }
            err++;
        }           
    });
    if (err == 0)
        return true;
    else
        return false
}

function _checkErrorAdd(name_spec,param_name, pos_value,def_value){
    if (name_spec != '' && param_name != ''){
        $('#alert_2').remove();

            if (_checkArray(pos_value, def_value) == true)
                return true;
            else{
                $('#field_err').append('<div id="alert_1" class="span9 alert alert-error">' +
                    '<button type="button" class="close" data-dismiss="alert">×</button>' +
                    '<strong>Error!</strong> Default value are out of list of possible value!</div>');
            }
    }
    else{
        if (document.getElementById("alert_2") == null){
            $('#field_err').append('<div id="alert_2" class="span9 alert alert-error">' +
                '<button type="button" class="close" data-dismiss="alert">×</button>' +
                '<strong>Error!</strong> Please, fill the required field.</div>');
        }
    }
}
