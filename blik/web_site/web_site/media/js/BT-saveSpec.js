function save1(){
	var form = document.createElement("form");
    form.setAttribute("method", "post");

    input_name = document.getElementById('name_spec').value;
    input_parent = document.getElementById('parent_spec').value;

    var hiddenField = document.createElement("input");
    hiddenField.setAttribute("type", "hidden");
    hiddenField.setAttribute("name", "name");
    hiddenField.setAttribute("value", input_name);

    var hiddenField2 = document.createElement("input");
    hiddenField2.setAttribute("type", "hidden");
    hiddenField2.setAttribute("name", "parent");
    hiddenField2.setAttribute("value", input_parent);

    form.appendChild(hiddenField);
    form.appendChild(hiddenField2);
    document.body.appendChild(form);
    form.submit();
	}
}
