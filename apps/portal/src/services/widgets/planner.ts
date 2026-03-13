import { WidgetSpec, validateWidgetSpecs, GeminiWidgetCallSchema } from './schema';
import { v4 as uuidv4 } from 'uuid';

/**
 * Widget Planner service
 * Handles:
 * - Parsing Gemini function calling responses
 * - Validating widget specifications
 * - Managing widget lifecycle and layout
 */

export interface WidgetPlan {
  id: string;
  widgets: WidgetSpec[];
  explanation: string;
  generatedAt: number;
  status: 'pending' | 'rendered' | 'error' | 'archived';
  error?: string;
}

/**
 * Parse Gemini function call response for widgets
 */
export function parseGeminiWidgetResponse(
  response: unknown
): { widgets: WidgetSpec[]; explanation: string } {
  try {
    // Validate against Gemini widget call schema
    const validated = GeminiWidgetCallSchema.parse(response);

    // Ensure all widgets have unique IDs
    const widgets = validated.widgets.map((w) => ({
      ...w,
      id: w.id || uuidv4(),
    }));

    // Validate all widgets
    const validated_widgets = validateWidgetSpecs(widgets);

    return {
      widgets: validated_widgets,
      explanation: validated.explanation || 'Widgets generated from voice command',
    };
  } catch (error) {
    console.error('[widget planner] Failed to parse Gemini response:', error);
    throw new Error('Invalid widget response from Gemini');
  }
}

/**
 * Create a widget plan from specs
 */
export function createWidgetPlan(
  widgets: WidgetSpec[],
  explanation: string = ''
): WidgetPlan {
  const planId = uuidv4();

  return {
    id: planId,
    widgets,
    explanation,
    generatedAt: Date.now(),
    status: 'pending',
  };
}

/**
 * Auto-layout widgets using a simple grid system
 */
export function autoLayoutWidgets(
  widgets: WidgetSpec[],
  containerWidth: number = 1200,
  containerHeight: number = 800
): WidgetSpec[] {
  const gridCols = 3;
  const gridRows = Math.ceil(widgets.length / gridCols);
  const cellWidth = containerWidth / gridCols;
  const cellHeight = containerHeight / gridRows;

  return widgets.map((widget, index) => {
    const row = Math.floor(index / gridCols);
    const col = index % gridCols;

    return {
      ...widget,
      position: {
        x: (col * cellWidth) / containerWidth * 100,
        y: (row * cellHeight) / containerHeight * 100,
      },
      size: {
        width: (cellWidth * 0.95) / containerWidth * 100,
        height: (cellHeight * 0.95) / containerHeight * 100,
      },
    };
  });
}

/**
 * Filter widgets by priority
 */
export function filterWidgetsByPriority(
  widgets: WidgetSpec[],
  priority: 'high' | 'medium' | 'low'
): WidgetSpec[] {
  return widgets.filter((w) => w.priority === priority);
}

/**
 * Sort widgets by priority
 */
export function sortWidgetsByPriority(widgets: WidgetSpec[]): WidgetSpec[] {
  const priorityOrder = { high: 0, medium: 1, low: 2 };
  return [...widgets].sort(
    (a, b) => priorityOrder[a.priority || 'medium'] - priorityOrder[b.priority || 'medium']
  );
}

/**
 * Batch widgets into groups for rendering
 */
export function batchWidgets(widgets: WidgetSpec[], batchSize: number = 5): WidgetSpec[][] {
  const batches: WidgetSpec[][] = [];
  for (let i = 0; i < widgets.length; i += batchSize) {
    batches.push(widgets.slice(i, i + batchSize));
  }
  return batches;
}

/**
 * Find widget by ID
 */
export function findWidget(widgets: WidgetSpec[], id: string): WidgetSpec | undefined {
  return widgets.find((w) => w.id === id);
}

/**
 * Update widget in array
 */
export function updateWidget(
  widgets: WidgetSpec[],
  id: string,
  updates: Partial<WidgetSpec>
): WidgetSpec[] {
  return widgets.map((w) => (w.id === id ? { ...w, ...updates } : w));
}

/**
 * Remove widget by ID
 */
export function removeWidget(widgets: WidgetSpec[], id: string): WidgetSpec[] {
  return widgets.filter((w) => w.id !== id);
}

/**
 * Merge widget plans (for combining multiple Gemini responses)
 */
export function mergeWidgetPlans(...plans: WidgetPlan[]): WidgetPlan {
  const mergedPlan: WidgetPlan = {
    id: uuidv4(),
    widgets: [],
    explanation: plans.map((p) => p.explanation).join('; '),
    generatedAt: Date.now(),
    status: 'pending',
  };

  for (const plan of plans) {
    mergedPlan.widgets.push(...plan.widgets);
  }

  // Remove duplicate IDs
  const seen = new Set<string>();
  mergedPlan.widgets = mergedPlan.widgets.filter((w) => {
    if (seen.has(w.id)) return false;
    seen.add(w.id);
    return true;
  });

  return mergedPlan;
}

/**
 * Optimize widget rendering by removing invisible/low-priority widgets
 */
export function optimizeWidgetPlan(plan: WidgetPlan, maxWidgets: number = 10): WidgetPlan {
  let widgets = plan.widgets.filter((w) => w.visible !== false);

  if (widgets.length > maxWidgets) {
    widgets = sortWidgetsByPriority(widgets).slice(0, maxWidgets);
  }

  return {
    ...plan,
    widgets,
  };
}

/**
 * Validate widget plan before rendering
 */
export function validateWidgetPlan(plan: WidgetPlan): { valid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!plan.widgets || plan.widgets.length === 0) {
    errors.push('Widget plan has no widgets');
  }

  if (!plan.id) {
    errors.push('Widget plan missing ID');
  }

  // Check for duplicate widget IDs
  const ids = new Set<string>();
  for (const widget of plan.widgets) {
    if (ids.has(widget.id)) {
      errors.push(`Duplicate widget ID: ${widget.id}`);
    }
    ids.add(widget.id);
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Generate widget cache key for memoization
 */
export function getWidgetCacheKey(plan: WidgetPlan): string {
  const widgetIds = plan.widgets.map((w) => w.id).sort().join(',');
  return `widgets:${widgetIds}:${plan.generatedAt}`;
}
