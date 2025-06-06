import { compare } from 'bcrypt-ts';
import NextAuth, { type DefaultSession } from 'next-auth';
import Credentials from 'next-auth/providers/credentials';
import { createGuestUser, getUser } from '@/lib/db/queries';
import { authConfig } from './auth.config';
import { DUMMY_PASSWORD } from '@/lib/constants';
import type { DefaultJWT } from 'next-auth/jwt';

export type UserType = 'guest' | 'regular';

declare module 'next-auth' {
  interface Session extends DefaultSession {
    user: {
      id: string;
      type: UserType;
    } & DefaultSession['user'];
  }

  interface User {
    id?: string;
    email?: string | null;
    type: UserType;
  }
}

declare module 'next-auth/jwt' {
  interface JWT extends DefaultJWT {
    id: string;
    type: UserType;
  }
}

export const {
  handlers: { GET, POST },
  auth,
  signIn,
  signOut,
} = NextAuth({
  ...authConfig,
  providers: [
    Credentials({
      credentials: {},
      async authorize({ email, password }: any) {
        const users = await getUser(email);

        if (users.length === 0) {
          await compare(password, DUMMY_PASSWORD);
          return null;
        }

        const [user] = users;

        if (!user.password) {
          await compare(password, DUMMY_PASSWORD);
          return null;
        }

        const passwordsMatch = await compare(password, user.password);

        if (!passwordsMatch) return null;

        return { ...user, type: 'regular' };
      },
    }),
    Credentials({
      id: 'guest',
      credentials: {},
      async authorize() {
        const guestUser = await createGuestUser();
        if (!guestUser) {
          return null; // Or throw an error if guest creation is mandatory
        }
        // Ensure guestUser has an id, as the User type in next-auth expects it.
        // The createGuestUser now returns the user object which should include the id.
        return { ...guestUser, id: guestUser.id!, type: 'guest' };
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        // This block only runs on sign-in or when user object is explicitly passed.
        token.id = user.id as string;
        token.type = user.type;
        // Persist other user fields to token if needed, e.g., token.email = user.email;
      }
      console.log('[auth.ts] JWT callback, user:', JSON.stringify(user, null, 2));
      console.log('[auth.ts] JWT callback, resulting token:', JSON.stringify(token, null, 2));
      return token;
    },
    async session({ session, token }) {
      console.log('[auth.ts] Session callback ENTRY, initial session:', JSON.stringify(session, null, 2));
      console.log('[auth.ts] Session callback ENTRY, token from JWT callback:', JSON.stringify(token, null, 2));

      // Ensure session.user exists before trying to assign to its properties
      if (!session.user) {
        // @ts-expect-error - creating user object if it doesn't exist, type will be extended by assignments
        session.user = {}; 
      }

      if (token.id && token.type) {
        session.user.id = token.id as string;
        session.user.type = token.type as UserType;
        // If you stored other user details in the token (like email, name), assign them here too:
        // session.user.email = token.email as string; 
        // session.user.name = token.name as string;
      } else {
        console.log('[auth.ts] Session callback: Token did not contain id or type. Session user might be incomplete or unauthenticated.');
        // If token is empty or lacks critical fields, NextAuth might return a default unauthenticated session.
        // Or, you might want to explicitly clear session.user or parts of it if token is invalid.
        // For now, just logging. The structure of `session` itself (e.g. if it's null) is determined by NextAuth internals based on token validity.
      }

      console.log('[auth.ts] Session callback EXIT, final session object to be returned:', JSON.stringify(session, null, 2));
      return session;
    },
  },
});
