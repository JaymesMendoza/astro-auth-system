import type { APIRoute } from 'astro';
import { SessionService } from '@/utils/sessionService';
import { UserService } from '@/utils/userService';
import { createApiSuccess, createApiError, sanitizeUser } from '@/utils/api';
import { setAuthCookies } from '@/utils/auth';

export const POST: APIRoute = async ({ cookies }) => {
  try {
    const refreshToken = cookies.get('refresh_token')?.value;
    
    if (!refreshToken) {
      return createApiError('Refresh token not found', 401);
    }

    // Find session by refresh token
    const session = await SessionService.findByRefreshToken(refreshToken);
    if (!session) {
      return createApiError('Invalid refresh token', 401);
    }

    // Get user details
    const user = await UserService.findById(session.userId);
    if (!user || !user.isActive) {
      return createApiError('User not found or inactive', 401);
    }

    // Refresh the session
    const tokens = await SessionService.refreshSession(
      refreshToken,
      user.email,
      user.role
    );

    if (!tokens) {
      return createApiError('Failed to refresh session', 401);
    }

    // Set new cookies
    setAuthCookies({ cookies } as any, tokens.accessToken, tokens.refreshToken);

    return createApiSuccess({
      user: sanitizeUser(user),
      accessToken: tokens.accessToken,
      refreshToken: tokens.refreshToken,
    }, 'Token refreshed successfully');

  } catch (error) {
    console.error('Refresh token error:', error);
    return createApiError('Internal server error', 500);
  }
};