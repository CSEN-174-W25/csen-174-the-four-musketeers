const express = require('express');
const bodyParser = require('body-parser');
const pdf = require('html-pdf');
const path = require('path');
const multer = require('multer');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

const upload = multer({ dest: 'uploads/' });

app.use(bodyParser.json());
app.use(express.static(path.join(__dirname)));

app.post('/api/create-pdf', upload.single('file'), (req, res) => {
    const { content } = req.body;
    let html = `<html><body>${content}</body></html>`;
    if (req.file) {
        const filePath = path.join(__dirname, req.file.path);
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

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
