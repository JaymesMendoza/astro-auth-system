import { eq, and, sql } from 'drizzle-orm';
import { db, sessions, type Session } from '@/lib/db';
import { generateRandomToken, generateAccessToken, generateRefreshToken, type JWTPayload } from '@/lib/auth';

export class SessionService {
  static async createSession(
    userId: string,
    userEmail: string,
    userRole: string,
    rememberMe = false,
    userAgent?: string,
    ipAddress?: string
  ): Promise<{ accessToken: string; refreshToken: string; session: Session }> {
    const payload: JWTPayload = { userId, email: userEmail, role: userRole };
    const accessToken = generateAccessToken(payload);
    const refreshToken = generateRefreshToken(payload);
    
    const now = Math.floor(Date.now() / 1000);
    const accessExpires = now + (15 * 60); // 15 minutes
    const refreshExpires = rememberMe 
      ? now + (30 * 24 * 60 * 60) // 30 days if remember me
      : now + (7 * 24 * 60 * 60); // 7 days default
    
    const [session] = await db.insert(sessions).values({
      id: generateRandomToken(),
      userId,
      token: accessToken,
      refreshToken,
      expiresAt: accessExpires,
      refreshExpiresAt: refreshExpires,
      userAgent,
      ipAddress,
    }).returning();
    
    return { accessToken, refreshToken, session };
  }
  
  static async findByToken(token: string): Promise<Session | null> {
    const [session] = await db.select().from(sessions).where(
      and(
        eq(sessions.token, token),
        eq(sessions.isActive, true),
        sql`${sessions.expiresAt} > ${Math.floor(Date.now() / 1000)}`
      )
    ).limit(1);
    
    return session || null;
  }
  
  static async findByRefreshToken(refreshToken: string): Promise<Session | null> {
    const [session] = await db.select().from(sessions).where(
      and(
        eq(sessions.refreshToken, refreshToken),
        eq(sessions.isActive, true),
        sql`${sessions.refreshExpiresAt} > ${Math.floor(Date.now() / 1000)}`
      )
    ).limit(1);
    
    return session || null;
  }
  
  static async refreshSession(
    refreshToken: string,
    userEmail: string,
    userRole: string
  ): Promise<{ accessToken: string; refreshToken: string } | null> {
    const session = await this.findByRefreshToken(refreshToken);
    if (!session) return null;
    
    const payload: JWTPayload = { userId: session.userId, email: userEmail, role: userRole };
    const newAccessToken = generateAccessToken(payload);
    const newRefreshToken = generateRefreshToken(payload);
    
    const now = Math.floor(Date.now() / 1000);
    const accessExpires = now + (15 * 60); // 15 minutes
    const refreshExpires = now + (7 * 24 * 60 * 60); // 7 days
    
    await db.update(sessions).set({
      token: newAccessToken,
      refreshToken: newRefreshToken,
      expiresAt: accessExpires,
      refreshExpiresAt: refreshExpires,
      updatedAt: now,
    }).where(eq(sessions.id, session.id));
    
    return { accessToken: newAccessToken, refreshToken: newRefreshToken };
  }
  
  static async revokeSession(token: string): Promise<boolean> {
    const result = await db.update(sessions).set({
      isActive: false,
      updatedAt: Math.floor(Date.now() / 1000),
    }).where(eq(sessions.token, token));
    
    return result.changes > 0;
  }
  
  static async revokeAllUserSessions(userId: string): Promise<void> {
    await db.update(sessions).set({
      isActive: false,
      updatedAt: Math.floor(Date.now() / 1000),
    }).where(eq(sessions.userId, userId));
  }
  
  static async cleanupExpiredSessions(): Promise<void> {
    const now = Math.floor(Date.now() / 1000);
    await db.delete(sessions).where(
      sql`${sessions.refreshExpiresAt} < ${now}`
    );
  }
  
  static async getUserSessions(userId: string): Promise<Session[]> {
    return db.select().from(sessions).where(
      and(
        eq(sessions.userId, userId),
        eq(sessions.isActive, true)
      )
    );
  }
}