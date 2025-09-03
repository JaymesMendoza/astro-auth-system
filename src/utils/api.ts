import type { ApiResponse } from '@/types';

export function createApiResponse<T>(data: T, message?: string): ApiResponse<T> {
  return {
    success: true,
    data,
    message,
  };
}

export function createApiError(error: string, statusCode = 400): Response {
  return new Response(JSON.stringify({
    success: false,
    error,
  }), {
    status: statusCode,
    headers: {
      'Content-Type': 'application/json',
    },
  });
}

export function createApiSuccess<T>(data: T, message?: string, statusCode = 200): Response {
  return new Response(JSON.stringify(createApiResponse(data, message)), {
    status: statusCode,
    headers: {
      'Content-Type': 'application/json',
    },
  });
}

export function formatValidationErrors(errors: any[]): string {
  return errors.map(err => err.message).join(', ');
}

export function sanitizeUser(user: any) {
  const { password, verificationToken, resetPasswordToken, resetPasswordExpires, ...sanitized } = user;
  return sanitized;
}

export function generatePagination(page: number, limit: number, total: number) {
  const totalPages = Math.ceil(total / limit);
  return {
    page,
    limit,
    total,
    totalPages,
    hasNext: page < totalPages,
    hasPrev: page > 1,
  };
}