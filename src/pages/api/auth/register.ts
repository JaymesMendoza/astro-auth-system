import type { APIRoute } from 'astro';
import { registerSchema } from '@/lib/auth';
import { UserService } from '@/utils/userService';
import { createApiError, createApiSuccess, formatValidationErrors, sanitizeUser } from '@/utils/api';
import { getClientIP } from '@/utils/auth';
import { apiRateLimiter } from '@/utils/rateLimiter';

export const POST: APIRoute = async ({ request }) => {
  try {
    // Rate limiting
    const clientIP = getClientIP(request);
    const rateLimitResult = apiRateLimiter.check(clientIP);
    
    if (!rateLimitResult.allowed) {
      return createApiError('Too many requests. Please try again later.', 429);
    }

    // Parse and validate request body
    const body = await request.json();
    const result = registerSchema.safeParse(body);
    
    if (!result.success) {
      return createApiError(formatValidationErrors(result.error.errors));
    }

    const { email, username, password, firstName, lastName } = result.data;

    // Check if user already exists
    const [existingUserByEmail, existingUserByUsername] = await Promise.all([
      UserService.findByEmail(email),
      UserService.findByUsername(username),
    ]);

    if (existingUserByEmail) {
      return createApiError('Email already registered', 409);
    }

    if (existingUserByUsername) {
      return createApiError('Username already taken', 409);
    }

    // Create user
    const user = await UserService.createUser({
      email,
      username,
      password,
      firstName,
      lastName,
      role: 'user',
      isVerified: false, // In a real app, you'd send verification email
      isActive: true,
    });

    // TODO: Send verification email here
    // await EmailService.sendVerificationEmail(user.email, user.verificationToken);

    return createApiSuccess({
      user: sanitizeUser(user),
    }, 'Registration successful. Please check your email for verification instructions.', 201);

  } catch (error) {
    console.error('Registration error:', error);
    return createApiError('Internal server error', 500);
  }
};