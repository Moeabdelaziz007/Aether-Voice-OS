import React from "react";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import MirrorInteractionOverlay from "@/components/HUD/MirrorInteractionOverlay";
import { useAetherStore } from "@/store/useAetherStore";

describe("MirrorInteractionOverlay", () => {
  beforeEach(() => {
    const store = useAetherStore.getState();
    store.clearMirrorFrameEvents();
  });

  it("renders recent mirror interaction labels", () => {
    const store = useAetherStore.getState();
    store.addMirrorFrameEvent({
      action: "type",
      eventKind: "typing",
      selector: "#query",
      text: "voyager",
      latencyMs: 21,
    });

    render(<MirrorInteractionOverlay />);
    expect(screen.getByText("typing")).toBeTruthy();
  });
});
