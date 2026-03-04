/**
 * @deprecated — Aether Voice OS — Engine Telemetry Hook.
 *
 * ⚠️ DEPRECATED: This hook opened a raw WebSocket without Ed25519 authentication,
 * which always fails the gateway handshake. ALL telemetry data now flows
 * through the main `useAetherGateway` hook (V2), which properly handles:
 *   - engine_state
 *   - affective_score
 *   - transcript
 *   - neural_event
 *   - vision_pulse
 *   - tool_result
 *   - soul_handoff
 *
 * For dashboard telemetry, use the Admin REST API at http://localhost:18790
 *
 * This file is kept as a no-op stub for backwards compatibility.
 * Remove all imports of this hook and use `useAetherGateway` instead.
 */

export function useEngineTelemetry() {
    console.warn(
        "⚠️ useEngineTelemetry is DEPRECATED. " +
        "All telemetry now flows through useAetherGateway (V2). " +
        "Remove this import."
    );
    return {
        connected: false,
        latencyMs: 0,
        logs: [] as string[],
    };
}
