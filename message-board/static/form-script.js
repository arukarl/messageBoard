const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);

let author = urlParams.get('author');
const loc = urlParams.get('location');
const desc = urlParams.get('description');

if (author !== null && author !== "") {
    document.getElementById("author").value = author;
}

document.getElementById("location").value = loc;
document.getElementById("description").value = desc;
