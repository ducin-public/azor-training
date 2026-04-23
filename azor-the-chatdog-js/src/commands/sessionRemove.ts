/**
 * Session remove command
 */

import { printSuccess, printError } from '../cli/console.js';
import type { SessionManager } from '../session/sessionManager.js';

/**
 * Remove current session and create a new one
 */
export async function removeCurrentSession(manager: SessionManager): Promise<void> {
  const result = await manager.removeCurrentSessionAndCreateNew();

  if (result.success) {
    printSuccess(`Session ${result.removedId} removed. Created new session.`);
  } else {
    printError(`Error removing session: ${result.error}`);
    printSuccess('Created new session anyway.');
  }
}
