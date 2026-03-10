import "fake-indexeddb/auto";
import { StateStorage } from 'zustand/middleware';
import { get, set, del } from 'idb-keyval';

/**
 * Custom storage engine for Zustand using IndexedDB (via idb-keyval).
 * Why?
 * 1. Security: IndexedDB is not directly accessible via simple console like localStorage.
 * 2. Capacity: localStorage is limited to ~5MB. IndexedDB can store gigabytes.
 * 3. Performance: Async by nature, prevents blocking the main thread during heavy state persistence.
 */
export const idbStorage: any = {
    getItem: async (name: string): Promise<string | null> => {
        return (await get(name)) || null;
    },
    setItem: async (name: string, value: string): Promise<void> => {
        await set(name, value);
    },
    removeItem: async (name: string): Promise<void> => {
        await del(name);
    },
};
