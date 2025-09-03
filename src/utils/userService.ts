import { eq, and, or, sql } from 'drizzle-orm';
import { db, users, auditLogs, type User, type NewUser } from '@/lib/db';
import { hashPassword, generateRandomToken } from '@/lib/auth';

export class UserService {
  static async createUser(userData: Omit<NewUser, 'id' | 'createdAt' | 'updatedAt'>): Promise<User> {
    const id = generateRandomToken();
    const hashedPassword = await hashPassword(userData.password);
    
    const [user] = await db.insert(users).values({
      ...userData,
      id,
      password: hashedPassword,
      verificationToken: generateRandomToken(),
    }).returning();
    
    await this.logAction(id, 'create', 'user', id, { email: userData.email });
    
    return user;
  }
  
  static async findByEmail(email: string): Promise<User | null> {
    const [user] = await db.select().from(users).where(eq(users.email, email)).limit(1);
    return user || null;
  }
  
  static async findByUsername(username: string): Promise<User | null> {
    const [user] = await db.select().from(users).where(eq(users.username, username)).limit(1);
    return user || null;
  }
  
  static async findById(id: string): Promise<User | null> {
    const [user] = await db.select().from(users).where(eq(users.id, id)).limit(1);
    return user || null;
  }
  
  static async findByEmailOrUsername(emailOrUsername: string): Promise<User | null> {
    const [user] = await db.select().from(users).where(
      or(eq(users.email, emailOrUsername), eq(users.username, emailOrUsername))
    ).limit(1);
    return user || null;
  }
  
  static async updateUser(id: string, updates: Partial<Omit<User, 'id' | 'createdAt'>>): Promise<User | null> {
    const [user] = await db.update(users).set({
      ...updates,
      updatedAt: Math.floor(Date.now() / 1000),
    }).where(eq(users.id, id)).returning();
    
    if (user) {
      await this.logAction(id, 'update', 'user', id, updates);
    }
    
    return user || null;
  }
  
  static async updatePassword(id: string, newPassword: string): Promise<boolean> {
    const hashedPassword = await hashPassword(newPassword);
    const result = await db.update(users).set({
      password: hashedPassword,
      updatedAt: Math.floor(Date.now() / 1000),
    }).where(eq(users.id, id));
    
    await this.logAction(id, 'update', 'user', id, { action: 'password_change' });
    
    return result.changes > 0;
  }
  
  static async updateLastLogin(id: string): Promise<void> {
    await db.update(users).set({
      lastLoginAt: Math.floor(Date.now() / 1000),
      updatedAt: Math.floor(Date.now() / 1000),
    }).where(eq(users.id, id));
    
    await this.logAction(id, 'login', 'user', id);
  }
  
  static async verifyUser(id: string): Promise<boolean> {
    const result = await db.update(users).set({
      isVerified: true,
      verificationToken: null,
      updatedAt: Math.floor(Date.now() / 1000),
    }).where(eq(users.id, id));
    
    if (result.changes > 0) {
      await this.logAction(id, 'verify', 'user', id);
    }
    
    return result.changes > 0;
  }
  
  static async setResetToken(email: string, token: string, expires: number): Promise<boolean> {
    const result = await db.update(users).set({
      resetPasswordToken: token,
      resetPasswordExpires: expires,
      updatedAt: Math.floor(Date.now() / 1000),
    }).where(eq(users.email, email));
    
    return result.changes > 0;
  }
  
  static async findByResetToken(token: string): Promise<User | null> {
    const [user] = await db.select().from(users).where(
      and(
        eq(users.resetPasswordToken, token),
        sql`${users.resetPasswordExpires} > ${Math.floor(Date.now() / 1000)}`
      )
    ).limit(1);
    
    return user || null;
  }
  
  static async clearResetToken(id: string): Promise<void> {
    await db.update(users).set({
      resetPasswordToken: null,
      resetPasswordExpires: null,
      updatedAt: Math.floor(Date.now() / 1000),
    }).where(eq(users.id, id));
  }
  
  static async deleteUser(id: string): Promise<boolean> {
    await this.logAction(id, 'delete', 'user', id);
    const result = await db.delete(users).where(eq(users.id, id));
    return result.changes > 0;
  }
  
  static async getAllUsers(page = 1, limit = 10, search = ''): Promise<{ users: User[], total: number }> {
    const offset = (page - 1) * limit;
    
    if (search) {
      const searchCondition = or(
        sql`${users.email} LIKE ${`%${search}%`}`,
        sql`${users.username} LIKE ${`%${search}%`}`,
        sql`${users.firstName} LIKE ${`%${search}%`}`,
        sql`${users.lastName} LIKE ${`%${search}%`}`
      );
      
      const [userResults, countResult] = await Promise.all([
        db.select().from(users).where(searchCondition).limit(limit).offset(offset),
        db.select({ count: sql<number>`count(*)` }).from(users).where(searchCondition)
      ]);
      
      return {
        users: userResults,
        total: countResult[0]?.count || 0
      };
    } else {
      const [userResults, countResult] = await Promise.all([
        db.select().from(users).limit(limit).offset(offset),
        db.select({ count: sql<number>`count(*)` }).from(users)
      ]);
      
      return {
        users: userResults,
        total: countResult[0]?.count || 0
      };
    }
  }
  
  private static async logAction(
    userId: string | null,
    action: string,
    resource: string,
    resourceId?: string,
    metadata?: any,
    ipAddress?: string,
    userAgent?: string
  ): Promise<void> {
    try {
      await db.insert(auditLogs).values({
        id: generateRandomToken(),
        userId,
        action,
        resource,
        resourceId,
        metadata: metadata ? JSON.stringify(metadata) : null,
        ipAddress,
        userAgent,
      });
    } catch (error) {
      console.error('Failed to log action:', error);
    }
  }
}