const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('[v0] Starting comprehensive npm rebuild...');

const portalDir = path.join(__dirname, '../apps/portal');

// Step 1: Remove corrupted lock file
const lockFile = path.join(portalDir, 'package-lock.json');
if (fs.existsSync(lockFile)) {
    console.log('[v0] Removing corrupted package-lock.json...');
    fs.unlinkSync(lockFile);
}

// Step 2: Remove node_modules
const nodeModulesDir = path.join(portalDir, 'node_modules');
if (fs.existsSync(nodeModulesDir)) {
    console.log('[v0] Removing node_modules directory...');
    execSync('rm -rf node_modules', { cwd: portalDir, stdio: 'inherit' });
}

// Step 3: Clear npm cache
console.log('[v0] Clearing npm cache...');
try {
    execSync('npm cache clean --force', { cwd: portalDir, stdio: 'inherit' });
} catch (err) {
    console.warn('[v0] Cache clean had issues, continuing...');
}

// Step 4: Run npm install with legacy peer deps
console.log('[v0] Installing all dependencies...');
try {
    execSync('npm install --legacy-peer-deps', { cwd: portalDir, stdio: 'inherit' });
    console.log('[v0] SUCCESS: Dependencies installed');
} catch (err) {
    console.error('[v0] Installation failed:', err.message);
    process.exit(1);
}

console.log('[v0] Rebuild complete!');
