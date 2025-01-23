document.getElementById('study-guide-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const content = document.getElementById('content').value;
    const response = await fetch('/api/create-pdf', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ content })
    });
    const result = await response.json();
    const messageDiv = document.getElementById('message');
    if (result.success) {
        messageDiv.textContent = 'PDF created successfully!';
    } else {
        messageDiv.textContent = 'Failed to create PDF.';
    }
});
