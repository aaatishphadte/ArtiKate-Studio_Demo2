

from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

# Path to your local model or Hugging Face model name
MODEL_NAME = "gpt2"  # Replace with a bigger local model if you want

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

# Create a text-generation pipeline
generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

def generate_answer(prompt, max_length=200):
    """
    Generate answer for a prompt using local model.
    """
    output = generator(prompt, max_length=max_length, do_sample=True, top_p=0.9, temperature=0.7)
    return output[0]["generated_text"]
