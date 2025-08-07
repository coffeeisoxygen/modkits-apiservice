#!/usr/bin/env python3
"""Test script untuk menjalankan FastAPI server dan test endpoints."""

import asyncio
import aiohttp
import time
import json


async def test_endpoints():
    """Test endpoints dengan sensitive data."""

    base_url = "http://localhost:8000"

    # Test cases
    test_cases = [
        {
            "endpoint": "/test-sensitive",
            "method": "GET",
            "description": "Test sensitive data endpoint",
        },
        {
            "endpoint": "/login",
            "method": "POST",
            "data": {
                "email": "admin@company.com",
                "password": "super_secret_password_123",
                "token": "sk-1234567890abcdef1234567890",
            },
            "description": "Test login with sensitive data",
        },
        {"endpoint": "/info", "method": "GET", "description": "Test normal endpoint"},
    ]

    print("🌐 Testing FastAPI endpoints...")

    async with aiohttp.ClientSession() as session:
        for i, test_case in enumerate(test_cases, 1):
            try:
                print(f"\n📡 Test {i}: {test_case['description']}")

                if test_case["method"] == "POST":
                    async with session.post(
                        f"{base_url}{test_case['endpoint']}",
                        json=test_case.get("data", {}),
                    ) as response:
                        result = await response.text()
                        print(f"   Status: {response.status}")
                        print(f"   Response: {result[:100]}...")

                else:  # GET
                    async with session.get(
                        f"{base_url}{test_case['endpoint']}"
                    ) as response:
                        result = await response.text()
                        print(f"   Status: {response.status}")
                        print(f"   Response: {result[:100]}...")

            except Exception as e:
                print(f"   ❌ Error: {e}")

            # Small delay between requests
            await asyncio.sleep(0.5)


def main():
    """Main function."""
    print("🚀 FastAPI Sensitive Data Test")
    print("=" * 50)

    print("\n📋 Instructions:")
    print("1. Buka terminal lain dan jalankan:")
    print("   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("2. Tunggu server start (sekitar 3-5 detik)")
    print("3. Press Enter untuk lanjut test...")

    input()

    # Run async test
    asyncio.run(test_endpoints())

    print("\n✅ Test completed!")
    print("📊 Check server logs untuk melihat sensitive data redaction!")


if __name__ == "__main__":
    main()
