import { test, expect } from '@playwright/test';



test("has title live", async ({ page }) => {
    await page.goto("127.0.0.1:5000/");
    await expect(page).toHaveTitle("Cinema Ticket Booking");
});