import { Router } from 'express';
import { requireAuth } from '../../middleware/auth.js';
import * as authController from './auth.controller.js';

const router = Router();

router.get('/me', requireAuth, authController.getMe);

export default router;

