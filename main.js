
function sendAPIRequest() {
    const apiRequest = document.getElementById("api-request").value;
    const responseDiv = document.getElementById("response-div");
    responseDiv.innerHTML = 'Thinking of the best solution to your prompt... \
    <br>Sip some &#9749; and wait for magic';
    
    const requestOptions = {
        method: 'POST',
        cache: "no-cache",
        headers: { 'Content-Type':  'application/json' },
        body: JSON.stringify({ 'api_request': apiRequest })
    };
    console.log(requestOptions);
    fetch('http://127.0.0.1:9000/getInformation', requestOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            
            responseDiv.innerHTML = data.code;
            Prism.highlightAll();
            console.log(data);
        })
        .catch(error => console.error(error));

}