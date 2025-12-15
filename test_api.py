import asyncio
import aiohttp
import json
import re

async def test_api():
    vehicle_number = "UP72H6726"
    
    # Create session with cookies enabled
    connector = aiohttp.TCPConnector()
    async with aiohttp.ClientSession(connector=connector, cookie_jar=aiohttp.CookieJar()) as session:
        # Test direct URL with &i=1
        print("=== Testing direct URL with &i=1 ===")
        direct_url = f"http://india.42web.io/vehicle/?q={vehicle_number}&i=1"
        try:
            async with session.get(direct_url, timeout=15) as response:
                print(f"Status: {response.status}")
                print(f"Content-Type: {response.headers.get('Content-Type')}")
                text = await response.text()
                print(f"Response length: {len(text)}")
                print(f"First 1000 chars:\n{text[:1000]}\n")
                
                # Try to parse as JSON
                try:
                    data = await response.json()
                    print("✓ Successfully parsed as JSON!")
                    print(json.dumps(data, indent=2)[:500])
                except Exception as e:
                    print(f"✗ JSON parse error: {e}")
                    # Try to extract JSON
                    json_match = re.search(r'\{[\s\S]*\}', text)
                    if json_match:
                        print("Found JSON-like structure in response")
                        json_str = json_match.group(0)
                        print(f"JSON string length: {len(json_str)}")
                        print(f"First 500 chars of JSON: {json_str[:500]}")
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n=== Testing with redirect chain ===")
        base_url = f"http://india.42web.io/vehicle/?q={vehicle_number}"
        
        # Follow redirect chain
        current_url = base_url
        max_redirects = 5
        
        for i in range(max_redirects):
            try:
                async with session.get(current_url, timeout=15, allow_redirects=False) as response:
                    text = await response.text()
                    print(f"\nStep {i+1}: {current_url}")
                    print(f"Status: {response.status}")
                    print(f"Response length: {len(text)}")
                    
                    # Check if it's JSON
                    if text.strip().startswith('{'):
                        print("✓ Found JSON response!")
                        try:
                            data = json.loads(text)
                            print("✓ Successfully parsed as JSON!")
                            print(json.dumps(data, indent=2))
                            break
                        except Exception as e:
                            print(f"✗ JSON parse error: {e}")
                            print(f"First 500 chars: {text[:500]}")
                    
                    # Check for redirect
                    redirect_match = re.search(r'location\.href="([^"]+)"', text)
                    if redirect_match:
                        current_url = redirect_match.group(1)
                        print(f"Redirecting to: {current_url}")
                    else:
                        print("No more redirects found")
                        print(f"First 500 chars: {text[:500]}")
                        break
            except Exception as e:
                print(f"Error at step {i+1}: {e}")
                break
        
        print("\n=== Testing direct &i=2 (final redirect) ===")
        final_url = f"http://india.42web.io/vehicle/?q={vehicle_number}&i=2"
        try:
            async with session.get(final_url, timeout=15) as response:
                print(f"Status: {response.status}")
                print(f"Content-Type: {response.headers.get('Content-Type')}")
                text = await response.text()
                print(f"Response length: {len(text)}")
                if text.strip().startswith('{'):
                    print("✓ Response is JSON!")
                    try:
                        data = json.loads(text)
                        print("✓ Successfully parsed!")
                        print(json.dumps(data, indent=2))
                    except Exception as e:
                        print(f"✗ Parse error: {e}")
                        print(f"First 1000 chars: {text[:1000]}")
                else:
                    print(f"First 1000 chars: {text[:1000]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())

