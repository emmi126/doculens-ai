import type { NextRequest } from 'next/server';
import { NextResponse } from 'next/server';

// Protected routes that require authentication
const protectedRoutes = ['/dashboard', '/course', '/document', '/trash'];

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Check if Auth0 is configured
  const auth0Domain = process.env.AUTH0_DOMAIN;
  const auth0ClientId = process.env.AUTH0_CLIENT_ID;
  const auth0Secret = process.env.AUTH0_SECRET;

  // If Auth0 is not configured, allow all routes (dev mode)
  if (!auth0Domain || !auth0ClientId || !auth0Secret) {
    return NextResponse.next();
  }

  // For Auth0 auth routes, use the auth0 middleware
  if (pathname.startsWith('/auth/')) {
    // Dynamic import to avoid issues when Auth0 is not configured
    const { auth0 } = await import('./lib/auth0');
    return auth0.middleware(request);
  }

  // Check if the route is protected
  const isProtectedRoute = protectedRoutes.some(route =>
    pathname.startsWith(route)
  );

  if (isProtectedRoute) {
    // Dynamic import to avoid issues when Auth0 is not configured
    const { auth0 } = await import('./lib/auth0');

    // Get session to check if user is authenticated
    const session = await auth0.getSession();

    if (!session) {
      // Redirect to login
      const loginUrl = new URL('/auth/login', request.url);
      loginUrl.searchParams.set('returnTo', pathname);
      return NextResponse.redirect(loginUrl);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico, sitemap.xml, robots.txt (metadata files)
     */
    '/((?!_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt).*)',
  ],
};
