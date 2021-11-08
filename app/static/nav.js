function go_to(datecode) {
    window.location.href = "/" + datecode;
}

function show_only_this(id) {
    if (id == "zero") { document.getElementById(id).style.display = "block"; }
    else { document.getElementById("zero").style.display = "none"; }

    if (id == "one") { document.getElementById(id).style.display = "block"; }
    else { document.getElementById("one").style.display = "none"; }

    if (id == "two") { document.getElementById(id).style.display = "block"; }
    else { document.getElementById("two").style.display = "none"; }

    if (id == "three") { document.getElementById(id).style.display = "block"; }
    else { document.getElementById("three").style.display = "none"; }
}