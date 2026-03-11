'use client';

import { useAetherStore } from '@/store/useAetherStore';

const tokenize = (text: string): string[] =>
    (text.toLowerCase().match(/[a-z0-9]+/g) || []).filter((token) => token.length > 1);

const scoreSemantic = (query: string, content: string): number => {
    const queryTokens = tokenize(query);
    const contentTokens = tokenize(content);
    if (queryTokens.length === 0 || contentTokens.length === 0) return 0;
    const contentSet = new Set(contentTokens);
    const overlap = queryTokens.filter((token) => contentSet.has(token)).length;
    const phraseBoost = content.toLowerCase().includes(query.toLowerCase()) ? 0.25 : 0;
    return Math.min(1, overlap / queryTokens.length + phraseBoost);
};

export async function recallNotesSemantic(query: string, limit: number = 5) {
    const normalized = query.trim();
    if (!normalized) {
        return {
            status: 'error' as const,
            query,
            count: 0,
            notes: [],
            message: 'query_required',
        };
    }

    const notes = useAetherStore.getState().notesPlanet;
    const ranked = notes
        .map((note) => ({
            ...note,
            score: scoreSemantic(normalized, note.content),
        }))
        .filter((note) => note.score >= 0.15)
        .sort((a, b) => b.score - a.score || b.updatedAt - a.updatedAt)
        .slice(0, Math.max(1, limit))
        .map((note) => ({
            id: note.id,
            content: note.content,
            tag: note.tag,
            taskId: note.taskId,
            sessionId: note.sessionId,
            score: Number(note.score.toFixed(4)),
            updatedAt: note.updatedAt,
        }));

    if (ranked.length === 0) {
        return {
            status: 'empty' as const,
            query: normalized,
            count: 0,
            notes: [],
            message: 'No semantically related notes found.',
        };
    }

    return {
        status: 'success' as const,
        query: normalized,
        count: ranked.length,
        notes: ranked,
        message: `Found ${ranked.length} relevant note(s).`,
    };
}
