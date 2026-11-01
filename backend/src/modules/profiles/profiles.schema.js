import { z } from 'zod';

export const updateProfileSchema = z
  .object({
    display_name: z
      .string({ required_error: 'display_name is required' })
      .trim()
      .min(1, 'display_name must be at least 1 character')
      .max(100, 'display_name must not exceed 100 characters'),
  })
  .strict({
    message: 'Unrecognized field in request body. user_id cannot be modified.',
  });

