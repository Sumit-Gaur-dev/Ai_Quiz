import { Router } from 'express';
import { requireAuth } from '../../middleware/auth.js';
import { validate } from '../../middleware/validate.js';
import { updateProfileSchema } from './profiles.schema.js';
import * as profilesController from './profiles.controller.js';

const router = Router();

router.get('/me', requireAuth, profilesController.getProfile);
router.patch('/me', requireAuth, validate(updateProfileSchema, 'body'), profilesController.updateProfile);

export default router;

