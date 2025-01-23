const express = require('express');
const bodyParser = require('body-parser');
const pdf = require('html-pdf');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(bodyParser.json());
app.use(express.static(path.join(__dirname)));

app.post('/api/create-pdf', (req, res) => {
    const { content } = req.body;
    const html = `<html><body>${content}</body></html>`;
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
