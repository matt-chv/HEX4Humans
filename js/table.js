function show_all(){
   console.log("show_all");
   show_hide("all","table-row");
   show_hide("r","table-row");
}

function show_bf_delta(){
   console.log("show_bf_delta");
}

function show_reset_delta(){
   console.log("show_reset_delta");
   show_hide("all","none");
   show_hide("r","table-row");
}


function show_hide(cls,on) {
   /* cls = class name */
   console.log("called show_hide_row",cls,on);
    var lst = document.getElementsByClassName(cls);
    for(var i = 0; i < lst.length; ++i) {
        lst[i].style.display = on; /* ? '' : 'none';*/
        console.log(i,lst[i].style.display  );
    }
}
