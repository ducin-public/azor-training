/**
 * Session list command (matches Python version)
 */

import { listSessions } from '../files/sessionFiles.js';
import { printHelp } from '../cli/console.js';

/**
 * Display list of all sessions
 */
export function displaySessionList(): void {
  const sessions = listSessions();

  if (sessions.length === 0) {
    printHelp('\nNo saved sessions.');
    return;
  }

  printHelp('\n--- Saved sessions (ID) ---');
  for (const session of sessions) {
    printHelp(
      `- ID: ${session.session_id}`
    );
    printHelp(
      `  Messages: ${session.message_count}, Last activity: ${session.last_modified.toLocaleString()}`
    );
  }
  printHelp('------------------------------------');
}
