var RES_PARAM_DICT = {};
var RES_PARENT_LIST = [];

var SELECTED_OPT = '';
var SELECTED_ID = '';

var ELEM_TYPE = {'IS_RES': 'resource',
                 'IS_CONN': 'connection',
                 'IS_COLL': 'collection'};

$(document).ready(function() {
    function onSelect(e) {
        NODE = e.node
        SELECTED_NAME = this.text(e.node).replace(/^\s+|\s+$/g,""); //split space
        getResParams(e.node)
    }

    $("#treeViewRes").kendoTreeView({
        template: kendo.template($("#treeview-template").html()),
        select: onSelect });

    $('#addParams').dataTable();
    //$('#callback-toggle-button').toggleButtons();

    //$('#res_collect').multiselect();

    //t = $('#test').bootstrapTransfer(
    //        {'target_id': 'multi-select-input',
    //            'height': '8em',
    //            'hilite_selection': true});

        //t.populate([
        //    {value:"1", content:"Apple"},
        //    {value:"2", content:"Orange"},
        //    {value:"3", content:"Banana"},
        //    {value:"4", content:"Peach"},
        //    {value:"5", content:"Grapes"}
        //]);
        //t.set_values(["2", "4"]);

});

function select_name_res(){
    var index = document.getElementById("res_name").selectedIndex;
    var opt = document.getElementById("res_name").options;
    SELECTED_OPT = opt[index].value;
    SELECTED_ID = opt[index].id;
    $("#connected_type").val('');
    $("#connecting_type").val('');
    $("#connected_res_name_id").empty();
    $("#connecting_res_name_id").empty();
    if (opt[index].id != 'root_opt'){
        $.ajax({
            type: "GET",
            url: "/tree_menu/",
            data: "spec_id=" + opt[index].id,
            success: function(){
                // json for treeMenu
                $.getJSON("/media/tree_menu.json", function(params_list){
                    //alert('params_list'+ $.toJSON(params_list.params_spec))
                    var items = [];
                    var treeView = $("#treeViewRes").kendoTreeView({template: kendo.template($("#treeview-template").html())}).data("kendoTreeView");

                    if ($("#coll_allow_type").val() != undefined){
                        $("#coll_allow_type").val(params_list.allowed_types)
                    }

                    // generate list of parameters
                    items.push({id: 'root_node', text: 'List of specification parameters', items: []});
                    items[0].items = params_list.params_spec;

                    // clear treeView
                    $(".k-treeview").data("kendoTreeView").remove(".k-item");

                    treeView.append(items);
                    // open root_node through dblclick on item :)
                    $(".k-first .k-in").dblclick()
                });
                // json specifications params list for resource
                $.getJSON("/media/spec_param_list.json", function(spec_param_list){
                    // global var. see BT-specification.js
                    SPEC_PARAM_LIST = [];
                    SPEC_PARAM_LIST = spec_param_list.params_spec;

                    // for connection
                    $("#connected_type").val(spec_param_list.connected_type);
                    $("#connecting_type").val(spec_param_list.connecting_type);

                    RES_PARAM_DICT = {'additional_parameters': {}};
                    convertAdditionalParams(RES_PARAM_DICT, spec_param_list.params_spec);
                });


                $.getJSON("/media/connecting_res_list.json", function(connecting_res){
                    //alert($.toJSON(connecting_res));

                    if (connecting_res != null){
                        for (var i=0; i<connecting_res.length; i++){
                            $("<option></option>", {value: connecting_res[i].connecting_res_id, text: connecting_res[i].res_name}).appendTo('.connecting_res');
                        }
                    }
                });
                $.getJSON("/media/connected_res_list.json", function(connected_res){
                    if (connected_res != null){
                        for (var i=0; i<connected_res.length; i++){
                            $("<option></option>", {value: connected_res[i].connected_res_id, text: connected_res[i].res_name}).appendTo('.connected_res');
                        }
                    }
                })



            },
            error: function(xhr, str){
                alert('Возникла ошибка: ' + xhr.responseText);
            }
        })
    }
    else{
        $("#coll_allow_type").val('');
        $(".k-treeview").data("kendoTreeView").remove(".k-item");
    }
}

function convertAdditionalParams(res_params_dict, spec_param_list){
    // convert spec params to smart dict and set type

    for (var i=0; i<spec_param_list.length; i++){
        // get child from parent
        if (spec_param_list[i].children_spec != undefined){
            // set parent to dict type
            res_params_dict.additional_parameters[spec_param_list[i].param_name] = {};
            // get every child
            _getEveryChild(res_params_dict.additional_parameters[spec_param_list[i].param_name], spec_param_list[i])

        }
        // for parent set type
        else{
            if (spec_param_list[i].param_type == 'dict')
                res_params_dict.additional_parameters[spec_param_list[i].param_name] = {};
            else if (spec_param_list[i].param_type == 'list')
                res_params_dict.additional_parameters[spec_param_list[i].param_name] = [];
            else if (spec_param_list[i].param_type == 'integer')
            // mark empty integer
                res_params_dict[spec_param_list[i].param_name] = null;
            else
                res_params_dict.additional_parameters[spec_param_list[i].param_name] = '';
        }
    }

    return res_params_dict
}

function _getEveryChild(res_params_dict, spec_param_list){
    // child
    for (var k=0; k<spec_param_list.children_spec.length; k++){
        // check type of child & set type
        if (spec_param_list.children_spec[k].children_spec == undefined){
            if (spec_param_list.children_spec[k].param_type == 'dict')
                res_params_dict[spec_param_list.children_spec[k].param_name] = {};
            else if (spec_param_list.children_spec[k].param_type == 'list')
                res_params_dict[spec_param_list.children_spec[k].param_name] = [];
            else if (spec_param_list.children_spec[k].param_type == 'integer')
            // mark empty integer
                res_params_dict[spec_param_list.children_spec[k].param_name] = null;
            else
                res_params_dict[spec_param_list.children_spec[k].param_name] = ''
        }
        // call recursive for get next child
        else{
            res_params_dict[spec_param_list.children_spec[k].param_name] = {};
            _getEveryChild(res_params_dict[spec_param_list.children_spec[k].param_name], spec_param_list.children_spec[k])
        }
    }
}
function getResForEdit(res_id, elem_type){
    if (elem_type == ELEM_TYPE.IS_RES)
        window.location = "/resource/?elem_id=" + escape(res_id);
    else if(elem_type == ELEM_TYPE.IS_CONN)
        window.location = "/connection/?elem_id=" + escape(res_id);
    else if (elem_type == ELEM_TYPE.IS_COLL)
        window.location = "/collection/?elem_id=" + escape(res_id);
    //alert('llll')
    //SPEC_PARAM_LIST = spec_param_list;
    //ITEMS.push({ id: 'root_node', text: 'List of specification parameters',items: []}); //expanded: true,
    //if (items != undefined){
//        ITEMS[0].items = items;
        //alert($.toJSON(ITEMS))
 //       treeView.append(ITEMS);
   //     $(".k-first .k-in").dblclick()
   // }
}
function searchResource(){

    //if ($("#res_s_name").val() != ''){
        var hiddenField = document.createElement("input");
        hiddenField.setAttribute("type", "hidden");
        hiddenField.setAttribute("name", "res_s_name");
        hiddenField.setAttribute("value", $("#res_s_name").val());
        var hiddenField1 = document.createElement("input");
        hiddenField1.setAttribute("type", "hidden");
        hiddenField1.setAttribute("name", "res_s_stat");
        hiddenField1.setAttribute("value", $("#res_s_stat").val());
        var hiddenField2 = document.createElement("input");
        hiddenField1.setAttribute("type", "hidden");
        hiddenField1.setAttribute("name", "res_s_ext_sys");
        hiddenField1.setAttribute("value", $("#res_s_ext_sys").val());

        var form = document.createElement("form");
        form.setAttribute("method", "GET");
        form.appendChild(hiddenField);
        form.appendChild(hiddenField2);
        form.submit();


        /*        var data_dict = {};
         data_dict['spec_type'] = spec_type;
         data_dict['s'] = $("#spec_search").val();
         $.ajax({
         type: "GET",
         url: "/spec_search_res/",
         data: data_dict,
         success: function(items){ alert('ok')}
         })*/

    //}
    //else{
    //    $('#alert_1').remove();
    //    $('#search_err').append('<div id="alert_1" class="span7 alert alert-error">' +
    //        '<button type="button" class="close" data-dismiss="alert">×</button>' +
    //        '<strong>Error!</strong> Please, input the search data!</div>');
    //}
}

function saveElement(elem_type){
    if (_checkRequiredSave() == true) {
        var data_dict = {};
            data_dict['elem_id'] = $('#res_id').val();

            if (SELECTED_OPT == '')
                data_dict['res_name'] = $("#root_opt").val();
            else
                data_dict['res_name'] = SELECTED_OPT;

            //data_dict['res_id'] = SELECTED_ID;
            data_dict['res_type'] = elem_type;
            data_dict['res_status'] = $('#res_status').val();
            data_dict['res_desc'] = $('#res_desc').val();
            data_dict['res_sys'] = $('#res_sys').val();
            data_dict['res_loc'] = $('#res_loc').val();
            data_dict['res_dep'] = $('#res_dep').val();
            data_dict['res_own'] = $('#res_own').val();
            // collection
            data_dict['coll_allow_type'] = $('#coll_allow_type').val();
            // connection
            data_dict['connected_res_id'] = $("#connected_res_name_id option:selected").val();
            data_dict['connecting_res_id'] = $("#connecting_res_name_id option:selected").val();

        //data_dict['res_collect'] = $('#res_collect').val();
            data_dict['res_param'] = $.toJSON(RES_PARAM_DICT.additional_parameters);

    // add collection to resource

        if (document.getElementById('test') != undefined){
            data_dict['old_assigned_to_coll'] = $.toJSON(ASSIGNED_COLL_LIS);
            data_dict['new_assigned_to_coll'] = $.toJSON(transfer.get_values());
        }
        else{
            data_dict['old_assigned_to_coll'] = '';
            data_dict['new_assigned_to_coll'] = ''
        }


    $.ajax({
        type: "POST",
        url: "/save_element/",
        data: data_dict,
        success: function(){
            jAlert('Element saved successfully!', 'Success', function(){
                if (elem_type == ELEM_TYPE.IS_RES)
                    window.location = "/resource_search/";
                else if (elem_type == ELEM_TYPE.IS_COLL)
                    window.location = "/collection_search/";
                else if (elem_type == ELEM_TYPE.IS_CONN)
                    window.location = "/collection_search/";
            })
        },
        error: function(xhr, str,f,t){
            //alert(xhr.responseText)
            str = xhr.responseText;
            //var txtRegex = /\w+\n/;
                //   /^\d+$/;
            //var txtRexex = new  RegExp('\\w', 'ig');
            var re = /(.+)?(\n)?(.+)/m;
            var found = str.match(re);

            var result = re.exec(str);

            //str="http//www.somedomain.ru/index2.html";
            //re=new RegExp("((\w+): \/\/)?([^/]+) (.*)?","i");
            //result=re.exec(str);

//BIValueError at /save_res/
//            [Blik Inventory ValueError] Parameter "idx" should has integer value, but "f" occured!
//BIException at /save_spec/
//[Blik Inventory ValueError] Parameter "idx" should has integer value, but "f" occured!
//[Blik Inventory Exception] Specification type <spec_type> is not supported!

            //alert(t) replace(/^\s+|\s+$/g,"")
            //for (i=0; i<xhr.length; i++){
            //found = str.match(re);

            //alert(found)
            //jAlert(found, 'Error')
            //    alert(xhr[i])
            //}
               alert('Возникла ошибка: ' + found);
        }
        })
    }
}
var show = true;
function showCollect(){
    //var show = true;
    if (show == true){
        $('#collection').show();
        $('#show_collect').text('Hide collection');
        show = false;
    }
    else{
    //$('#show_collect').append('<i class="icon-ok-sign"></i>Hide collection');
        $('#show_collect').text('Show collection');
        $('#collection').hide();
        show = true
    }
}

function updateParamRes(){
    $('#field_err').remove();

    var param_name = $('#param_name').val();
    var param_type = $('#param_type').val();

    if (param_name != ''){
        var res_parent_list = [];
            res_parent_list.push(SELECTED_NAME);
            res_parent_list = _getParentRes(NODE, res_parent_list);

        _updateParamRes(res_parent_list, RES_PARAM_DICT.additional_parameters, param_type);
        $.gritter.add({
            title:  'Blik inventory',
            text:   'Updated successfully!',
            sticky: false
        });

        $("#save_res").removeAttr("disabled");

    }
    else{
        // TODO make error by label
        jAlert('Fill the parameter value!');
    }
}

function _getParentRes(node, parent_list){
    var name = node.parentNode.parentNode.textContent.match(/\w+/);
    // if not root_id in treeMenu
    if (name != 'List'){
        parent_list.push(name);
        _getParentRes(node.parentNode.parentNode, parent_list)
    }
    return parent_list
}

function _updateParamRes(res_parent_list, res_params_dict, param_type){
    var parent1 = res_parent_list.pop();

    if (res_parent_list.length != 0){
        _updateParamRes(res_parent_list, res_params_dict[parent1], param_type)
    }
    else{
        var param_name = $("#param_name").val();
        if (param_type == 'list'){
            // make structure like: param = ['value']
            var arr = new Array();
            arr[0] = param_name;
            res_params_dict[parent1] = arr;
        }
        else if (param_type == 'integer'){
            var intRegex = /^\d+$/;
            if(intRegex.test(param_name)){
                res_params_dict[parent1] = param_name;
            }
            else
                jAlert('Parameter value must be a integer!')
        }
        else
            res_params_dict[parent1] = param_name;
    }
}

function getResParams(selectedNode){
    var name = selectedNode.textContent.match(/\w+/);

    if (name == 'List'){
        _clear_form_elements();
        $("#add_spec").removeAttr("disabled");
        $("#update_spec").attr("disabled", "disabled");

        // set resource form
        if (document.getElementById('param_name_res') != null){
            $("#param_name_res").text('Parameter');
            $("#lbl_param_name").text('Parameter name');

            //$(".hide_elem").show();
            $("#btn_add_res_param").attr('disabled', 'disabled');
            $("#param_name").attr('disabled', 'disabled')
        }
    }
    // get param from children
    else{
        $("#add_spec").attr("disabled", "disabled");
        $("#update_spec").removeAttr("disabled");
        var parent_res_list = [];
        parent_res_list.push(SELECTED_NAME);
        parent_res_list = _getParentRes(NODE, parent_res_list);

        // make copy of parent list
        RES_PARENT_LIST = parent_res_list.slice();

        _getResParam(parent_res_list, RES_PARAM_DICT.additional_parameters, SPEC_PARAM_LIST);
    }
}

function _getResParam(parent_res_list, res_param_dict, spec_param_list){
    // display parent & child items on TreeMenu. Hide & show parameters.

    var parent = parent_res_list.pop();

    for (var i=0; i<spec_param_list.length; i++){
        if (spec_param_list[i].param_name != parent)
            continue;
        else{
            if (spec_param_list[i].param_name == SELECTED_NAME){
                var param_name = $("#param_name");
                // display parent resource params
                if (spec_param_list[i].children_spec != undefined){
                    $("#lbl_param_name").text('Parameter name');
                    $("#param_name_res").text(spec_param_list[i].param_name);

                    _assignedResParams(spec_param_list[i], true);

                    param_name.attr('disabled', 'disabled');
                    $("#update_spec").attr('disabled', true);

                }
                // display child resource params
                else{
                    $("#lbl_param_name").text('Parameter value');
                    $("#param_name_res").text(spec_param_list[i].param_name);

                    param_name.removeAttr('disabled');

                    param_name.val('');
                    $("#param_type").val(spec_param_list[i].param_type);
                    $("#param_desc").val(spec_param_list[i].description);
                    $("#pos_value").val(spec_param_list[i].possible_values);
                    $("#def_value").val(spec_param_list[i].default_value);

                    if(spec_param_list[i].mandatory == true)
                        $("#mandatory").attr('checked',true).trigger('change');
                    else
                        $("#mandatory").attr('checked',false).trigger('change');

                    param_name.val(res_param_dict[SELECTED_NAME]);
                }
            }
            else
                _getResParam(parent_res_list, res_param_dict[spec_param_list[i].param_name], spec_param_list[i].children_spec)
        }
    }
}

function _assignedResParams(spec_param_list, param_name){
    $(".hide_elem").show();
    $("#btn_add_res_param").attr('disabled', 'disabled');

    if (param_name == true)
        $("#param_name").val(spec_param_list.param_name);
    else
        // clear param_name for child
        $("#param_name").val('');

    $("#param_type").val(spec_param_list.param_type);
    $("#param_desc").val(spec_param_list.description);
    $("#pos_value").val(spec_param_list.possible_values);
    $("#def_value").val(spec_param_list.default_value);

    if(spec_param_list.mandatory == 'Yes')
        $("#mandatory").attr('checked',true).trigger('change');
    else
        $("#mandatory").attr('checked',false).trigger('change')
}

/*function _checkRequiredSave() {
    var err = 0;
    $("#form_res").find('.required').each(function() {
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
        return true
    else
        return false
}*/