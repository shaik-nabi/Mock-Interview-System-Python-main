import ollama
import sys

print("Testing Ollama integration...")

try:
    # List available models
    models_response = ollama.list()
    print("Available models:", models_response)
    
    # Try a simple generation
    print("\nAttempting generation with 'llama3'...")
    response = ollama.chat(model='llama3', messages=[
        {
            'role': 'user',
            'content': 'Say "Hello, World!"',
        },
    ])
    print("\nSuccess! Response:")
    print(response['message']['content'])
    
except Exception as e:
    print(f"\nError: {e}")
    print("\nTroubleshooting tips:")
    print("1. Is Ollama running? (Run 'ollama serve' in a separate terminal)")
    print("2. Is the 'llama3' model pulled? (Run 'ollama pull llama3')")
    sys.exit(1)
