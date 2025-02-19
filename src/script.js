function setupFormSubmission() {
    const form = document.getElementById('study-guide-form');
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const content = document.getElementById('content').value;
        const fileInput = document.getElementById('file-upload');
        const messageDiv = document.getElementById('message');

        if (!content) {
            messageDiv.textContent = 'Failed to create the PDF.';
            return;
        }

        const formData = new FormData();
        formData.append('content', content);
        if (fileInput.files.length > 0) {
            formData.append('file', fileInput.files[0]);
        }

        try {
            const response = await fetch('/api/create-pdf', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            if (result.success) {
                messageDiv.textContent = 'PDF created successfully!';
            } else {
                messageDiv.textContent = 'Failed to create PDF.';
            }
        } catch (error) {
            messageDiv.textContent = 'Failed to create PDF.';
        }
    });
}

module.exports = { setupFormSubmission };
