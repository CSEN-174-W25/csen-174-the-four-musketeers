/**
 * @jest-environment jsdom
 */

const fs = require('fs');
const path = require('path');
const html = fs.readFileSync(path.resolve(__dirname, '../index.html'), 'utf8');

describe('script.js', () => {
    let fetchMock;

    beforeEach(() => {
        document.documentElement.innerHTML = html.toString();
        fetchMock = jest.spyOn(global, 'fetch').mockImplementation(() =>
            Promise.resolve({
                json: () => Promise.resolve({ success: true })
            })
        );
    });

    afterEach(() => {
        fetchMock.mockRestore();
    });

    test('should display success message on successful PDF creation', async () => {
        const form = document.getElementById('study-guide-form');
        const content = document.getElementById('content');
        const messageDiv = document.getElementById('message');

        content.value = 'Test content';
        form.dispatchEvent(new Event('submit'));

        await new Promise(process.nextTick);

        expect(fetchMock).toHaveBeenCalledTimes(1);
        expect(messageDiv.textContent).toBe('PDF created successfully!');
    });

    test('should display failure message on PDF creation failure', async () => {
        fetchMock.mockImplementationOnce(() =>
            Promise.resolve({
                json: () => Promise.resolve({ success: false })
            })
        );

        const form = document.getElementById('study-guide-form');
        const content = document.getElementById('content');
        const messageDiv = document.getElementById('message');

        content.value = 'Test content';
        form.dispatchEvent(new Event('submit'));

        await new Promise(process.nextTick);

        expect(fetchMock).toHaveBeenCalledTimes(1);
        expect(messageDiv.textContent).toBe('Failed to create PDF.');
    });

    test('should handle file upload and display success message', async () => {
        const form = document.getElementById('study-guide-form');
        const content = document.getElementById('content');
        const fileInput = document.getElementById('file-upload');
        const messageDiv = document.getElementById('message');

        content.value = 'Test content';
        const file = new File(['file content'], 'test.txt', { type: 'text/plain' });
        Object.defineProperty(fileInput, 'files', {
            value: [file]
        });

        form.dispatchEvent(new Event('submit'));

        await new Promise(process.nextTick);

        expect(fetchMock).toHaveBeenCalledTimes(1);
        expect(messageDiv.textContent).toBe('PDF created successfully!');
    });

    test('should display failure message when content is missing', async () => {
        const form = document.getElementById('study-guide-form');
        const messageDiv = document.getElementById('message');

        form.dispatchEvent(new Event('submit'));

        await new Promise(process.nextTick);

        expect(fetchMock).toHaveBeenCalledTimes(1);
        expect(messageDiv.textContent).toBe('Failed to create PDF.');
    });

    test('should display failure message on server error', async () => {
        fetchMock.mockImplementationOnce(() => Promise.reject(new Error('Test error')));

        const form = document.getElementById('study-guide-form');
        const content = document.getElementById('content');
        const messageDiv = document.getElementById('message');

        content.value = 'Test content';
        form.dispatchEvent(new Event('submit'));

        await new Promise(process.nextTick);

        expect(fetchMock).toHaveBeenCalledTimes(1);
        expect(messageDiv.textContent).toBe('Failed to create PDF.');
    });
});
