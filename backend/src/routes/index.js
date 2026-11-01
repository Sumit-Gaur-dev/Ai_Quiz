import { Router } from 'express';
import healthRouter from './health.js';
import authRouter from '../modules/auth/auth.routes.js';
import profilesRouter from '../modules/profiles/profiles.routes.js';

const router = Router();

router.use('/health', healthRouter);
router.use('/auth', authRouter);
router.use('/profiles', profilesRouter);

export default router;
