import React from "react";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import OrbitalWorkspaceOverlay from "@/components/HUD/OrbitalWorkspaceOverlay";
import { useAetherStore } from "@/store/useAetherStore";

describe("OrbitalWorkspaceOverlay", () => {
  beforeEach(() => {
    const store = useAetherStore.getState();
    store.clearOrbitRegistry();
    store.focusOrbitPlanet(null);
    store.setFocusModeEnvironment(false);
    store.setOrbitalLayoutPreset("mid");
  });

  it("renders materialized planets from orbit registry", () => {
    const store = useAetherStore.getState();
    store.applyWorkspaceState({
      action: "materialize_app",
      app_id: "planet-voyager",
      x: 90,
      y: 30,
      orbit_lane: "inner",
    });
    store.applyWorkspaceState({
      action: "focus_app",
      app_id: "planet-voyager",
      focused_app_id: "planet-voyager",
    });

    render(<OrbitalWorkspaceOverlay />);

    expect(screen.getByText("planet-voyager")).toBeTruthy();
  });
});
