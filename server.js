// server.js
const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

// Initialize Express app
const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health Check Route
app.get('/health', (req, res) => {
    res.status(200).json({
        status: 'ok',
        message: 'Education District IV Portal API is running!',
        timestamp: new Date().toISOString()
    });
});

// Welcome Route
app.get('/', (req, res) => {
    res.json({
        message: 'Welcome to Education District IV Portal API',
        version: '1.0.0',
        endpoints: [
            '/health - Health check',
            '/api/files - File management',
            '/api/staff - Staff management',
            '/api/students - Student management'
        ]
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`
    🏫 Education District IV Portal API
    🚀 Server running on http://localhost:${PORT}
    📅 Started at: ${new Date().toLocaleString()}
    `);
});