# Voice-to-Agent: Practical Usage Examples

## Example 1: Creating Agent from Voice Input

### Scenario
User says: "Create an agent called DataAnalyst that can analyze spreadsheets and generate reports"

### Implementation

```typescript
// In your voice handler or chat interface
import { createAgentFromVoice } from '@/services/agentService';

async function handleVoiceInput(transcript: string) {
  // Step 1: Parse transcript with Gemini or custom logic
  const agentInput = extractAgentDetails(transcript);
  // Returns:
  // {
  //   name: 'DataAnalyst',
  //   persona: 'A data analysis specialist...',
  //   skills: ['data_analysis', 'spreadsheet_processing', 'report_generation'],
  //   tools: ['excel', 'pandas', 'matplotlib']
  // }

  // Step 2: Create with idempotency
  const idempotencyKey = `voice-${Date.now()}`; // Unique key per request
  
  try {
    const { agentId, agent, isNew } = await createAgentFromVoice(
      agentInput,
      idempotencyKey,
      currentUserId // From auth context
    );

    // Step 3: Provide feedback
    if (isNew) {
      speak(`${agent.name} created successfully! It has ${agent.skills.length} skills.`);
    } else {
      speak(`${agent.name} already exists in your account.`);
    }

    // Step 4: Return to UI for further actions
    return agent;
  } catch (error) {
    speak(`Failed to create agent: ${error.message}`);
    throw error;
  }
}
```

---

## Example 2: Handling Duplicate Agent Creation

### Scenario
User says the same thing twice quickly, expecting only one agent created

### Implementation

```typescript
// The idempotency system handles this automatically
const transcript1 = "Create agent Analytics Bot";
const transcript2 = "Create agent Analytics Bot"; // Accidental repeat

const key = 'user-voice-session-123';

// First request
const result1 = await createAgentFromVoice(
  { name: 'Analytics Bot', persona: '...', skills: ['analytics'] },
  key
);
// Creates new agent: { agentId: 'uuid-1', isNew: true }

// Second request (within 1 hour)
const result2 = await createAgentFromVoice(
  { name: 'Analytics Bot', persona: '...', skills: ['analytics'] },
  key
);
// Returns cached agent: { agentId: 'uuid-1', isNew: false }

console.log(result1.agentId === result2.agentId); // true - same agent!
```

---

## Example 3: Voice Command Routing

### Scenario
Multiple voice commands in sequence

### Implementation

```typescript
// File: components/gemigram/CustomVoiceRouter.tsx
import { GlobalVoiceRouter } from '@/components/gemigram/GlobalVoiceRouter';
import { useAetherStore } from '@/store/useAetherStore';

export function CommandSequenceExample() {
  const transcripts = [
    'Open agent Atlas',              // Command: open_agent
    'Deploy this agent',             // Command: deploy_agent
    'Show me the widgets',           // Command: show_widgets
    'What can you do?',              // Command: show_capabilities
  ];

  return (
    <div>
      {transcripts.map((transcript, i) => (
        <GlobalVoiceRouter 
          key={i}
          transcript={transcript}
          onProcessing={(isProcessing) => {
            console.log(`Processing command ${i + 1}: ${isProcessing}`);
          }}
        />
      ))}
    </div>
  );
}

// Each transcript triggers:
// 1. Pattern matching in GlobalVoiceRouter
// 2. Intent + entity extraction
// 3. Command execution with error handling
// 4. Terminal logging for debugging
```

---

## Example 4: Dynamic Widget Generation

### Scenario
After creating agent, Gemini suggests relevant widgets

### Implementation

```typescript
// File: hooks/useWidgetGeneration.ts
import { parseGeminiWidgetResponse } from '@/services/widgets/planner';
import { validateWidgetSpecs } from '@/services/widgets/schema';
import { renderWidgets } from '@/services/widgets/registry';

export function useWidgetGeneration(agent) {
  const [widgets, setWidgets] = useState([]);

  useEffect(() => {
    // Simulate Gemini function calling
    const generateWidgets = async () => {
      const geminiResponse = {
        function: 'create_widgets',
        widgets: [
          {
            id: 'skill-toggle-1',
            type: 'skill_toggle',
            title: `Toggle ${agent.skills[0]}`,
            props: {
              skillName: agent.skills[0],
              isActive: true,
            },
            priority: 'high',
          },
          {
            id: 'agent-status-1',
            type: 'agent_status',
            title: `Status: ${agent.name}`,
            props: {
              agentId: agent.id,
              agentName: agent.name,
              status: 'online',
            },
            priority: 'high',
          },
          {
            id: 'action-deploy',
            type: 'action_button',
            props: {
              label: 'Deploy Agent',
              variant: 'primary',
              onClick: () => deployAgent(agent.id),
            },
            priority: 'medium',
          },
        ],
        explanation: 'Created control widgets for agent management',
      };

      try {
        // Validate and parse
        const { widgets: validatedWidgets } = parseGeminiWidgetResponse(geminiResponse);
        setWidgets(validatedWidgets);

        // Render widgets
        const rendered = renderWidgets(validatedWidgets);
        return rendered;
      } catch (error) {
        console.error('Widget generation failed:', error);
        // Show error to user
        return null;
      }
    };

    generateWidgets();
  }, [agent]);

  return widgets;
}

// Usage in component
function AgentDashboard({ agent }) {
  const widgets = useWidgetGeneration(agent);

  return (
    <div className="grid grid-cols-3 gap-4">
      {renderWidgets(widgets)}
    </div>
  );
}
```

---

## Example 5: Complete Voice-Enabled Agent Orchestration

### Scenario
Full user journey from voice input to deployed agent

### Implementation

```typescript
// File: app/agent-creation/page.tsx
'use client';

import { useState, useCallback } from 'react';
import GemiGramInterface from '@/components/gemigram/GemiGramInterface';
import { createAgentFromVoice } from '@/services/agentService';
import { parseGeminiWidgetResponse } from '@/services/widgets/planner';

export default function AgentCreationPage() {
  const [step, setStep] = useState<'voice-input' | 'confirmation' | 'deployed'>('voice-input');
  const [currentAgent, setCurrentAgent] = useState(null);
  const [widgets, setWidgets] = useState([]);

  const handleVoiceTranscript = useCallback(async (transcript: string) => {
    // Step 1: Extract agent details (in real app, use Gemini)
    const agentInput = {
      name: extractName(transcript),
      persona: extractPersona(transcript),
      skills: extractSkills(transcript),
    };

    // Step 2: Create agent with voice confirmation
    try {
      const { agent, isNew } = await createAgentFromVoice(agentInput);
      setCurrentAgent(agent);
      setStep('confirmation');

      // Step 3: Generate widgets
      const geminiResponse = await callGeminiFunctions({
        function: 'create_widgets',
        context: { agent },
      });

      const { widgets: generatedWidgets } = parseGeminiWidgetResponse(geminiResponse);
      setWidgets(generatedWidgets);

      // Step 4: Speak confirmation
      await speak(
        `${agent.name} has been created with ${agent.skills.length} skills. Ready to deploy?`
      );
    } catch (error) {
      await speak(`Failed to create agent: ${error.message}`);
    }
  }, []);

  const handleDeploy = useCallback(async () => {
    if (!currentAgent) return;

    try {
      // Deploy agent (mock for this example)
      await deployAgent(currentAgent.id);
      setStep('deployed');
      await speak(`${currentAgent.name} is now live and ready to use!`);
    } catch (error) {
      await speak(`Deployment failed: ${error.message}`);
    }
  }, [currentAgent]);

  return (
    <div className="w-full h-screen">
      {step === 'voice-input' && (
        <GemiGramInterface />
      )}
      
      {step === 'confirmation' && currentAgent && (
        <ConfirmationPanel
          agent={currentAgent}
          widgets={widgets}
          onDeploy={handleDeploy}
        />
      )}

      {step === 'deployed' && currentAgent && (
        <SuccessPanel agent={currentAgent} />
      )}
    </div>
  );
}

// Helper functions (mock implementations)
function extractName(transcript: string): string {
  const match = transcript.match(/(?:agent\s+)?named\s+(\w+)/i);
  return match?.[1] || 'Agent';
}

function extractPersona(transcript: string): string {
  return transcript; // In real app, use Gemini to extract
}

function extractSkills(transcript: string): string[] {
  const skills = transcript.match(/\b(?:skill|can)\s+(\w+)/gi) || [];
  return skills.map((s) => s.toLowerCase());
}

async function speak(text: string) {
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(utterance);
  }
}
```

---

## Example 6: Error Recovery and Rollback

### Scenario
Agent creation starts but network fails mid-write

### Implementation

```typescript
// File: services/agentService.ts (error handling flow)
import { createAgentFromVoice } from '@/services/agentService';

async function createAgentWithRollback(input) {
  const agentId = uuidv4();
  const startTime = Date.now();

  try {
    // Attempt creation
    const { agent, isNew } = await createAgentFromVoice(
      input,
      `create-${agentId}`, // Track this specific attempt
      currentUserId
    );

    if (!isNew) {
      // Already exists, no need to rollback
      return agent;
    }

    return agent;
  } catch (error) {
    // Determine if we should rollback
    const duration = Date.now() - startTime;
    const isNetworkError = error.code === 'network-error';
    const isTimeoutError = duration > 30000;

    if (isNetworkError || isTimeoutError) {
      // Attempt to delete the partially created agent
      try {
        await deleteAgent(agentId, currentUserId);
        console.log('[Rollback] Agent deleted:', agentId);
      } catch (deleteError) {
        console.error('[Rollback] Failed to delete agent:', deleteError);
        // Even if rollback fails, propagate original error
      }
    }

    throw error;
  }
}
```

---

## Example 7: Batch Agent Creation

### Scenario
Import multiple agents from file or voice list

### Implementation

```typescript
import { batchCreateAgents } from '@/services/agentService';

async function importAgentsFromCSV(csvText: string) {
  const lines = csvText.split('\n').slice(1); // Skip header

  const inputs = lines.map((line) => {
    const [name, persona, skills] = line.split(',');
    return {
      name: name.trim(),
      persona: persona.trim(),
      skills: skills.split(';').map((s) => s.trim()),
    };
  });

  try {
    const { agentIds, failed } = await batchCreateAgents(inputs);

    if (failed.length === 0) {
      speak(`Successfully imported ${agentIds.length} agents!`);
    } else {
      speak(`Imported ${agentIds.length} agents, but ${failed.length} failed: ${failed.join(', ')}`);
    }

    return { agentIds, failed };
  } catch (error) {
    speak(`Batch import failed: ${error.message}`);
    throw error;
  }
}
```

---

## Example 8: Custom Widget Registration

### Scenario
Add specialized widget for custom use case

### Implementation

```typescript
// File: app/custom-widgets.ts
import { registerCustomWidget } from '@/services/widgets/registry';
import MyCustomWidget from '@/components/widgets/MyCustomWidget';

// Register once at app startup
registerCustomWidget('my_analytics_dashboard', MyCustomWidget);

// Now Gemini can generate widgets of this type:
const geminiResponse = {
  function: 'create_widgets',
  widgets: [
    {
      id: 'custom-1',
      type: 'my_analytics_dashboard', // Uses registered component
      props: {
        dataSource: 'agent-logs',
        timeRange: '24h',
      },
    },
  ],
};

// Component automatically renders with the custom widget
```

---

## Example 9: Monitoring and Logging

### Scenario
Track all agent creations and voice commands

### Implementation

```typescript
// File: hooks/useVoiceLogging.ts
import { useAetherStore } from '@/store/useAetherStore';

export function useVoiceLogging() {
  const addTerminalLog = useAetherStore((s) => s.addTerminalLog);

  const logAgentCreation = (agent, duration) => {
    addTerminalLog(
      'INFO',
      `Agent created: ${agent.name} (${agent.id}) in ${duration}ms`
    );
  };

  const logCommand = (intent, entities, success) => {
    addTerminalLog(
      success ? 'SUCCESS' : 'ERROR',
      `Command: ${intent} ${JSON.stringify(entities)}`
    );
  };

  const logWidget = (type, count) => {
    addTerminalLog('INFO', `Generated ${count} ${type} widgets`);
  };

  return { logAgentCreation, logCommand, logWidget };
}
```

---

## Example 10: Accessibility Testing

### Scenario
Ensure voice interface works with screen readers

### Implementation

```typescript
// File: __tests__/voice-accessibility.test.tsx
import { render, screen } from '@testing-library/react';
import GemiGramInterface from '@/components/gemigram/GemiGramInterface';

describe('Voice Interface Accessibility', () => {
  it('announces voice status changes', async () => {
    const { container } = render(<GemiGramInterface />);

    const statusRegion = container.querySelector('[aria-live="polite"]');
    expect(statusRegion).toBeInTheDocument();

    // Status should update as listening state changes
    await waitFor(() => {
      expect(statusRegion).toHaveTextContent('Listening');
    });
  });

  it('provides keyboard alternatives', () => {
    const { container } = render(<GemiGramInterface />);

    // Development-only keyboard controls should be documented
    const devMenu = container.querySelector('details');
    expect(devMenu).toBeInTheDocument();
    expect(devMenu).toHaveTextContent('Space: Toggle listening');
  });

  it('maintains semantic structure', () => {
    const { container } = render(<GemiGramInterface />);

    expect(container.querySelector('header')).toBeInTheDocument();
    expect(container.querySelector('button[aria-label*="listening"]')).toBeInTheDocument();
  });
});
```

---

These examples demonstrate the complete voice-to-agent workflow from simple use cases to advanced orchestration scenarios. Each can be adapted to your specific needs!
