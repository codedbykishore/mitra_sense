/**
 * User permission utilities for role-based access control
 */

export type UserRole = 'student' | 'institution' | 'facilitator' | 'admin';

export interface User {
  name: string;
  email: string;
  picture: string;
  plan: string;
  onboarding_completed: boolean;
  role: string | null;
  profile: Record<string, string>;
}

/**
 * Check if user has access to dashboard features
 * Currently includes all roles for development purposes
 */
export function canAccessDashboard(user: User | null | undefined): boolean {
  if (!user || !user.role) return false;
  
  // Allow dashboard access for all roles during development
  // In production, you might want to restrict this further
  return ['student', 'institution', 'facilitator', 'admin'].includes(user.role);
}

/**
 * Check if user can manage students (view student list, add moods, etc.)
 */
export function canManageStudents(user: User | null | undefined): boolean {
  if (!user || !user.role) return false;
  
  // Allow student management for facilitators, institutions, and admins
  // Students can also view for self-management purposes
  return ['student', 'institution', 'facilitator', 'admin'].includes(user.role);
}

/**
 * Check if user has admin privileges
 */
export function isAdmin(user: User | null | undefined): boolean {
  if (!user || !user.role) return false;
  return user.role === 'admin';
}

/**
 * Check if user is a facilitator or has facilitator-level permissions
 */
export function isFacilitator(user: User | null | undefined): boolean {
  if (!user || !user.role) return false;
  return ['facilitator', 'admin'].includes(user.role);
}

/**
 * Check if user represents an institution
 */
export function isInstitution(user: User | null | undefined): boolean {
  if (!user || !user.role) return false;
  return ['institution', 'admin'].includes(user.role);
}
