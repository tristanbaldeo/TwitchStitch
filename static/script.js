function startDownload() {
    const formData = new FormData(document.getElementById('downloadForm'));
    fetch('/start_download', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            document.getElementById('progress').innerText = data.message;
            pollProgress();
        } else {
            document.getElementById('progress').innerText = 'Error: ' + data.message;
        }
    })
    .catch(error => {
        document.getElementById('progress').innerText = 'Error: ' + error.message;
    });
}

function pollProgress() {
    fetch('/progress')
    .then(response => response.json())
    .then(data => {
        if (data.status === 'Compiling clips...') {
            document.getElementById('progress').innerText = `${data.status}`;
        } else {
            document.getElementById('progress').innerText = `${data.status}\n${data.progress}%`;
        }

        if (data.status !== 'Complete') {
            setTimeout(pollProgress, 1000);
        }
    })
    .catch(error => {
        document.getElementById('progress').innerText = 'Error: ' + error.message;
    });
}
