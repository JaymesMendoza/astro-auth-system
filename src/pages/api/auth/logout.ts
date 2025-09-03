import type { APIRoute } from 'astro';
import { SessionService } from '@/utils/sessionService';
import { createApiSuccess, createApiError } from '@/utils/api';
import { clearAuthCookies, getAuthContext } from '@/utils/auth';

export const POST: APIRoute = async (context) => {
  try {
    const auth = await getAuthContext(context);
    
    if (auth.isAuthenticated && auth.session) {
      // Revoke the current session
      await SessionService.revokeSession(auth.session.token);
    }

    // Clear auth cookies
    clearAuthCookies(context);

    return createApiSuccess(null, 'Logout successful');

  } catch (error) {
    console.error('Logout error:', error);
    return createApiError('Internal server error', 500);
  }
};