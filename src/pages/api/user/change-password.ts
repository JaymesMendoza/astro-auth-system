import type { APIRoute } from 'astro';
import { changePasswordSchema, verifyPassword } from '@/lib/auth';
import { UserService } from '@/utils/userService';
import { SessionService } from '@/utils/sessionService';
import { createApiError, createApiSuccess, formatValidationErrors } from '@/utils/api';
import { getAuthContext, requireAuth } from '@/utils/auth';

export const PUT: APIRoute = async (context) => {
  try {
    const auth = await getAuthContext(context);
    const user = requireAuth(auth);

    // Parse and validate request body
    const body = await context.request.json();
    const result = changePasswordSchema.safeParse(body);
    
    if (!result.success) {
      return createApiError(formatValidationErrors(result.error.errors));
    }

    const { currentPassword, newPassword } = result.data;

    // Get user with password to verify current password
    const userWithPassword = await UserService.findById(user.id);
    if (!userWithPassword) {
      return createApiError('User not found', 404);
    }

    // Verify current password
    const isCurrentPasswordValid = await verifyPassword(currentPassword, userWithPassword.password);
    if (!isCurrentPasswordValid) {
      return createApiError('Current password is incorrect', 400);
    }

    // Update password
    const success = await UserService.updatePassword(user.id, newPassword);
    if (!success) {
      return createApiError('Failed to update password', 500);
    }

    // Revoke all other sessions for security (keep current session)
    const sessions = await SessionService.getUserSessions(user.id);
    const currentSessionId = auth.session?.id;
    
    for (const session of sessions) {
      if (session.id !== currentSessionId) {
        await SessionService.revokeSession(session.token);
      }
    }

    return createApiSuccess(
      null, 
      'Password changed successfully. Other devices have been logged out for security.'
    );

  } catch (error) {
    if (error instanceof Error && error.message === 'Authentication required') {
      return createApiError('Authentication required', 401);
    }
    console.error('Change password error:', error);
    return createApiError('Internal server error', 500);
  }
};