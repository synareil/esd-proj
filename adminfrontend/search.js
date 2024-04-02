//To include this search function in the homepage/index.html
document.getElementById("searchinput")
    .addEventListener("keyup", function (event) {
        event.preventDefault();
        if (event.keyCode === 13) {
            document.getElementById("button-addon2").click();
        }
    });
// search script
function search() {
    keyword = document.getElementById("searchinput").value.toLowerCase();
    //   if (localStorage.getItem("search") !== null) {
    //     localStorage.removeItem("search")
    //   }
    localStorage.setItem("search", keyword)
    window.location.assign(`/search.html`);
}

