/**
 * Session display command (matches Python version)
 */

import type { ChatSession } from '../session/chatSession.js';
import { printInfo, printUser, printAssistant } from '../cli/console.js';

/**
 * Display the full conversation history of current session
 */
export function displaySessionHistory(session: ChatSession): void {
  const history = session.getHistory();

  if (history.length === 0) {
    printInfo('Session history is empty.');
    return;
  }

  printInfo(
    `\n--- FULL SESSION HISTORY (${session.id}, ${history.length} message(s)) ---`
  );

  for (let i = 0; i < history.length; i++) {
    const msg = history[i];
    const role = msg.role;
    const displayRole = role === 'user' ? 'YOU' : session.assistantName;
    const text = msg.parts[0]?.text || '';

    // Display with appropriate function based on role
    if (role === 'user') {
      printUser(`\n[${i + 1}] ${displayRole}:`);
      printUser(text);
    } else {
      printAssistant(`\n[${i + 1}] ${displayRole}:`);
      printAssistant(text);
    }
  }

  printInfo('--------------------------------------------------------');
}
