function startDownload() {
    const formData = new FormData(document.getElementById('downloadForm'));
    fetch('/start_download', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('progress').innerText = data.message;
    })
    .catch(error => {
        document.getElementById('progress').innerText = 'Error: ' + error.message;
    });
}