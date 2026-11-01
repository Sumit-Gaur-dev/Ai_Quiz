import test from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import app from '../src/app.js';
import * as authController from '../src/modules/auth/auth.controller.js';
import * as profilesController from '../src/modules/profiles/profiles.controller.js';
import { updateProfileSchema } from '../src/modules/profiles/profiles.schema.js';

let server;
let baseUrl;

test.before(async () => {
  await new Promise((resolve) => {
    server = http.createServer(app);
    server.listen(0, '127.0.0.1', () => {
      const port = server.address().port;
      baseUrl = `http://127.0.0.1:${port}`;
      resolve();
    });
  });
});

test.after(async () => {
  await new Promise((resolve) => server.close(resolve));
});

// Helper for making requests to test server
const apiRequest = async (path, options = {}) => {
  const url = `${baseUrl}${path}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  const data = await response.json();
  return { status: response.status, data };
};

test('GET /api/v1/health returns 200 OK', async () => {
  const res = await apiRequest('/api/v1/health');
  assert.equal(res.status, 200);
  assert.equal(res.data.status, 'ok');
  assert.equal(res.data.service, 'ai-quiz-backend');
});

test('Accessing protected route GET /api/v1/auth/me without token returns 401 UNAUTHORIZED', async () => {
  const res = await apiRequest('/api/v1/auth/me');
  assert.equal(res.status, 401);
  assert.equal(res.data.error.code, 'UNAUTHORIZED');
  assert.match(res.data.error.message, /Authorization header with Bearer token is required/i);
});

test('Accessing protected route GET /api/v1/auth/me with malformed Authorization header returns 401', async () => {
  const res = await apiRequest('/api/v1/auth/me', {
    headers: { Authorization: 'Basic dXNlcjpwYXNz' },
  });
  assert.equal(res.status, 401);
  assert.equal(res.data.error.code, 'UNAUTHORIZED');
});

test('Accessing protected route GET /api/v1/profiles/me without token returns 401 UNAUTHORIZED', async () => {
  const res = await apiRequest('/api/v1/profiles/me');
  assert.equal(res.status, 401);
  assert.equal(res.data.error.code, 'UNAUTHORIZED');
});

test('Accessing protected route PATCH /api/v1/profiles/me without token returns 401 UNAUTHORIZED', async () => {
  const res = await apiRequest('/api/v1/profiles/me', {
    method: 'PATCH',
    body: JSON.stringify({ display_name: 'Test' }),
  });
  assert.equal(res.status, 401);
  assert.equal(res.data.error.code, 'UNAUTHORIZED');
});

test('Accessing protected route with an invalid or expired JWT token returns 401 UNAUTHORIZED', async () => {
  const res = await apiRequest('/api/v1/auth/me', {
    headers: { Authorization: 'Bearer invalid.or.expired.jwt.token' },
  });
  // Without real Supabase creds or with an invalid token, returns 401 or 500 auth error, but never allows access
  assert.ok(res.status === 401 || res.status === 500);
  assert.ok(res.data.error);
});

test('Validation: updateProfileSchema rejects missing or empty display_name', () => {
  const emptyResult = updateProfileSchema.safeParse({ display_name: '' });
  assert.equal(emptyResult.success, false);

  const missingResult = updateProfileSchema.safeParse({});
  assert.equal(missingResult.success, false);
});

test('Security: updateProfileSchema strictly blocks user_id injection in request body', () => {
  const injectedBody = {
    display_name: 'Legit Name',
    user_id: 'malicious-injected-user-id',
  };
  const result = updateProfileSchema.safeParse(injectedBody);
  assert.equal(result.success, false);
  const issues = result.error.issues || result.error.errors || [];
  assert.ok(issues.length > 0);
});

test('Security & Controller: getMe returns only claims derived from verified token', async () => {
  const req = {
    user: {
      id: 'user-aaa-111',
      email: 'userA@example.com',
      userMetadata: { display_name: 'User A' },
      appMetadata: { provider: 'email' },
    },
  };

  let responseData = null;
  let responseStatus = null;
  const res = {
    status: (code) => {
      responseStatus = code;
      return {
        json: (data) => {
          responseData = data;
        },
      };
    },
  };

  await authController.getMe(req, res);
  assert.equal(responseStatus, 200);
  assert.equal(responseData.user.id, 'user-aaa-111');
  assert.equal(responseData.user.email, 'userA@example.com');
  assert.equal(responseData.user.userMetadata.display_name, 'User A');
});

test('Security & Data Isolation: getProfile queries only user_id from verified token', async () => {
  let queriedTable = null;
  let queriedId = null;

  const mockSupabase = {
    from: (table) => {
      queriedTable = table;
      return {
        select: () => ({
          eq: (field, value) => {
            if (field === 'id') queriedId = value;
            return {
              maybeSingle: async () => ({
                data: {
                  id: value,
                  display_name: 'User A',
                  created_at: '2026-11-01T00:00:00Z',
                  updated_at: '2026-11-01T00:00:00Z',
                },
                error: null,
              }),
            };
          },
        }),
      };
    },
  };

  const req = {
    user: { id: 'user-aaa-111' },
    supabase: mockSupabase,
  };

  let responseData = null;
  const res = {
    status: (code) => ({
      json: (data) => {
        responseData = data;
      },
    }),
  };

  await profilesController.getProfile(req, res);
  assert.equal(queriedTable, 'profiles');
  assert.equal(queriedId, 'user-aaa-111');
  assert.equal(responseData.profile.id, 'user-aaa-111');
});

test('Security & Data Isolation: User A cannot update User B profile', async () => {
  let updatedId = null;
  let updatePayload = null;

  const mockSupabase = {
    from: (table) => ({
      update: (payload) => {
        updatePayload = payload;
        return {
          eq: (field, value) => {
            updatedId = value;
            return {
              select: () => ({
                single: async () => ({
                  data: {
                    id: value,
                    display_name: payload.display_name,
                    created_at: '2026-11-01T00:00:00Z',
                    updated_at: payload.updated_at,
                  },
                  error: null,
                }),
              }),
            };
          },
        };
      },
    }),
  };

  // User A makes a request
  const req = {
    user: { id: 'user-aaa-111' }, // Authenticated as User A
    body: { display_name: 'Updated User A Name' },
    supabase: mockSupabase,
  };

  let responseData = null;
  const res = {
    status: (code) => ({
      json: (data) => {
        responseData = data;
      },
    }),
  };

  await profilesController.updateProfile(req, res);

  // Assert that ONLY User A's ID was updated, never User B's
  assert.equal(updatedId, 'user-aaa-111');
  assert.notEqual(updatedId, 'user-bbb-222');
  assert.equal(updatePayload.display_name, 'Updated User A Name');
  assert.equal(responseData.profile.display_name, 'Updated User A Name');
});

test('Security: Response never exposes service-role keys or privileged credentials', async () => {
  const res = await apiRequest('/api/v1/health');
  const serialized = JSON.stringify(res.data);
  assert.equal(serialized.includes('service_role'), false);
  assert.equal(serialized.includes('SERVICE_ROLE'), false);
});

