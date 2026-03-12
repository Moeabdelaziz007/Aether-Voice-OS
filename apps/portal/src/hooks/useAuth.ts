"use client";

import { useState, useEffect } from "react";
import {
    signInWithPopup,
    signOut,
    onAuthStateChanged,
    User,
    getIdToken,
} from "firebase/auth";
import type { Auth } from "firebase/auth";
import { auth, googleProvider, isClient } from "../lib/firebase";
import { useAetherStore } from "../store/useAetherStore";

// Mock user for development/fallback
const MOCK_USER: User = {
    uid: 'dev-user-001',
    email: 'dev@example.com',
    displayName: 'Development User',
    photoURL: null,
    emailVerified: true,
    isAnonymous: false,
    metadata: {
        creationTime: new Date().toISOString(),
        lastSignInTime: new Date().toISOString(),
    },
    providerData: [],
    getIdToken: async () => 'mock-token',
    getIdTokenResult: async () => ({
        token: 'mock-token',
        expirationTime: new Date(Date.now() + 3600000).toISOString(),
        authTime: new Date().toISOString(),
        issuedAtTime: new Date().toISOString(),
        signInProvider: 'custom',
        signInSecondFactor: null,
        claims: {},
    }),
    reload: async () => {},
    getDisplayName: () => 'Development User',
    delete: async () => {},
    toJSON: () => ({}),
} as any;

export function useAuth() {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const [firebaseReady, setFirebaseReady] = useState(!!auth && isClient);
    const addSystemLog = useAetherStore((s) => s.addSystemLog);

    useEffect(() => {
        // Client-side only initialization
        if (!isClient) {
            console.debug('[useAuth] Running on server - skipping Firebase initialization.');
            return;
        }

        // If Firebase is not initialized, use mock user for development
        if (!auth) {
            console.warn('[useAuth] Firebase not initialized. Using development mode with mock user.');
            addSystemLog('[Auth] Firebase not configured. Using development mode.');
            setUser(MOCK_USER);
            setLoading(false);
            setFirebaseReady(false);
            return;
        }

        // We only want to set up this listener once
        const unsubscribe = onAuthStateChanged(auth, async (currentUser) => {
            setUser(currentUser);
            setLoading(false);

            if (currentUser) {
                addSystemLog(`[Auth] User synchronized: ${currentUser.displayName}`);
                // Pre-fetch token to ensure it's ready for the gateway
                try {
                    await getIdToken(currentUser);
                } catch (e) {
                    console.error("[v0] Token fetch failed", e);
                }
            } else {
                addSystemLog("[Auth] User signed out.");
            }
        });

        return () => unsubscribe();
    }, [addSystemLog]);

    const loginWithGoogle = async () => {
        if (!auth || !googleProvider) {
            console.warn('[useAuth] Firebase not available. Returning mock user.');
            addSystemLog('[Auth] Firebase not available. Logged in with mock user.');
            setUser(MOCK_USER);
            return MOCK_USER;
        }

        try {
            const result = await signInWithPopup(auth, googleProvider);
            addSystemLog(`[Auth] Successfully logged in: ${result.user.displayName}`);
            return result.user;
        } catch (error) {
            console.error("[v0] Login failed:", error);
            // Fallback to mock user on Firebase error
            if ((error as any)?.code === 'auth/invalid-api-key' || (error as any)?.code === 'auth/operation-not-allowed') {
                console.warn('[useAuth] Firebase authentication unavailable. Using mock user for development.');
                addSystemLog('[Auth] Using development/mock authentication.');
                setUser(MOCK_USER);
                return MOCK_USER;
            }
            throw error;
        }
    };

    const logout = async () => {
        if (!auth) {
            setUser(null);
            addSystemLog('[Auth] Logged out (mock).');
            return;
        }

        try {
            await signOut(auth);
            addSystemLog('[Auth] Successfully logged out.');
        } catch (error) {
            console.error("[v0] Logout failed:", error);
        }
    };

    const getToken = async () => {
        if (!user) return null;
        if (!auth || !firebaseReady) {
            // Return a mock token for development
            return 'mock-jwt-token-' + Date.now();
        }
        try {
            return await getIdToken(user);
        } catch (error) {
            console.error("[v0] Token retrieval failed:", error);
            return 'mock-jwt-token-' + Date.now();
        }
    };

    return { user, loading, loginWithGoogle, logout, getToken, firebaseReady };
}
