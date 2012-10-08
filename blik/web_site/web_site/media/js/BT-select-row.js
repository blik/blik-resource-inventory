$(document).ready(function() {
    /* Add/remove class to a row when clicked on */
    $('#addParams tr').click( function() {
        $(this).toggleClass('row_selected');
    } );
     
    /* Init the table */
    var oTable = $('#addParams').dataTable( );
} );