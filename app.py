import gradio as gr
import os
import subprocess
import threading
import sys

# Aurora ASR: Gradio Dashboard for Hugging Face Spaces

def run_aurora_repair(api_key):
    # Set the API key in the environment for the sub-process
    env = os.environ.copy()
    if api_key:
        env["OPENAI_API_KEY"] = api_key
    else:
        env["OPENAI_API_KEY"] = "mock" # Default to mock mode for demo
    
    # Run the inference script and capture output in real-time
    process = subprocess.Popen(
        [sys.executable, "inference.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env
    )
    
    partial_output = ""
    for line in iter(process.stdout.readline, ""):
        partial_output += line
        yield partial_output
    
    process.stdout.close()
    process.wait()

# UI Design
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🚀 Aurora ASR: Self-Healing CI/CD Agent
    **Autonomous Software Repair for OpenEnv-v4!**
    
    This agent identifies bugs in provided tasks (Easy, Medium, Hard) and repairs them in isolated sandboxes.
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            key_input = gr.Textbox(
                label="OpenAI API Key (Optional)", 
                placeholder="sk-...", 
                type="password",
                info="If left empty, the agent runs in 'Mock Mode' for demonstration."
            )
            run_btn = gr.Button("🔥 Start Repair Pipeline", variant="primary")
            
        with gr.Column(scale=2):
            output_log = gr.Textbox(
                label="Repair Logs (Real-time)", 
                lines=25, 
                max_lines=30,
                autoscroll=True
            )

    run_btn.click(fn=run_aurora_repair, inputs=[key_input], outputs=[output_log])
    
    gr.Markdown("""
    ### 🛡️ OpenEnv-v4 Compliance
    This Space follows the strict **OpenEnv-v4 metadata and logging standards**.
    Key logs to watch for: `[START]`, `[STEP]`, `[END]`.
    """)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
