import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import { NotesPlanetWidget } from "@/components/generative/NotesPlanetWidget";
import { useAetherStore } from "@/store/useAetherStore";

describe("NotesPlanetWidget", () => {
  beforeEach(() => {
    const store = useAetherStore.getState();
    store.clearPlanetNotes();
    store.setTaskPulse(null);
    store.setSessionStartTime(null);
  });

  it("creates and renders a new note", () => {
    const store = useAetherStore.getState();
    store.setTaskPulse({
      taskId: "task-ui-note",
      phase: "EXECUTING",
      action: "capture_note",
      vibe: "typing",
      intensity: 0.6,
      timestamp: Date.now(),
    });
    store.setSessionStartTime(999);

    render(<NotesPlanetWidget />);
    fireEvent.change(screen.getByPlaceholderText("Capture memory crystal..."), {
      target: { value: "Remember fallback strategy" },
    });
    fireEvent.click(screen.getByLabelText("Add note"));

    expect(screen.getByText("Remember fallback strategy")).toBeTruthy();
    expect(screen.getByText(/task:task-ui-note/i)).toBeTruthy();
  });
});
