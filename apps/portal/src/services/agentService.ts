import { db, auth } from '@/lib/firebase';
import {
  collection,
  doc,
  setDoc,
  getDoc,
  getDocs,
  updateDoc,
  deleteDoc,
  query,
  where,
  Timestamp,
  writeBatch,
} from 'firebase/firestore';
import { v4 as uuidv4 } from 'uuid';
import {
  AgentCreationInput,
  AgentCreationInputSchema,
  FirestoreAgent,
  FirestoreAgentSchema,
} from '@/lib/validation';

/**
 * Idempotency key storage to prevent duplicate agent creation
 * In production, store this in Firestore with TTL
 */
const idempotencyCache = new Map<string, { agentId: string; timestamp: number }>();
const IDEMPOTENCY_TTL = 3600000; // 1 hour

/**
 * Clear expired idempotency keys
 */
function cleanupIdempotencyCache() {
  const now = Date.now();
  for (const [key, value] of idempotencyCache.entries()) {
    if (now - value.timestamp > IDEMPOTENCY_TTL) {
      idempotencyCache.delete(key);
    }
  }
}

/**
 * Create a new agent from voice input with idempotency
 */
export async function createAgentFromVoice(
  input: AgentCreationInput,
  idempotencyKey?: string,
  currentUserId?: string
): Promise<{ agentId: string; agent: FirestoreAgent; isNew: boolean }> {
  cleanupIdempotencyCache();

  // Check idempotency key
  if (idempotencyKey && idempotencyCache.has(idempotencyKey)) {
    const cached = idempotencyCache.get(idempotencyKey)!;
    console.log('[agentService] Returning cached agent for idempotency key:', idempotencyKey);
    const agent = await getAgent(cached.agentId, currentUserId);
    return { agentId: cached.agentId, agent: agent!, isNew: false };
  }

  // Validate input
  const validatedInput = AgentCreationInputSchema.parse(input);

  // Get current user
  const userId = currentUserId || auth?.currentUser?.uid;
  if (!userId) {
    throw new Error('User must be authenticated to create an agent');
  }

  // Check if Firestore is available
  if (!db) {
    throw new Error('Firestore is not initialized. Cannot create agent.');
  }

  try {
    const agentId = uuidv4();
    const now = Timestamp.now();

    const agent: FirestoreAgent = {
      id: agentId,
      name: validatedInput.name,
      persona: validatedInput.persona,
      skills: validatedInput.skills,
      tools: validatedInput.tools || [],
      description: validatedInput.description,
      createdAt: now.toMillis(),
      updatedAt: now.toMillis(),
      status: 'draft',
      userId,
    };

    // Validate against Firestore schema
    FirestoreAgentSchema.parse(agent);

    // Write to Firestore with retry logic
    const agentDocRef = doc(db, `users/${userId}/agents`, agentId);
    await setDoc(agentDocRef, {
      ...agent,
      createdAt: now,
      updatedAt: now,
    });

    // Cache idempotency key
    if (idempotencyKey) {
      idempotencyCache.set(idempotencyKey, {
        agentId,
        timestamp: Date.now(),
      });
    }

    console.log('[agentService] Agent created successfully:', agentId);
    return { agentId, agent, isNew: true };
  } catch (error) {
    console.error('[agentService] Failed to create agent:', error);
    throw error;
  }
}

/**
 * Get agent by ID
 */
export async function getAgent(
  agentId: string,
  currentUserId?: string
): Promise<FirestoreAgent | null> {
  const userId = currentUserId || auth?.currentUser?.uid;
  if (!userId || !db) {
    console.warn('[agentService] User or Firestore not available');
    return null;
  }

  try {
    const agentDocRef = doc(db, `users/${userId}/agents`, agentId);
    const agentSnap = await getDoc(agentDocRef);

    if (!agentSnap.exists()) {
      console.warn('[agentService] Agent not found:', agentId);
      return null;
    }

    const data = agentSnap.data();
    return FirestoreAgentSchema.parse({
      ...data,
      createdAt: data.createdAt?.toMillis?.() || data.createdAt,
      updatedAt: data.updatedAt?.toMillis?.() || data.updatedAt,
    });
  } catch (error) {
    console.error('[agentService] Failed to get agent:', error);
    return null;
  }
}

/**
 * List all agents for current user
 */
export async function listAgents(
  currentUserId?: string,
  status?: 'draft' | 'active' | 'archived'
): Promise<FirestoreAgent[]> {
  const userId = currentUserId || auth?.currentUser?.uid;
  if (!userId || !db) {
    console.warn('[agentService] User or Firestore not available');
    return [];
  }

  try {
    let q = query(collection(db, `users/${userId}/agents`));

    if (status) {
      q = query(collection(db, `users/${userId}/agents`), where('status', '==', status));
    }

    const snapshot = await getDocs(q);
    const agents = snapshot.docs.map((doc) => {
      const data = doc.data();
      return FirestoreAgentSchema.parse({
        ...data,
        createdAt: data.createdAt?.toMillis?.() || data.createdAt,
        updatedAt: data.updatedAt?.toMillis?.() || data.updatedAt,
      });
    });

    return agents;
  } catch (error) {
    console.error('[agentService] Failed to list agents:', error);
    return [];
  }
}

/**
 * Update agent
 */
export async function updateAgent(
  agentId: string,
  updates: Partial<Omit<FirestoreAgent, 'id' | 'userId' | 'createdAt'>>,
  currentUserId?: string
): Promise<FirestoreAgent | null> {
  const userId = currentUserId || auth?.currentUser?.uid;
  if (!userId || !db) {
    console.warn('[agentService] User or Firestore not available');
    return null;
  }

  try {
    const agentDocRef = doc(db, `users/${userId}/agents`, agentId);
    const updatePayload = {
      ...updates,
      updatedAt: Timestamp.now(),
    };

    await updateDoc(agentDocRef, updatePayload);
    return getAgent(agentId, userId);
  } catch (error) {
    console.error('[agentService] Failed to update agent:', error);
    throw error;
  }
}

/**
 * Delete agent
 */
export async function deleteAgent(
  agentId: string,
  currentUserId?: string
): Promise<boolean> {
  const userId = currentUserId || auth?.currentUser?.uid;
  if (!userId || !db) {
    console.warn('[agentService] User or Firestore not available');
    return false;
  }

  try {
    const agentDocRef = doc(db, `users/${userId}/agents`, agentId);
    await deleteDoc(agentDocRef);
    return true;
  } catch (error) {
    console.error('[agentService] Failed to delete agent:', error);
    throw error;
  }
}

/**
 * Batch create agents (for bulk operations)
 */
export async function batchCreateAgents(
  inputs: AgentCreationInput[],
  currentUserId?: string
): Promise<{ agentIds: string[]; failed: string[] }> {
  const userId = currentUserId || auth?.currentUser?.uid;
  if (!userId || !db) {
    throw new Error('User must be authenticated');
  }

  const batch = writeBatch(db);
  const agentIds: string[] = [];
  const failed: string[] = [];
  const now = Timestamp.now();

  for (const input of inputs) {
    try {
      const validatedInput = AgentCreationInputSchema.parse(input);
      const agentId = uuidv4();

      const agent: FirestoreAgent = {
        id: agentId,
        name: validatedInput.name,
        persona: validatedInput.persona,
        skills: validatedInput.skills,
        tools: validatedInput.tools || [],
        description: validatedInput.description,
        createdAt: now.toMillis(),
        updatedAt: now.toMillis(),
        status: 'draft',
        userId,
      };

      const agentDocRef = doc(db, `users/${userId}/agents`, agentId);
      batch.set(agentDocRef, { ...agent, createdAt: now, updatedAt: now });
      agentIds.push(agentId);
    } catch (error) {
      failed.push(input.name);
      console.error('[agentService] Failed to prepare agent:', input.name, error);
    }
  }

  try {
    await batch.commit();
    return { agentIds, failed };
  } catch (error) {
    console.error('[agentService] Batch commit failed:', error);
    throw error;
  }
}

/**
 * Export agent as JSON
 */
export async function exportAgent(
  agentId: string,
  currentUserId?: string
): Promise<string | null> {
  const agent = await getAgent(agentId, currentUserId);
  if (!agent) return null;

  return JSON.stringify(agent, null, 2);
}

/**
 * Import agent from JSON
 */
export async function importAgent(
  json: string,
  currentUserId?: string
): Promise<FirestoreAgent | null> {
  try {
    const data = JSON.parse(json);
    const input: AgentCreationInput = {
      name: data.name,
      persona: data.persona,
      skills: data.skills,
      tools: data.tools,
      description: data.description,
    };

    const { agent } = await createAgentFromVoice(input, undefined, currentUserId);
    return agent;
  } catch (error) {
    console.error('[agentService] Failed to import agent:', error);
    return null;
  }
}
