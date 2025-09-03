import type { APIRoute } from 'astro';
import { updateProfileSchema } from '@/lib/auth';
import { UserService } from '@/utils/userService';
import { createApiError, createApiSuccess, formatValidationErrors, sanitizeUser } from '@/utils/api';
import { getAuthContext, requireAuth } from '@/utils/auth';

export const GET: APIRoute = async (context) => {
  try {
    const auth = await getAuthContext(context);
    const user = requireAuth(auth);

    return createApiSuccess({
      user: sanitizeUser(user),
    });

  } catch (error) {
    if (error instanceof Error && error.message === 'Authentication required') {
      return createApiError('Authentication required', 401);
    }
    console.error('Get profile error:', error);
    return createApiError('Internal server error', 500);
  }
};

export const PUT: APIRoute = async (context) => {
  try {
    const auth = await getAuthContext(context);
    const user = requireAuth(auth);

    // Parse and validate request body
    const body = await context.request.json();
    const result = updateProfileSchema.safeParse(body);
    
    if (!result.success) {
      return createApiError(formatValidationErrors(result.error.errors));
    }

    const { firstName, lastName, username } = result.data;

    // Check if username is already taken by another user
    if (username !== user.username) {
      const existingUser = await UserService.findByUsername(username);
      if (existingUser && existingUser.id !== user.id) {
        return createApiError('Username already taken', 409);
      }
    }

    // Update user profile
    const updatedUser = await UserService.updateUser(user.id, {
      firstName,
      lastName,
      username,
    });

    if (!updatedUser) {
      return createApiError('Failed to update profile', 500);
    }

    return createApiSuccess({
      user: sanitizeUser(updatedUser),
    }, 'Profile updated successfully');

  } catch (error) {
    if (error instanceof Error && error.message === 'Authentication required') {
      return createApiError('Authentication required', 401);
    }
    console.error('Update profile error:', error);
    return createApiError('Internal server error', 500);
  }
};