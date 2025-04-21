import subprocess
import json
import os
import config

class LocalLLMClient:
    """Interface for local LLM interactions using llama.cpp"""
    
    def __init__(self, model_path=None, model_type="phi"):
        self.model_path = model_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "models",
            "phi-2.Q4_K_M.gguf"
        )
        self.llama_cpp_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "llama.cpp"
        )
        self.model_type = model_type
        
        # Validate model path
        if not os.path.exists(self.model_path):
            print(f"Warning: Model not found at {self.model_path}")
    
    def generate_recommendation(self, prompt):
        """Generate recommendations using the local LLM"""
        formatted_prompt = self._format_prompt_for_model(prompt)
        
        try:
            # Call llama.cpp with the prompt
            
            cmd = [
                f"{self.llama_cpp_path}/build/bin/llama-cli",  # Using main which is the standard binary name
                "-m", self.model_path,
                "-n", "2048",  # Output token limit
                "--temp", "0.7",
                "--ctx-size", "4500",  # Reduced context window size
                "-b", "512",    # Smaller batch size
                "-p", formatted_prompt
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
                    # If GPU memory error, fall back to CPU
            if result.returncode != 0 and "Insufficient Memory" in result.stderr:
                print("GPU memory insufficient, falling back to CPU...")
                cmd.append("--n-gpu-layers")
                cmd.append("0")  # Use CPU only
                result = subprocess.run(cmd, capture_output=True, text=True)
            
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            

            if result.returncode != 0:
                print(f"LLM subprocess failed with return code {result.returncode}")
                return f"Error running LLM subprocess:\n{result.stderr}"
           
            # Extract output from the model response
            output = result.stdout
            
            # Remove the prompt from the output to get just the response
            if output and formatted_prompt in output:
                output = output.split(formatted_prompt)[1].strip()
                                
            return output
            
        except Exception as e:
            print(f"Error generating recommendations with local LLM: {e}")
            return "Error generating recommendations. Please check your local LLM setup."
    
    def _format_prompt_for_model(self, prompt):
        """Format prompt based on the model type"""
        if self.model_type == "phi":
            # Mistral Instruct format
            formatted_prompt = f"""<s>[INST] You are Bob, a whisky expert who specializes in personalized recommendations. 

{prompt} [/INST]</s>"""
            
        elif self.model_type == "llama":
            # Llama-2-Chat format
            formatted_prompt = f"""<s>[INST] <<SYS>>
You are Bob, a whisky expert who specializes in personalized recommendations.
<</SYS>>

{prompt} [/INST]"""
            
        else:
            # Generic format (fallback)
            formatted_prompt = f"""### System:
You are Bob, a whisky expert who specializes in personalized recommendations.

### User:
{prompt}

### Assistant:
"""
            
        return formatted_prompt
