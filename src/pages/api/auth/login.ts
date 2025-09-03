import type { APIRoute } from 'astro';
import { loginSchema, verifyPassword } from '@/lib/auth';
import { UserService } from '@/utils/userService';
import { SessionService } from '@/utils/sessionService';
import { createApiError, createApiSuccess, formatValidationErrors, sanitizeUser } from '@/utils/api';
import { setAuthCookies, getClientIP, getUserAgent } from '@/utils/auth';
import { loginRateLimiter } from '@/utils/rateLimiter';

export const POST: APIRoute = async ({ request, cookies }) => {
  try {
    // Rate limiting
    const clientIP = getClientIP(request);
    const rateLimitResult = loginRateLimiter.check(clientIP);
    
    if (!rateLimitResult.allowed) {
      return createApiError(
        `Too many login attempts. Try again in ${Math.ceil((rateLimitResult.resetTime - Date.now()) / 60000)} minutes.`,
        429
      );
    }

    // Parse and validate request body
    const body = await request.json();
    const result = loginSchema.safeParse(body);
    
    if (!result.success) {
      return createApiError(formatValidationErrors(result.error.errors));
    }

    const { email, password, rememberMe } = result.data;

    // Find user by email or username
    const user = await UserService.findByEmailOrUsername(email);
    if (!user) {
      return createApiError('Invalid credentials', 401);
    }

    // Verify password
    const isPasswordValid = await verifyPassword(password, user.password);
    if (!isPasswordValid) {
      return createApiError('Invalid credentials', 401);
    }

    // Check if user is active
    if (!user.isActive) {
      return createApiError('Account is deactivated', 401);
    }

    // Update last login
    await UserService.updateLastLogin(user.id);

    // Create session
    const userAgent = getUserAgent(request);
    const { accessToken, refreshToken } = await SessionService.createSession(
      user.id,
      user.email,
      user.role,
      rememberMe,
      userAgent,
      clientIP
    );

    // Set HTTP-only cookies
    setAuthCookies({ cookies } as any, accessToken, refreshToken, rememberMe);

    return createApiSuccess({
      user: sanitizeUser(user),
      accessToken,
      refreshToken,
    }, 'Login successful');

  } catch (error) {
    console.error('Login error:', error);
    return createApiError('Internal server error', 500);
  }
};