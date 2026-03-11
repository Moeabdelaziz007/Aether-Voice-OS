"use client";

import { useState, useEffect } from "react";
import {
    signInWithPopup,
    signOut,
    onAuthStateChanged,
    User,
    getIdToken
} from "firebase/auth";
import { auth, googleProvider } from "../lib/firebase";
import { useAetherStore } from "../store/useAetherStore";

export function useAuth() {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const addSystemLog = useAetherStore((s) => s.addSystemLog);

    useEffect(() => {
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
                    console.error("Token fetch failed", e);
                }
            } else {
                addSystemLog("[Auth] User signed out.");
            }
        });

        return () => unsubscribe();
    }, [addSystemLog]);

    const loginWithGoogle = async () => {
        try {
            const result = await signInWithPopup(auth, googleProvider);
            return result.user;
        } catch (error) {
            console.error("Login failed:", error);
            throw error;
        }
    };

    const logout = async () => {
        try {
            await signOut(auth);
        } catch (error) {
            console.error("Logout failed:", error);
        }
    };

    const getToken = async () => {
        if (!auth.currentUser) return null;
        return await getIdToken(auth.currentUser);
    };

    return { user, loading, loginWithGoogle, logout, getToken };
}
