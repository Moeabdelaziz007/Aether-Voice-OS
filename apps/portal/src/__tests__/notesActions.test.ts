import { beforeEach, describe, expect, it } from "vitest";
import { recallNotesSemantic } from "@/app/actions/notesActions";
import { useAetherStore } from "@/store/useAetherStore";

describe("notesActions", () => {
  beforeEach(() => {
    const store = useAetherStore.getState();
    store.clearPlanetNotes();
  });

  it("returns semantically ranked notes", async () => {
    const store = useAetherStore.getState();
    store.createPlanetNote({
      content: "Fallback handover script for notes planet demo",
      tag: "research",
      taskId: "task-recall",
      sessionId: "sess-1",
    });
    store.createPlanetNote({
      content: "Buy fruits and vegetables",
      tag: "general",
      taskId: "task-home",
      sessionId: "sess-2",
    });

    const result = await recallNotesSemantic("handover fallback", 3);
    expect(result.status).toBe("success");
    expect(result.notes.length).toBeGreaterThan(0);
    expect(result.notes[0].content.toLowerCase()).toContain("handover");
  });
});
