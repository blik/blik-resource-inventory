var oTable;
 
$(document).ready(function() {
    alert('1')
    /* Add a click handler to the rows - this could be used as a callback */
    $("#search tbody tr").click( function( e ) {
        alert('2')
        if ( $(this).hasClass('row_selected') ) {
            $(this).removeClass('row_selected');
        }
        else {
            oTable.$('tr.row_selected').removeClass('row_selected');
            $(this).addClass('row_selected');
        }
    });
     
    /* Add a click handler for the delete row */
    $('#delete').click( function() {
        var anSelected = fnGetSelected( oTable );
        if ( anSelected.length !== 0 ) {
            oTable.fnDeleteRow( anSelected[0] );
        }
    } );
     
    /* Init the table */
    oTable = $('#search').dataTable( );
} );
