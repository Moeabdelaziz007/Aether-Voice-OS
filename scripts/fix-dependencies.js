#!/usr/bin/env node
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const portalDir = path.join(__dirname, '../apps/portal');

console.log('[v0] Starting dependency sync...');
console.log('[v0] Portal directory:', portalDir);

try {
  console.log('[v0] Current Node version:', execSync('node --version').toString().trim());
  console.log('[v0] Current npm version:', execSync('npm --version').toString().trim());

  console.log('[v0] Installing dependencies with --legacy-peer-deps...');
  execSync('npm install --legacy-peer-deps', {
    cwd: portalDir,
    stdio: 'inherit',
    shell: true
  });

  console.log('[v0] Checking firebase installation...');
  const output = execSync('npm list firebase', {
    cwd: portalDir,
    encoding: 'utf-8'
  });
  console.log('[v0] Firebase check result:', output);

  console.log('[v0] SUCCESS: All dependencies synced!');
  process.exit(0);
} catch (error) {
  console.error('[v0] ERROR during dependency sync:', error.message);
  process.exit(1);
}
