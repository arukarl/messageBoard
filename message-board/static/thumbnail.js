const img = document.getElementById("thumbnail");
img.onerror = () => {
  img.src = "https://d3jwmvy177h8cq.cloudfront.net/static/loading.gif";
};
