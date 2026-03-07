import React from "react";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import MissionControlHUD from "@/components/HUD/MissionControlHUD";
import { useAetherStore } from "@/store/useAetherStore";

describe("MissionControlHUD", () => {
  beforeEach(() => {
    const store = useAetherStore.getState();
    store.setWorkspaceGalaxy("Genesis");
    store.clearMissionLog();
    store.setTaskPulse(null);
  });

  it("renders pulse thought and mapped phase label", () => {
    const store = useAetherStore.getState();
    store.setWorkspaceGalaxy("gal-alpha");
    store.setTaskPulse({
      taskId: "task-1",
      phase: "EXECUTING",
      action: "analyze_repository",
      vibe: "focusing",
      thought: "Running static checks on the graph.",
      intensity: 0.7,
      timestamp: Date.now(),
    });
    store.pushMissionLog({
      taskId: "task-1",
      title: "Repository analysis started",
      detail: "Collected tool metadata",
      status: "in-progress",
    });

    render(<MissionControlHUD />);

    expect(screen.getByText("Mission Control")).toBeTruthy();
    expect(screen.getByText("gal-alpha")).toBeTruthy();
    expect(screen.getByText("SYNAPSES_LINKED")).toBeTruthy();
    expect(screen.getByText("analyze_repository")).toBeTruthy();
    expect(screen.getByText("Running static checks on the graph.")).toBeTruthy();
    expect(screen.getByText("Repository analysis started")).toBeTruthy();
  });

  it("shows idle fallback when no pulse exists", () => {
    render(<MissionControlHUD />);
    expect(screen.getByText("Awaiting mission pulse.")).toBeTruthy();
    expect(screen.getByText("No timeline entries yet.")).toBeTruthy();
  });
});
