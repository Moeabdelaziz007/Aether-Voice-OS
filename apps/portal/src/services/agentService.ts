import { FirestoreAgent } from '@/lib/validation';

// Mock listAgents since the service seems to have been removed or missing.
export const listAgents = async (userId?: string, status?: string): Promise<FirestoreAgent[]> => {
  return [
    {
      id: "agent-1",
      agent_id: "agent-1",
      name: "Atlas",
      role: "AI Companion",
      description: "Default Agent",
      status: "active",
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    } as any
  ];
};
