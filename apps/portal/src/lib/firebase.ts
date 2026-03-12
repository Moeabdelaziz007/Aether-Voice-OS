import { initializeApp, getApps, getApp, FirebaseApp } from "firebase/app";
import { getAuth, GoogleAuthProvider, Auth } from "firebase/auth";
import { getFirestore, Firestore } from "firebase/firestore";

// Check if running on server or client
const isClient = typeof window !== 'undefined';

// Validate that all required Firebase config variables are present
const validateFirebaseConfig = () => {
    const requiredVars = [
        'NEXT_PUBLIC_FIREBASE_API_KEY',
        'NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN',
        'NEXT_PUBLIC_FIREBASE_PROJECT_ID',
        'NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET',
        'NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID',
        'NEXT_PUBLIC_FIREBASE_APP_ID',
    ];

    const missingVars = requiredVars.filter(
        (varName) => !process.env[varName]
    );

    if (missingVars.length > 0) {
        console.warn(
            `[Firebase] Missing environment variables: ${missingVars.join(', ')}\n` +
            'Please add these to your .env.local file or Vercel environment variables.\n' +
            'Create .env.local with Firebase configuration from your Firebase Console project settings.'
        );
        return null;
    }

    return {
        apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || '',
        authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || '',
        projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || '',
        storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || '',
        messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || '',
        appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID || '',
    };
};

const firebaseConfig = validateFirebaseConfig();

// Initialize Firebase with error handling - only on client side
let auth: Auth | null = null;
let db: Firestore | null = null;
let googleProvider: GoogleAuthProvider | null = null;
let app: FirebaseApp | null = null;

if (isClient && firebaseConfig) {
    try {
        // Check if we have valid config
        if (!firebaseConfig.apiKey || !firebaseConfig.projectId) {
            throw new Error(
                'Firebase configuration is incomplete. Please set environment variables in Vercel project settings or .env.local'
            );
        }

        app = getApps().length > 0 ? getApp() : initializeApp(firebaseConfig);
        auth = getAuth(app);
        db = getFirestore(app);
        googleProvider = new GoogleAuthProvider();

        console.log('[Firebase] Initialized successfully');
    } catch (error) {
        console.error('[Firebase] Initialization failed:', error);
        // Firebase will be unavailable but the app won't crash
        auth = null;
        db = null;
        googleProvider = null;
    }
} else if (!isClient) {
    console.debug('[Firebase] Running on server - Firebase initialization skipped');
}

export {
    auth,
    db,
    googleProvider,
    firebaseConfig,
    app,
    isClient,
};
