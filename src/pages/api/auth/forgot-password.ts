import type { APIRoute } from 'astro';
import { forgotPasswordSchema, generateResetToken } from '@/lib/auth';
import { UserService } from '@/utils/userService';
import { createApiError, createApiSuccess, formatValidationErrors } from '@/utils/api';
import { passwordResetRateLimiter } from '@/utils/rateLimiter';
import { getClientIP } from '@/utils/auth';

export const POST: APIRoute = async ({ request }) => {
  try {
    // Rate limiting
    const clientIP = getClientIP(request);
    const rateLimitResult = passwordResetRateLimiter.check(clientIP);
    
    if (!rateLimitResult.allowed) {
      return createApiError(
        'Too many password reset attempts. Please try again later.',
        429
      );
    }

    // Parse and validate request body
    const body = await request.json();
    const result = forgotPasswordSchema.safeParse(body);
    
    if (!result.success) {
      return createApiError(formatValidationErrors(result.error.errors));
    }

    const { email } = result.data;

    // Find user by email
    const user = await UserService.findByEmail(email);
    
    // Always return success to prevent email enumeration
    if (!user) {
      return createApiSuccess(
        null, 
        'If an account with that email exists, we\'ve sent a password reset link.'
      );
    }

    // Generate reset token
    const resetToken = generateResetToken();
    const expires = Math.floor(Date.now() / 1000) + (60 * 60); // 1 hour from now

    // Save reset token
    await UserService.setResetToken(email, resetToken, expires);

    // TODO: Send password reset email
    // await EmailService.sendPasswordResetEmail(email, resetToken);

    return createApiSuccess(
      null, 
      'If an account with that email exists, we\'ve sent a password reset link.'
    );

  } catch (error) {
    console.error('Forgot password error:', error);
    return createApiError('Internal server error', 500);
  }
};