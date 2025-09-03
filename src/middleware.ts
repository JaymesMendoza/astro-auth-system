import { defineMiddleware } from 'astro:middleware';
import { getAuthContext } from '@/utils/auth';

export const onRequest = defineMiddleware(async (context, next) => {
  const pathname = context.url.pathname;

  // Skip middleware for public routes
  if (
    pathname === '/' ||
    pathname.startsWith('/api/auth/') ||
    pathname.startsWith('/auth/') ||
    pathname.startsWith('/_astro/') ||
    pathname.includes('.') // Static files
  ) {
    return next();
  }

  // Get authentication context
  const auth = await getAuthContext(context);

  // Protect dashboard routes
  if (pathname.startsWith('/dashboard') || pathname.startsWith('/profile')) {
    if (!auth.isAuthenticated) {
      return context.redirect('/auth/login');
    }
  }

  // Protect admin routes
  if (pathname.startsWith('/admin')) {
    if (!auth.isAuthenticated) {
      return context.redirect('/auth/login');
    }
    if (!auth.isAdmin) {
      return context.redirect('/dashboard');
    }
  }

  // Protect API routes
  if (pathname.startsWith('/api/')) {
    // User routes require authentication
    if (pathname.startsWith('/api/user/')) {
      if (!auth.isAuthenticated) {
        return new Response(JSON.stringify({
          success: false,
          error: 'Authentication required'
        }), {
          status: 401,
          headers: { 'Content-Type': 'application/json' }
        });
      }
    }

    // Admin routes require admin role
    if (pathname.startsWith('/api/admin/')) {
      if (!auth.isAuthenticated) {
        return new Response(JSON.stringify({
          success: false,
          error: 'Authentication required'
        }), {
          status: 401,
          headers: { 'Content-Type': 'application/json' }
        });
      }
      if (!auth.isAdmin) {
        return new Response(JSON.stringify({
          success: false,
          error: 'Admin access required'
        }), {
          status: 403,
          headers: { 'Content-Type': 'application/json' }
        });
      }
    }
  }

  // Add auth context to locals for use in pages
  context.locals.auth = auth;

  return next();
});