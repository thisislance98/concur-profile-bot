#!/usr/bin/env python3
"""
Script to inspect browser session and extract OAuth app information
"""

import asyncio
from playwright.async_api import async_playwright

async def inspect_browser_session():
    async with async_playwright() as p:
        # Connect to existing browser session if possible
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Navigate to the integration environment
        await page.goto("https://integration.concursolutions.com/home")
        await page.wait_for_load_state('networkidle')
        
        # Check local storage for any OAuth info
        local_storage = await page.evaluate("() => { return localStorage; }")
        print("Local Storage:")
        print(local_storage)
        
        # Check session storage
        session_storage = await page.evaluate("() => { return sessionStorage; }")
        print("\nSession Storage:")
        print(session_storage)
        
        # Check cookies
        cookies = await context.cookies()
        print("\nCookies:")
        for cookie in cookies:
            if 'oauth' in cookie['name'].lower() or 'client' in cookie['name'].lower() or 'app' in cookie['name'].lower():
                print(f"  {cookie['name']}: {cookie['value']}")
        
        # Check for any JavaScript variables
        js_vars = await page.evaluate("""
            () => {
                const result = {};
                for (let key in window) {
                    if (typeof window[key] === 'string' && 
                        (key.toLowerCase().includes('client') || 
                         key.toLowerCase().includes('oauth') ||
                         key.toLowerCase().includes('app'))) {
                        result[key] = window[key];
                    }
                }
                return result;
            }
        """)
        
        print("\nJavaScript Variables:")
        print(js_vars)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_browser_session()) 