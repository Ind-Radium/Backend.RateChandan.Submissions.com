const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;
const FILE_PATH = path.join(__dirname, 'submissions.json');

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Ensure the file exists
if (!fs.existsSync(FILE_PATH)) {
    fs.writeFileSync(FILE_PATH, JSON.stringify([]));
}

// Endpoint to save a submission
app.post('/submit', (req, res) => {
    const { rating, comment } = req.body;

    if (rating === undefined || rating < 0 || rating > 100) {
        return res.status(400).json({ message: 'Invalid rating. Rating must be between 0 and 100.' });
    }

    const submissions = JSON.parse(fs.readFileSync(FILE_PATH));
    const newSubmission = {
        user: `User ${submissions.length + 1}`,
        rating,
        comment: comment || 'No comment provided.',
    };
    submissions.push(newSubmission);

    fs.writeFileSync(FILE_PATH, JSON.stringify(submissions, null, 2));
    res.json({ message: 'Submission saved successfully!' });
});

// Endpoint to fetch all submissions (admin access)
app.get('/submissions', (req, res) => {
    const submissions = JSON.parse(fs.readFileSync(FILE_PATH));
    res.json(submissions);
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
