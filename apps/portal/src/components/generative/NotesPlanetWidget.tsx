"use client";

import React, { useMemo, useState } from "react";
import { Pencil, Save, Trash2, Plus } from "lucide-react";
import { useAetherStore } from "@/store/useAetherStore";
import { recallNotesSemantic } from "@/app/actions/notesActions";

export function NotesPlanetWidget() {
    const notes = useAetherStore((s) => s.notesPlanet);
    const taskPulse = useAetherStore((s) => s.taskPulse);
    const sessionStartTime = useAetherStore((s) => s.sessionStartTime);
    const createPlanetNote = useAetherStore((s) => s.createPlanetNote);
    const updatePlanetNote = useAetherStore((s) => s.updatePlanetNote);
    const deletePlanetNote = useAetherStore((s) => s.deletePlanetNote);

    const [draft, setDraft] = useState("");
    const [tag, setTag] = useState("general");
    const [editingId, setEditingId] = useState<string | null>(null);
    const [editingDraft, setEditingDraft] = useState("");
    const [recallQuery, setRecallQuery] = useState("");
    const [recallMatches, setRecallMatches] = useState<Array<{ id: string; score: number; content: string }>>([]);

    const sortedNotes = useMemo(
        () => [...notes].sort((a, b) => b.updatedAt - a.updatedAt),
        [notes]
    );

    const handleCreate = () => {
        const content = draft.trim();
        if (!content) return;
        createPlanetNote({
            content,
            tag,
            taskId: taskPulse?.taskId,
            sessionId: sessionStartTime ? String(sessionStartTime) : undefined,
        });
        setDraft("");
    };

    const startEdit = (id: string, content: string) => {
        setEditingId(id);
        setEditingDraft(content);
    };

    const saveEdit = () => {
        if (!editingId) return;
        const nextContent = editingDraft.trim();
        if (!nextContent) return;
        updatePlanetNote(editingId, { content: nextContent });
        setEditingId(null);
        setEditingDraft("");
    };

    const handleRecall = async () => {
        const result = await recallNotesSemantic(recallQuery, 4);
        if (result.status !== "success") {
            setRecallMatches([]);
            return;
        }
        setRecallMatches(result.notes.map((note) => ({
            id: note.id,
            score: note.score,
            content: note.content,
        })));
    };

    return (
        <div className="flex h-full flex-col gap-3">
            <div className="flex items-center justify-between">
                <div className="text-xs text-cyan-300 font-mono tracking-[0.2em] uppercase">
                    Notes Planet
                </div>
                <div className="text-[10px] text-white/60 font-mono uppercase">
                    {sortedNotes.length} notes
                </div>
            </div>

            <div className="rounded-xl border border-white/10 bg-black/35 p-3">
                <div className="flex items-center gap-2 mb-2">
                    <select
                        aria-label="Note tag"
                        className="bg-white/5 border border-white/10 rounded-md text-[11px] text-white/80 px-2 py-1 outline-none"
                        value={tag}
                        onChange={(e) => setTag(e.target.value)}
                    >
                        <option value="general">general</option>
                        <option value="research">research</option>
                        <option value="todo">todo</option>
                        <option value="voice">voice</option>
                    </select>
                    <button
                        onClick={handleCreate}
                        aria-label="Add note"
                        className="inline-flex items-center gap-1 text-[11px] px-2 py-1 rounded-md bg-cyan-500/20 text-cyan-200 hover:bg-cyan-500/30 transition-colors"
                    >
                        <Plus className="w-3 h-3" />
                        add
                    </button>
                </div>
                <textarea
                    value={draft}
                    onChange={(e) => setDraft(e.target.value)}
                    placeholder="Capture memory crystal..."
                    className="w-full h-20 resize-none rounded-md bg-white/5 border border-white/10 px-2 py-2 text-xs text-white/90 placeholder:text-white/40 outline-none"
                />
                <div className="mt-2 text-[10px] text-white/40">
                    Linked task: {taskPulse?.taskId || "none"} · session: {sessionStartTime ? "active" : "none"}
                </div>
                <div className="mt-2 flex items-center gap-2">
                    <input
                        aria-label="Recall notes query"
                        value={recallQuery}
                        onChange={(e) => setRecallQuery(e.target.value)}
                        placeholder="Recall by idea..."
                        className="flex-1 rounded-md bg-black/35 border border-white/10 px-2 py-1 text-[11px] text-white/90 placeholder:text-white/40 outline-none"
                    />
                    <button
                        aria-label="Run semantic recall"
                        onClick={handleRecall}
                        className="text-[11px] px-2 py-1 rounded-md bg-emerald-500/20 text-emerald-200 hover:bg-emerald-500/30 transition-colors"
                    >
                        recall
                    </button>
                </div>
                {recallMatches.length > 0 && (
                    <div className="mt-2 space-y-1">
                        {recallMatches.map((match) => (
                            <div key={match.id} className="text-[10px] text-white/65 truncate">
                                {Math.round(match.score * 100)}% · {match.content}
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <div className="flex-1 overflow-auto space-y-2 pr-1">
                {sortedNotes.length === 0 ? (
                    <div className="text-xs text-white/50">No notes yet.</div>
                ) : (
                    sortedNotes.map((note) => (
                        <div key={note.id} className="rounded-lg border border-white/10 bg-white/[0.03] p-2">
                            <div className="flex items-center justify-between mb-1">
                                <div className="text-[10px] uppercase tracking-wider text-emerald-300/80">
                                    {note.tag}
                                </div>
                                <div className="flex items-center gap-1">
                                    {editingId === note.id ? (
                                        <button
                                            onClick={saveEdit}
                                            aria-label="Save note"
                                            className="p-1 rounded hover:bg-white/10 text-cyan-200"
                                        >
                                            <Save className="w-3 h-3" />
                                        </button>
                                    ) : (
                                        <button
                                            onClick={() => startEdit(note.id, note.content)}
                                            aria-label="Edit note"
                                            className="p-1 rounded hover:bg-white/10 text-white/70"
                                        >
                                            <Pencil className="w-3 h-3" />
                                        </button>
                                    )}
                                    <button
                                        onClick={() => deletePlanetNote(note.id)}
                                        aria-label="Delete note"
                                        className="p-1 rounded hover:bg-white/10 text-rose-300"
                                    >
                                        <Trash2 className="w-3 h-3" />
                                    </button>
                                </div>
                            </div>
                            {editingId === note.id ? (
                                <textarea
                                    value={editingDraft}
                                    onChange={(e) => setEditingDraft(e.target.value)}
                                    aria-label="Edit note content"
                                    className="w-full h-16 resize-none rounded bg-black/40 border border-white/10 px-2 py-1 text-xs text-white/90 outline-none"
                                />
                            ) : (
                                <div className="text-xs text-white/85 whitespace-pre-wrap">{note.content}</div>
                            )}
                            <div className="mt-1 text-[10px] text-white/45">
                                task:{note.taskId || "none"} · {new Date(note.updatedAt).toLocaleTimeString()}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
