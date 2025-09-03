import type { APIRoute } from 'astro';
import { z } from 'zod';
import { UserService } from '@/utils/userService';
import { SessionService } from '@/utils/sessionService';
import { createApiError, createApiSuccess, formatValidationErrors, sanitizeUser } from '@/utils/api';
import { getAuthContext, requireAdmin } from '@/utils/auth';

const updateUserSchema = z.object({
  firstName: z.string().min(1, 'First name is required').optional(),
  lastName: z.string().min(1, 'Last name is required').optional(),
  username: z.string().min(3, 'Username must be at least 3 characters').optional(),
  email: z.string().email('Invalid email address').optional(),
  role: z.enum(['user', 'admin']).optional(),
  isActive: z.boolean().optional(),
  isVerified: z.boolean().optional(),
});

export const GET: APIRoute = async (context) => {
  try {
    const auth = await getAuthContext(context);
    requireAdmin(auth);

    const userId = context.params.id as string;
    const user = await UserService.findById(userId);

    if (!user) {
      return createApiError('User not found', 404);
    }

    return createApiSuccess({
      user: sanitizeUser(user),
    });

  } catch (error) {
    if (error instanceof Error) {
      if (error.message === 'Authentication required') {
        return createApiError('Authentication required', 401);
      }
      if (error.message === 'Admin access required') {
        return createApiError('Admin access required', 403);
      }
    }
    console.error('Get user error:', error);
    return createApiError('Internal server error', 500);
  }
};

export const PUT: APIRoute = async (context) => {
  try {
    const auth = await getAuthContext(context);
    const admin = requireAdmin(auth);

    const userId = context.params.id as string;
    
    // Prevent admin from modifying their own account through this endpoint
    if (userId === admin.id) {
      return createApiError('Cannot modify your own account through admin panel', 400);
    }

    // Parse and validate request body
    const body = await context.request.json();
    const result = updateUserSchema.safeParse(body);
    
    if (!result.success) {
      return createApiError(formatValidationErrors(result.error.errors));
    }

    const updates = result.data;

    // Check if user exists
    const existingUser = await UserService.findById(userId);
    if (!existingUser) {
      return createApiError('User not found', 404);
    }

    // Check for email/username conflicts if they're being updated
    if (updates.email && updates.email !== existingUser.email) {
      const emailConflict = await UserService.findByEmail(updates.email);
      if (emailConflict && emailConflict.id !== userId) {
        return createApiError('Email already in use', 409);
      }
    }

    if (updates.username && updates.username !== existingUser.username) {
      const usernameConflict = await UserService.findByUsername(updates.username);
      if (usernameConflict && usernameConflict.id !== userId) {
        return createApiError('Username already taken', 409);
      }
    }

    // Update user
    const updatedUser = await UserService.updateUser(userId, updates);
    if (!updatedUser) {
      return createApiError('Failed to update user', 500);
    }

    // If user was deactivated, revoke all their sessions
    if (updates.isActive === false) {
      await SessionService.revokeAllUserSessions(userId);
    }

    return createApiSuccess({
      user: sanitizeUser(updatedUser),
    }, 'User updated successfully');

  } catch (error) {
    if (error instanceof Error) {
      if (error.message === 'Authentication required') {
        return createApiError('Authentication required', 401);
      }
      if (error.message === 'Admin access required') {
        return createApiError('Admin access required', 403);
      }
    }
    console.error('Update user error:', error);
    return createApiError('Internal server error', 500);
  }
};

export const DELETE: APIRoute = async (context) => {
  try {
    const auth = await getAuthContext(context);
    const admin = requireAdmin(auth);

    const userId = context.params.id as string;
    
    // Prevent admin from deleting their own account
    if (userId === admin.id) {
      return createApiError('Cannot delete your own account', 400);
    }

    // Check if user exists
    const user = await UserService.findById(userId);
    if (!user) {
      return createApiError('User not found', 404);
    }

    // Delete user (this will cascade delete sessions via foreign key)
    const success = await UserService.deleteUser(userId);
    if (!success) {
      return createApiError('Failed to delete user', 500);
    }

    return createApiSuccess(null, 'User deleted successfully');

  } catch (error) {
    if (error instanceof Error) {
      if (error.message === 'Authentication required') {
        return createApiError('Authentication required', 401);
      }
      if (error.message === 'Admin access required') {
        return createApiError('Admin access required', 403);
      }
    }
    console.error('Delete user error:', error);
    return createApiError('Internal server error', 500);
  }
};