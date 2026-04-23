/**
 * Terminal output utilities
 * Color scheme matches Python version using colorama
 */

import chalk from 'chalk';

/**
 * Print error message in red (Fore.RED)
 */
export function printError(message: string): void {
  console.log(chalk.red(message));
}

/**
 * Print success message in green
 */
export function printSuccess(message: string): void {
  console.log(chalk.green(message));
}

/**
 * Print info message in default color (no color in Python version)
 */
export function printInfo(message: string): void {
  console.log(message);
}

/**
 * Print help message in yellow (Fore.YELLOW)
 */
export function printHelp(message: string): void {
  console.log(chalk.yellow(message));
}

/**
 * Print warning message in yellow
 */
export function printWarning(message: string): void {
  console.log(chalk.yellow(message));
}

/**
 * Print assistant message in cyan (Fore.CYAN)
 */
export function printAssistant(message: string): void {
  console.log(chalk.cyan(message));
}

/**
 * Print user message in blue (Fore.BLUE)
 */
export function printUser(message: string): void {
  console.log(chalk.blue(message));
}

/**
 * Display help information (matches Python version)
 */
export function displayHelp(sessionId?: string): void {
  if (sessionId) {
    printInfo(`Current session (ID): ${sessionId}`);
  }
  printHelp('Available commands (slash commands):');
  printHelp('  /switch <ID>      - Switch to an existing session.');
  printHelp('  /help             - Show this help.');
  printHelp('  /exit, /quit      - End the chat.');
  printHelp('\n  /session list     - List saved sessions.');
  printHelp('  /session display  - Show full session history.');
  printHelp('  /session pop      - Remove the last user/assistant message pair.');
  printHelp('  /session clear    - Clear the current session history.');
  printHelp('  /session new      - Start a new session.');
}

/**
 * Print a separator line
 */
export function printSeparator(): void {
  console.log(chalk.gray('─'.repeat(60)));
}

/**
 * Clear the console
 */
export function clearConsole(): void {
  console.clear();
}
