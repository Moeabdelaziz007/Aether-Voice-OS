import { z } from 'zod';

// Agent creation validation schemas
export const AgentNameSchema = z.string()
  .min(2, 'Agent name must be at least 2 characters')
  .max(50, 'Agent name must not exceed 50 characters')
  .regex(/^[a-zA-Z0-9\s\-_]+$/, 'Agent name can only contain alphanumeric characters, spaces, hyphens, and underscores');

export const PersonaSchema = z.string()
  .min(10, 'Persona description must be at least 10 characters')
  .max(500, 'Persona description must not exceed 500 characters');

export const SkillSchema = z.string()
  .min(2, 'Skill name must be at least 2 characters')
  .max(50, 'Skill name must not exceed 50 characters');

export const ToolSchema = z.string()
  .min(2, 'Tool name must be at least 2 characters')
  .max(50, 'Tool name must not exceed 50 characters');

export const AgentCreationInputSchema = z.object({
  name: AgentNameSchema,
  persona: PersonaSchema,
  skills: z.array(SkillSchema).min(1, 'At least one skill is required'),
  tools: z.array(ToolSchema).optional().default([]),
  description: z.string().optional(),
});

export type AgentCreationInput = z.infer<typeof AgentCreationInputSchema>;

// Firestore agent document schema
export const FirestoreAgentSchema = z.object({
  id: z.string().uuid(),
  name: AgentNameSchema,
  persona: PersonaSchema,
  skills: z.array(SkillSchema),
  tools: z.array(ToolSchema),
  description: z.string().optional(),
  createdAt: z.number(), // timestamp
  updatedAt: z.number(), // timestamp
  status: z.enum(['draft', 'active', 'archived']).default('draft'),
  userId: z.string().min(1, 'User ID is required'),
  voiceId: z.string().optional(),
  metadata: z.record(z.string(), z.any()).optional(),
});

export type FirestoreAgent = z.infer<typeof FirestoreAgentSchema>;

// Widget spec validation
export const WidgetSpecSchema = z.object({
  id: z.string(),
  type: z.string(),
  props: z.record(z.string(), z.any()),
  position: z.object({
    x: z.number(),
    y: z.number(),
  }).optional(),
  size: z.object({
    width: z.number(),
    height: z.number(),
  }).optional(),
});

export type WidgetSpec = z.infer<typeof WidgetSpecSchema>;

// Voice command validation
export const VoiceCommandSchema = z.object({
  command: z.string(),
  intent: z.string(),
  entities: z.record(z.string(), z.any()).optional(),
  confidence: z.number().min(0).max(1),
});

export type VoiceCommand = z.infer<typeof VoiceCommandSchema>;
