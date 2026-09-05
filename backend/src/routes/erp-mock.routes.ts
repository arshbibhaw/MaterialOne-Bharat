// Express routes for erp-mock
// Simulates real SAP/ERP integration for prototype phase
import { Router } from 'express';
const router = Router();
router.post('/push', (req, res) => {
    console.log('Received SAP-IDoc-style JSON payload', req.body);
    res.json({ success: true, message: 'Mock ERP push received' });
});
export default router;
