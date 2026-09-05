import express from 'express';
import cors from 'cors';

const app = express();
app.use(cors());
app.use(express.json());

app.get('/health', (req, res) => res.send('OK'));

const port = process.env.PORT || 3001;
app.listen(port, () => console.log(`Backend running on port ${port}`));
