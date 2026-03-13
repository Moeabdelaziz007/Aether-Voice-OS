import { z } from 'zod';

/**
 * Widget specification schema for dynamic widget rendering
 * Used with Gemini function calling to generate widget structures
 */

export enum WidgetType {
  SKILL_TOGGLE = 'skill_toggle',
  AGENT_STATUS = 'agent_status',
  INTEGRATION_CARD = 'integration_card',
  MEMORY_PANEL = 'memory_panel',
  VOICE_CONTROL = 'voice_control',
  TASK_QUEUE = 'task_queue',
  METRIC_DISPLAY = 'metric_display',
  ACTION_BUTTON = 'action_button',
  TEXT_INPUT = 'text_input',
  SELECT_DROPDOWN = 'select_dropdown',
  TIMER = 'timer',
  ALERT = 'alert',
  CHART = 'chart',
  GALLERY = 'gallery',
}

export const WidgetSpecSchema = z.object({
  id: z.string().describe('Unique widget identifier'),
  type: z.nativeEnum(WidgetType).describe('Widget type'),
  title: z.string().optional().describe('Widget title'),
  description: z.string().optional().describe('Widget description'),
  props: z.record(z.string(), z.any()).describe('Widget-specific properties'),
  position: z.object({
    x: z.number().describe('X position (0-100%)'),
    y: z.number().describe('Y position (0-100%)'),
  }).optional().describe('Widget position on screen'),
  size: z.object({
    width: z.number().describe('Width in pixels or percentage'),
    height: z.number().describe('Height in pixels or percentage'),
  }).optional().describe('Widget dimensions'),
  visible: z.boolean().default(true).describe('Widget visibility'),
  interactive: z.boolean().default(true).describe('Widget interactivity'),
  priority: z.enum(['high', 'medium', 'low']).default('medium').describe('Rendering priority'),
  data: z.record(z.string(), z.any()).optional().describe('Widget data payload'),
});

export type WidgetSpec = z.infer<typeof WidgetSpecSchema>;

/**
 * Widget props by type
 */

export const SkillTogglePropsSchema = z.object({
  skillName: z.string(),
  isActive: z.boolean(),
  onChange: z.function().optional(),
  icon: z.string().optional(),
});

export type SkillToggleProps = z.infer<typeof SkillTogglePropsSchema>;

export const AgentStatusPropsSchema = z.object({
  agentId: z.string(),
  agentName: z.string(),
  status: z.enum(['online', 'offline', 'busy', 'idle']),
  lastSeen: z.number().optional(),
  icon: z.string().optional(),
});

export type AgentStatusProps = z.infer<typeof AgentStatusPropsSchema>;

export const IntegrationCardPropsSchema = z.object({
  integrationName: z.string(),
  isConnected: z.boolean(),
  icon: z.string().optional(),
  onConnect: z.function().optional(),
  onDisconnect: z.function().optional(),
  metadata: z.record(z.string(), z.any()).optional(),
});

export type IntegrationCardProps = z.infer<typeof IntegrationCardPropsSchema>;

export const MemoryPanelPropsSchema = z.object({
  memories: z.array(z.object({
    id: z.string(),
    content: z.string(),
    timestamp: z.number(),
    tags: z.array(z.string()).optional(),
  })),
  maxDisplay: z.number().default(5),
  onSelect: z.function().optional(),
});

export type MemoryPanelProps = z.infer<typeof MemoryPanelPropsSchema>;

export const VoiceControlPropsSchema = z.object({
  isListening: z.boolean(),
  transcript: z.string().optional(),
  onStart: z.function().optional(),
  onStop: z.function().optional(),
  commands: z.array(z.string()).optional(),
});

export type VoiceControlProps = z.infer<typeof VoiceControlPropsSchema>;

export const ActionButtonPropsSchema = z.object({
  label: z.string(),
  onClick: z.function().optional(),
  disabled: z.boolean().default(false),
  variant: z.enum(['primary', 'secondary', 'danger', 'success']).default('primary'),
  icon: z.string().optional(),
  loading: z.boolean().default(false),
});

export type ActionButtonProps = z.infer<typeof ActionButtonPropsSchema>;

/**
 * Gemini function calling schema for widget generation
 * This is what Gemini will return to create dynamic widgets
 */
export const GeminiWidgetCallSchema = z.object({
  function: z.literal('create_widgets'),
  widgets: z.array(WidgetSpecSchema),
  explanation: z.string().optional().describe('Why these widgets were created'),
});

export type GeminiWidgetCall = z.infer<typeof GeminiWidgetCallSchema>;

/**
 * Validate widget specs array before rendering
 */
export function validateWidgetSpecs(specs: unknown): WidgetSpec[] {
  try {
    const parsed = z.array(WidgetSpecSchema).parse(specs);
    return parsed;
  } catch (error) {
    console.error('[widget schema] Invalid widget specs:', error);
    throw new Error('Invalid widget specifications');
  }
}

/**
 * Validate individual widget spec
 */
export function validateWidgetSpec(spec: unknown): WidgetSpec {
  try {
    return WidgetSpecSchema.parse(spec);
  } catch (error) {
    console.error('[widget schema] Invalid widget spec:', error);
    throw new Error('Invalid widget specification');
  }
}

/**
 * Safe widget props parser based on type
 */
export function validateWidgetProps(type: WidgetType, props: unknown): Record<string, any> {
  const propSchemas: Record<WidgetType, z.ZodType> = {
    [WidgetType.SKILL_TOGGLE]: SkillTogglePropsSchema,
    [WidgetType.AGENT_STATUS]: AgentStatusPropsSchema,
    [WidgetType.INTEGRATION_CARD]: IntegrationCardPropsSchema,
    [WidgetType.MEMORY_PANEL]: MemoryPanelPropsSchema,
    [WidgetType.VOICE_CONTROL]: VoiceControlPropsSchema,
    [WidgetType.ACTION_BUTTON]: ActionButtonPropsSchema,
    [WidgetType.TASK_QUEUE]: z.record(z.any()),
    [WidgetType.METRIC_DISPLAY]: z.record(z.any()),
    [WidgetType.TEXT_INPUT]: z.record(z.any()),
    [WidgetType.SELECT_DROPDOWN]: z.record(z.any()),
    [WidgetType.TIMER]: z.record(z.any()),
    [WidgetType.ALERT]: z.record(z.any()),
    [WidgetType.CHART]: z.record(z.any()),
    [WidgetType.GALLERY]: z.record(z.any()),
  };

  const schema = propSchemas[type];
  if (!schema) {
    console.warn(`[widget schema] No schema for widget type: ${type}`);
    return props as Record<string, any>;
  }

  try {
    return schema.parse(props);
  } catch (error) {
    console.error(`[widget schema] Invalid props for widget type ${type}:`, error);
    throw new Error(`Invalid props for widget type: ${type}`);
  }
}
