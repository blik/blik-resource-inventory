function delete_item(del_id){
  jConfirm('<strong>Do you want delete specification?</strong>', 'Confirmation Dialog', function(r) {
    if (r == true){
      var form = document.createElement("form");
        form.setAttribute("method", "post");

      var hiddenField = document.createElement("input");
        hiddenField.setAttribute("type", "hidden");
        hiddenField.setAttribute("name", "del_id");
        hiddenField.setAttribute("value", del_id);


    form.appendChild(hiddenField);
    document.body.appendChild(form);
    form.submit();

    oTable = $('#search').dataTable( );
    }
  });
}

function getInfo(item_id) {
   var form1 = document.createElement("form");
    form.setAttribute("method", "post");

  var hiddenField = document.createElement("input");
    hiddenField.setAttribute("type", "hidden");
    hiddenField.setAttribute("name", "item_id");
    hiddenField.setAttribute("value", item_id);

    form1.appendChild(hiddenField);
    document.body.appendChild(form1);
    form1.submit();

}