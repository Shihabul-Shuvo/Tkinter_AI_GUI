try:
    import tkinter
    print("✅ tkinter")
except ImportError as e:
    print(f"❌ tkinter: {e}")

try:
    import PIL
    print("✅ pillow")
except ImportError as e:
    print(f"❌ pillow: {e}")

try:
    import transformers
    print("✅ transformers")
except ImportError as e:
    print(f"❌ transformers: {e}")

try:
    import huggingface_hub
    print("✅ huggingface_hub")
except ImportError as e:
    print(f"❌ huggingface_hub: {e}")

try:
    import torch
    print("✅ torch")
except ImportError as e:
    print(f"❌ torch: {e}")

try:
    import pyperclip
    print("✅ pyperclip")
except ImportError as e:
    print(f"❌ pyperclip: {e}")

try:
    import tkinterdnd2
    print("✅ tkinterdnd2")
except ImportError as e:
    print(f"❌ tkinterdnd2: {e}")

try:
    import ttkbootstrap
    print("✅ ttkbootstrap")
except ImportError as e:
    print(f"❌ ttkbootstrap: {e}")

print("\nAll packages verified!")