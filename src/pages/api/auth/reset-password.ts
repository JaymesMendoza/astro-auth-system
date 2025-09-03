import type { APIRoute } from 'astro';
import { resetPasswordSchema } from '@/lib/auth';
import { UserService } from '@/utils/userService';
import { SessionService } from '@/utils/sessionService';
import { createApiError, createApiSuccess, formatValidationErrors } from '@/utils/api';

export const POST: APIRoute = async ({ request }) => {
  try {
    // Parse and validate request body
    const body = await request.json();
    const result = resetPasswordSchema.safeParse(body);
    
    if (!result.success) {
      return createApiError(formatValidationErrors(result.error.errors));
    }

    const { token, password } = result.data;

    // Find user by reset token
    const user = await UserService.findByResetToken(token);
    if (!user) {
      return createApiError('Invalid or expired reset token', 400);
    }

    // Update password
    await UserService.updatePassword(user.id, password);

    // Clear reset token
    await UserService.clearResetToken(user.id);

    // Revoke all existing sessions for security
    await SessionService.revokeAllUserSessions(user.id);

    return createApiSuccess(
      null, 
      'Password reset successfully. Please log in with your new password.'
    );

  } catch (error) {
    console.error('Reset password error:', error);
    return createApiError('Internal server error', 500);
  }
};