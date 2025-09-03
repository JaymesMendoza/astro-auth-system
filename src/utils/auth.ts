import type { APIContext } from 'astro';
import type { AuthContext, User } from '@/types';
import { verifyAccessToken } from '@/lib/auth';
import { UserService } from '@/utils/userService';
import { SessionService } from '@/utils/sessionService';

export async function getAuthContext(context: APIContext): Promise<AuthContext> {
  const authHeader = context.request.headers.get('authorization');
  const cookieToken = context.cookies.get('access_token')?.value;
  
  const token = authHeader?.replace('Bearer ', '') || cookieToken;
  
  if (!token) {
    return { user: null, session: null, isAuthenticated: false, isAdmin: false };
  }
  
  try {
    const payload = verifyAccessToken(token);
    if (!payload) {
      return { user: null, session: null, isAuthenticated: false, isAdmin: false };
    }
    
    const [user, session] = await Promise.all([
      UserService.findById(payload.userId),
      SessionService.findByToken(token)
    ]);
    
    if (!user || !session || !user.isActive) {
      return { user: null, session: null, isAuthenticated: false, isAdmin: false };
    }
    
    return {
      user,
      session,
      isAuthenticated: true,
      isAdmin: user.role === 'admin'
    };
  } catch (error) {
    console.error('Auth context error:', error);
    return { user: null, session: null, isAuthenticated: false, isAdmin: false };
  }
}

export function requireAuth(auth: AuthContext): User {
  if (!auth.isAuthenticated || !auth.user) {
    throw new Error('Authentication required');
  }
  return auth.user;
}

export function requireAdmin(auth: AuthContext): User {
  const user = requireAuth(auth);
  if (!auth.isAdmin) {
    throw new Error('Admin access required');
  }
  return user;
}

export function setAuthCookies(
  context: APIContext, 
  accessToken: string, 
  refreshToken: string,
  rememberMe = false
): void {
  const cookieOptions = {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax' as const,
    path: '/',
  };
  
  // Access token - short lived
  context.cookies.set('access_token', accessToken, {
    ...cookieOptions,
    maxAge: 15 * 60, // 15 minutes
  });
  
  // Refresh token - longer lived
  context.cookies.set('refresh_token', refreshToken, {
    ...cookieOptions,
    maxAge: rememberMe ? 30 * 24 * 60 * 60 : 7 * 24 * 60 * 60, // 30 days or 7 days
  });
}

export function clearAuthCookies(context: APIContext): void {
  context.cookies.delete('access_token', { path: '/' });
  context.cookies.delete('refresh_token', { path: '/' });
}

export function getClientIP(request: Request): string {
  return request.headers.get('x-forwarded-for')?.split(',')[0] || 
         request.headers.get('x-real-ip') || 
         'unknown';
}

export function getUserAgent(request: Request): string {
  return request.headers.get('user-agent') || 'unknown';
}