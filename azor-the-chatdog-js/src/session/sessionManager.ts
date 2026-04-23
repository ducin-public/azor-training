/**
 * SessionManager - Orchestrates session lifecycle and manages active session
 */

import type { Assistant } from '../assistant/assistant.js';
import { ChatSession } from './chatSession.js';
import type {
  SessionSwitchResult,
  SessionCreateResult,
  SessionRemoveResult,
} from '../types/index.js';
import { removeSessionFile } from '../files/sessionFiles.js';

/**
 * SessionManager singleton class
 */
export class SessionManager {
  private currentSession?: ChatSession;
  private assistant: Assistant;

  constructor(assistant: Assistant) {
    this.assistant = assistant;
  }

  /**
   * Get the current active session
   */
  getCurrentSession(): ChatSession {
    if (!this.currentSession) {
      throw new Error('No active session. Call createNewSession() first.');
    }
    return this.currentSession;
  }

  /**
   * Check if there is an active session
   */
  hasActiveSession(): boolean {
    return !!this.currentSession;
  }

  /**
   * Create a new session
   */
  async createNewSession(saveCurrent: boolean = true): Promise<SessionCreateResult> {
    let saveAttempted = false;
    let previousId: string | undefined;
    let saveError: string | undefined;

    if (saveCurrent && this.currentSession) {
      saveAttempted = true;
      previousId = this.currentSession.id;

      const result = this.currentSession.saveToFile();
      if (!result.success) {
        saveError = result.error;
      }
    }

    const newSession = await ChatSession.create(this.assistant);
    this.currentSession = newSession;

    return {
      session: newSession,
      saveAttempted,
      previousId,
      saveError,
    };
  }

  /**
   * Switch to an existing session
   */
  async switchToSession(sessionId: string): Promise<SessionSwitchResult> {
    let saveAttempted = false;
    let previousId: string | undefined;

    if (this.currentSession) {
      saveAttempted = true;
      previousId = this.currentSession.id;

      const saveResult = this.currentSession.saveToFile();
      if (!saveResult.success) {
        console.error('Error saving current session:', saveResult.error);
      }
    }

    const loadResult = await ChatSession.loadFromFile(this.assistant, sessionId);

    if (!loadResult.success) {
      return {
        session: this.currentSession!,
        saveAttempted,
        previousId,
        loadSuccessful: false,
        error: loadResult.error,
        hasHistory: false,
      };
    }

    const newSession = loadResult.value;
    this.currentSession = newSession;

    return {
      session: newSession,
      saveAttempted,
      previousId,
      loadSuccessful: true,
      hasHistory: !newSession.isEmpty(),
    };
  }

  /**
   * Remove current session and create new one
   */
  async removeCurrentSessionAndCreateNew(): Promise<SessionRemoveResult> {
    if (!this.currentSession) {
      throw new Error('No active session to remove');
    }

    const removedId = this.currentSession.id;
    const removeResult = removeSessionFile(removedId);

    const newSession = await ChatSession.create(this.assistant);
    this.currentSession = newSession;

    return {
      session: newSession,
      removedId,
      success: removeResult.success,
      error: removeResult.success ? undefined : removeResult.error,
    };
  }

  /**
   * Initialize from CLI arguments
   */
  async initializeFromCLI(cliSessionId?: string): Promise<ChatSession> {
    if (cliSessionId) {
      const result = await ChatSession.loadFromFile(this.assistant, cliSessionId);

      if (result.success) {
        this.currentSession = result.value;
        return result.value;
      } else {
        console.error(`Error loading session ${cliSessionId}:`, result.error);
        console.log('Creating new session instead...');
      }
    }

    const session = await ChatSession.create(this.assistant);
    this.currentSession = session;
    return session;
  }

  /**
   * Cleanup and save on exit
   */
  cleanupAndSave(): void {
    if (this.currentSession) {
      const result = this.currentSession.saveToFile();
      if (!result.success) {
        console.error('Error saving session on exit:', result.error);
      }
    }
  }
}

// Singleton instance
let sessionManagerInstance: SessionManager | undefined;

/**
 * Get the session manager singleton
 */
export function getSessionManager(assistant?: Assistant): SessionManager {
  if (!sessionManagerInstance) {
    if (!assistant) {
      throw new Error('Assistant required for first initialization');
    }
    sessionManagerInstance = new SessionManager(assistant);
  }
  return sessionManagerInstance;
}
