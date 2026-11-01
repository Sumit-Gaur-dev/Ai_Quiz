/**
 * Middleware factory to validate request body, query, or params using Zod.
 *
 * @param {import('zod').ZodSchema} schema
 * @param {'body'|'query'|'params'} source
 */
export const validate = (schema, source = 'body') => {
  return (req, res, next) => {
    const result = schema.safeParse(req[source]);

    if (!result.success) {
      const issues = result.error.issues || result.error.errors || [];
      const details = issues.map((err) => ({
        path: Array.isArray(err.path) ? err.path.join('.') : '',
        message: err.message,
      }));

      return res.status(400).json({
        error: {
          code: 'VALIDATION_ERROR',
          message: 'Invalid request data',
          details,
        },
      });
    }

    req[source] = result.data;
    next();
  };
};
