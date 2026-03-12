import React, { ComponentType } from 'react';
import { WidgetType, WidgetSpec } from './schema';

/**
 * Component registry for dynamic widget rendering
 * Maps widget type strings to React components
 */

// Placeholder components for each widget type
// In a real app, these would be actual component implementations

const SkillToggleWidget: ComponentType<any> = ({ skillName, isActive, onChange }) => (
  <div className="flex items-center gap-2 p-3 bg-black/40 border border-cyan-500/20 rounded-lg">
    <div className={`w-3 h-3 rounded-full ${isActive ? 'bg-cyan-500 shadow-lg shadow-cyan-500/50' : 'bg-gray-600'}`} />
    <span className="text-sm text-white">{skillName}</span>
    <button
      onClick={onChange}
      className="ml-auto px-2 py-1 text-xs bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/50 rounded transition-colors"
    >
      {isActive ? 'Disable' : 'Enable'}
    </button>
  </div>
);

const AgentStatusWidget: ComponentType<any> = ({ agentName, status }) => (
  <div className="p-4 bg-black/40 border border-purple-500/20 rounded-lg">
    <div className="flex items-center gap-2 mb-2">
      <div className={`w-2 h-2 rounded-full ${status === 'online' ? 'bg-green-500' : status === 'busy' ? 'bg-yellow-500' : 'bg-gray-600'}`} />
      <span className="font-semibold text-white">{agentName}</span>
    </div>
    <span className="text-xs text-gray-400 capitalize">{status}</span>
  </div>
);

const IntegrationCardWidget: ComponentType<any> = ({ integrationName, isConnected, onConnect, onDisconnect }) => (
  <div className="p-4 bg-black/40 border border-emerald-500/20 rounded-lg">
    <h4 className="font-semibold text-white mb-2">{integrationName}</h4>
    <div className="flex items-center gap-2">
      <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500' : 'bg-gray-600'}`} />
      <span className="text-xs text-gray-400">{isConnected ? 'Connected' : 'Disconnected'}</span>
    </div>
    <button
      onClick={isConnected ? onDisconnect : onConnect}
      className="mt-3 w-full px-2 py-1 text-xs bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/50 rounded transition-colors"
    >
      {isConnected ? 'Disconnect' : 'Connect'}
    </button>
  </div>
);

const MemoryPanelWidget: ComponentType<any> = ({ memories = [] }) => (
  <div className="space-y-2 p-4 bg-black/40 border border-blue-500/20 rounded-lg">
    <h4 className="text-xs uppercase tracking-widest text-blue-600 mb-3">Memory</h4>
    {memories.slice(0, 5).map((mem: any) => (
      <div key={mem.id} className="text-xs text-gray-300 truncate">{mem.content}</div>
    ))}
  </div>
);

const VoiceControlWidget: ComponentType<any> = ({ isListening, transcript }) => (
  <div className="p-4 bg-black/40 border border-pink-500/20 rounded-lg">
    <div className="flex items-center gap-2 mb-2">
      <div className={`w-2 h-2 rounded-full ${isListening ? 'bg-pink-500 animate-pulse' : 'bg-gray-600'}`} />
      <span className="text-sm font-semibold text-white">{isListening ? 'Listening...' : 'Ready'}</span>
    </div>
    {transcript && <div className="text-xs text-gray-300 mt-2">{transcript}</div>}
  </div>
);

const ActionButtonWidget: ComponentType<any> = ({ label, onClick, variant = 'primary', loading = false }) => {
  const variants: Record<string, string> = {
    primary: 'bg-cyan-500/20 border-cyan-500/50 hover:bg-cyan-500/30',
    secondary: 'bg-gray-500/20 border-gray-500/50 hover:bg-gray-500/30',
    danger: 'bg-red-500/20 border-red-500/50 hover:bg-red-500/30',
    success: 'bg-green-500/20 border-green-500/50 hover:bg-green-500/30',
  };

  return (
    <button
      onClick={onClick}
      disabled={loading}
      className={`w-full px-4 py-2 text-sm font-semibold text-white border rounded-lg transition-colors ${variants[variant] || variants.primary}`}
    >
      {loading ? 'Loading...' : label}
    </button>
  );
};

const DefaultWidget: ComponentType<any> = ({ type, title }) => (
  <div className="p-4 bg-black/40 border border-gray-500/20 rounded-lg">
    <p className="text-xs text-gray-400">
      {title || `Widget (${type})`}
    </p>
  </div>
);

/**
 * Complete widget component registry
 */
export const WidgetComponentRegistry: Record<WidgetType, ComponentType<any>> = {
  [WidgetType.SKILL_TOGGLE]: SkillToggleWidget,
  [WidgetType.AGENT_STATUS]: AgentStatusWidget,
  [WidgetType.INTEGRATION_CARD]: IntegrationCardWidget,
  [WidgetType.MEMORY_PANEL]: MemoryPanelWidget,
  [WidgetType.VOICE_CONTROL]: VoiceControlWidget,
  [WidgetType.ACTION_BUTTON]: ActionButtonWidget,
  [WidgetType.TASK_QUEUE]: DefaultWidget,
  [WidgetType.METRIC_DISPLAY]: DefaultWidget,
  [WidgetType.TEXT_INPUT]: DefaultWidget,
  [WidgetType.SELECT_DROPDOWN]: DefaultWidget,
  [WidgetType.TIMER]: DefaultWidget,
  [WidgetType.ALERT]: DefaultWidget,
  [WidgetType.CHART]: DefaultWidget,
  [WidgetType.GALLERY]: DefaultWidget,
};

/**
 * Render a widget by spec
 */
export function renderWidget(spec: WidgetSpec): React.ReactNode {
  const Component = WidgetComponentRegistry[spec.type as WidgetType];

  if (!Component) {
    console.warn(`[widget registry] Unknown widget type: ${spec.type}`);
    return <DefaultWidget type={spec.type} title={spec.title} />;
  }

  return (
    <div key={spec.id} className="widget-container">
      <Component {...spec.props} />
    </div>
  );
}

/**
 * Render multiple widgets
 */
export function renderWidgets(specs: WidgetSpec[]): React.ReactNode[] {
  return specs.map((spec) => renderWidget(spec));
}

/**
 * Get component for widget type
 */
export function getWidgetComponent(type: WidgetType): ComponentType<any> | undefined {
  return WidgetComponentRegistry[type];
}

/**
 * Check if widget type is supported
 */
export function isWidgetTypeSupported(type: string): type is WidgetType {
  return Object.values(WidgetType).includes(type as WidgetType);
}

/**
 * Register custom widget component
 */
export function registerCustomWidget(type: string, component: ComponentType<any>): void {
  (WidgetComponentRegistry as Record<string, ComponentType<any>>)[type] = component;
  console.log(`[widget registry] Registered custom widget: ${type}`);
}
