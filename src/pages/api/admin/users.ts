import type { APIRoute } from 'astro';
import { UserService } from '@/utils/userService';
import { createApiError, createApiSuccess, sanitizeUser, generatePagination } from '@/utils/api';
import { getAuthContext, requireAdmin } from '@/utils/auth';

export const GET: APIRoute = async (context) => {
  try {
    const auth = await getAuthContext(context);
    requireAdmin(auth);

    const url = new URL(context.request.url);
    const page = parseInt(url.searchParams.get('page') || '1');
    const limit = parseInt(url.searchParams.get('limit') || '10');
    const search = url.searchParams.get('search') || '';

    const { users, total } = await UserService.getAllUsers(page, limit, search);

    return createApiSuccess({
      users: users.map(sanitizeUser),
      pagination: generatePagination(page, limit, total),
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
    console.error('Get users error:', error);
    return createApiError('Internal server error', 500);
  }
};