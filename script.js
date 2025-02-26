document.getElementById('study-guide-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const content = document.getElementById('content').value;
    const fileInput = document.getElementById('file-upload');
    const formData = new FormData();
    formData.append('content', content);
    if (fileInput.files.length > 0) {
        formData.append('file', fileInput.files[0]);
    }
    const response = await fetch('/api/create-pdf', {
        method: 'POST',
        body: formData
    });
    const result = await response.json();
    const messageDiv = document.getElementById('message');
    if (result.success) {
        messageDiv.textContent = 'PDF created successfully!';
    } else {
        messageDiv.textContent = 'Failed to create PDF.';
    }
});
