#!/usr/bin/env python3
"""
Test OpenRouter free models availability and performance.

Usage:
    python test_openrouter_free.py [--api-key KEY] [--models MODEL1 MODEL2 ...]

Examples:
    python test_openrouter_free.py
    python test_openrouter_free.py --api-key sk-or-v1-xxx
    python test_openrouter_free.py --models deepseek/deepseek-v4-flash:free baidu/cobuddy:free
"""

import argparse
import json
import sys
import os
from datetime import datetime

try:
    import requests
except ImportError:
    print("Error: requests library required. Install with: pip install requests")
    sys.exit(1)


def get_api_key(args_api_key=None):
    """Get API key from args or environment."""
    if args_api_key:
        return args_api_key
    return os.environ.get('OPENROUTER_API_KEY', '').strip()


def list_free_models(api_key):
    """List all available free models from OpenRouter."""
    print("\n=== Fetching Free Models ===\n")
    
    response = requests.get(
        "https://openrouter.ai/api/v1/models",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch models: HTTP {response.status_code}")
        return []
    
    data = response.json()
    models = data.get('data', [])
    free_models = [m for m in models if m.get('id', '').endswith(':free')]
    
    print(f"Total models: {len(models)}")
    print(f"Free models (:free suffix): {len(free_models)}")
    
    return free_models


def test_model(api_key, model_id, test_message="Hello, test response.", max_tokens=50):
    """Test a single model with a simple prompt."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://hermes-agent.local",
        "X-Title": "Hermes Agent"
    }
    
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": test_message}],
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=20
        )
        
        result = {
            "model": model_id,
            "status_code": response.status_code,
            "success": False,
            "error": None,
            "response_preview": None,
            "tokens_used": None
        }
        
        if response.status_code == 200:
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                result['success'] = True
                result['response_preview'] = data['choices'][0]['message']['content'][:100]
                result['tokens_used'] = data.get('usage', {}).get('total_tokens', 'N/A')
            else:
                result['error'] = "No choices in response"
        elif response.status_code == 429:
            result['error'] = "Rate Limited (429)"
        elif response.status_code == 404:
            result['error'] = "Privacy/Guardrail Restricted (404)"
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            result['error'] = error_data.get('error', {}).get('message', f"HTTP {response.status_code}")
            
    except requests.exceptions.Timeout:
        result['error'] = "Timeout"
    except requests.exceptions.RequestException as e:
        result['error'] = f"Request error: {str(e)[:100]}"
    except Exception as e:
        result['error'] = f"Error: {str(e)[:100]}"
    
    return result


def main():
    parser = argparse.ArgumentParser(description='Test OpenRouter free models')
    parser.add_argument('--api-key', help='OpenRouter API key')
    parser.add_argument('--models', nargs='+', help='Specific models to test')
    parser.add_argument('--max-models', type=int, default=10, help='Max models to test')
    args = parser.parse_args()
    
    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: No API key provided. Use --api-key or set OPENROUTER_API_KEY env var")
        sys.exit(1)
    
    print(f"API Key: {api_key[:12]}...{api_key[-4:]}")
    print(f"Test time: {datetime.now().isoformat()}")
    
    # Get list of free models
    all_free_models = list_free_models(api_key)
    
    if not all_free_models:
        print("No free models found!")
        sys.exit(1)
    
    # Select models to test
    if args.models:
        models_to_test = args.models
    else:
        # Default: test first 10 free models + router
        models_to_test = [m['id'] for m in all_free_models[:10]]
        # Always include the router
        if 'openrouter/free' not in models_to_test:
            models_to_test.append('openrouter/free')
    
    models_to_test = models_to_test[:args.max_models]
    
    # Test each model
    results = []
    for model_id in models_to_test:
        print(f"\nTesting: {model_id}")
        result = test_model(api_key, model_id)
        results.append(result)
        
        if result['success']:
            print(f"  ✅ Success: {result['response_preview']}...")
            print(f"  Tokens: {result['tokens_used']}")
        elif result['error']:
            print(f"  ❌ {result['error']}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    working = [r for r in results if r['success']]
    rate_limited = [r for r in results if r['error'] and 'Rate Limited' in r['error']]
    privacy_restricted = [r for r in results if r['error'] and 'Privacy' in r['error']]
    other_errors = [r for r in results if r['error'] and 'Rate Limited' not in r['error'] and 'Privacy' not in r['error']]
    
    print(f"\n✅ Working ({len(working)}):")
    for r in working:
        print(f"   {r['model']}")
    
    if rate_limited:
        print(f"\n⚠️ Rate Limited ({len(rate_limited)}):")
        for r in rate_limited:
            print(f"   {r['model']}")
    
    if privacy_restricted:
        print(f"\n❌ Privacy/Guardrail ({len(privacy_restricted)}):")
        for r in privacy_restricted:
            print(f"   {r['model']}")
    
    if other_errors:
        print(f"\n⚠️ Other Errors ({len(other_errors)}):")
        for r in other_errors:
            print(f"   {r['model']}: {r['error']}")
    
    # Save results
    output_file = f"openrouter_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "api_key_prefix": api_key[:12],
            "total_free_models": len(all_free_models),
            "tested": len(results),
            "results": results
        }, f, indent=2)
    print(f"\n📄 Results saved to: {output_file}")


if __name__ == '__main__':
    main()
