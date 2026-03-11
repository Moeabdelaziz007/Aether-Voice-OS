import { test, expect } from '@playwright/test';

test.describe('Aether Portal E2E', () => {
    test('should navigate from landing to dashboard', async ({ page }) => {
        // 1. Visit the landing page
        await page.goto('/');
        
        // Check if GemiGram title is visible
        await expect(page.getByRole('heading', { name: /GEMIGRAM/i })).toBeVisible();

        // 2. Click enter interface button
        // Based on the code: <span className="relative z-10 flex items-center gap-6 text-sm font-black text-white uppercase tracking-[0.25em]">Enter_Interface_Node...</span>
        const enterButton = page.getByRole('button', { name: /Enter_Interface_Node/i });
        await expect(enterButton).toBeVisible();
        await enterButton.click();

        // 3. Verify transition to Portal / Dashboard
        // SoulSwapAnimation takes about 800-1500ms
        // Wait for the Dashboard widget grid or sidebar
        await expect(page.getByRole('complementary')).toBeVisible({ timeout: 10000 }); // Sidebar is <motion.aside> which usually maps to complementary
        
        // Verify we are on the dashboard panel by checking for the 'Dashboard' nav item state or content
        await expect(page.getByText(/System_Status/i)).not.toBeVisible(); // Landing status should be gone
    });

    test('should open settings from sidebar', async ({ page }) => {
        await page.goto('/');
        await page.getByRole('button', { name: /Enter_Interface_Node/i }).click();

        // Wait for sidebar
        const sidebar = page.getByRole('complementary');
        await expect(sidebar).toBeVisible();

        // Click settings button in sidebar
        // It has title="Settings"
        const settingsBtn = page.getByTitle('Settings');
        await expect(settingsBtn).toBeVisible();
        await settingsBtn.click();

        // Verify settings hub appears
        // Assuming settings hub has some identifiable text or role
        await expect(page.getByText(/Preferences/i).or(page.getByText(/Settings/i))).toBeVisible();
    });

    test('should switch between realms/panels', async ({ page }) => {
        await page.goto('/');
        await page.getByRole('button', { name: /Enter_Interface_Node/i }).click();

        // Wait for sidebar
        await expect(page.getByRole('complementary')).toBeVisible();

        // Click on Agent Hub
        await page.getByTitle('Agent Hub').click();
        
        // Verify Agent Hub content
        // AgentHub component likely has some unique text
        await expect(page.getByText(/FORGE/i).or(page.getByText(/HUMAN/i))).toBeVisible();

        // Click on Persona
        await page.getByTitle('Persona').click();
        
        // Verify Persona panel
        await expect(page.getByText(/IDENTITY/i).or(page.getByText(/DNA/i))).toBeVisible();
    });
});
