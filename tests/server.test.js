const request = require('supertest');
const express = require('express');
const bodyParser = require('body-parser');
const multer = require('multer');
const fs = require('fs');
const path = require('path');
const pdf = require('html-pdf');

const app = express();
const upload = multer({ dest: 'uploads/' });

app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, '../')));

app.post('/api/create-pdf', upload.single('file'), (req, res) => {
    const { content } = req.body;
    if (!content) {
        return res.json({ success: false });
    }
    let html = `<html><body>${content}</body></html>`;
    if (req.file) {
        const filePath = path.join(__dirname, '../', req.file.path);
        const fileContent = fs.readFileSync(filePath, 'utf8');
        html += `<div>${fileContent}</div>`;
        fs.unlinkSync(filePath);
    }
    pdf.create(html).toFile('study-guide.pdf', (err, result) => {
        if (err) {
            return res.json({ success: false });
        }
        res.json({ success: true });
    });
});

describe('POST /api/create-pdf', () => {
    test('should create PDF from provided content', async () => {
        const response = await request(app)
            .post('/api/create-pdf')
            .send({ content: 'Test content' })
            .set('Accept', 'application/json');
        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
    });

    test('should create PDF from provided content and uploaded file', async () => {
        const response = await request(app)
            .post('/api/create-pdf')
            .field('content', 'Test content')
            .attach('file', Buffer.from('File content'), 'test.txt');
        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
    });

    test('should return failure when content is missing', async () => {
        const response = await request(app)
            .post('/api/create-pdf')
            .send({})
            .set('Accept', 'application/json');
        expect(response.status).toBe(200);
        expect(response.body.success).toBe(false);
    });

    test('should handle empty file upload gracefully', async () => {
        const response = await request(app)
            .post('/api/create-pdf')
            .field('content', 'Test content')
            .attach('file', Buffer.from(''), 'test.txt');
        expect(response.status).toBe(200);
        expect(response.body.success).toBe(true);
    });

    test('should return failure on server error', async () => {
        jest.spyOn(pdf, 'create').mockImplementation(() => ({
            toFile: (path, callback) => callback(new Error('Test error'))
        }));
        const response = await request(app)
            .post('/api/create-pdf')
            .send({ content: 'Test content' })
            .set('Accept', 'application/json');
        expect(response.status).toBe(200);
        expect(response.body.success).toBe(false);
    });
});
