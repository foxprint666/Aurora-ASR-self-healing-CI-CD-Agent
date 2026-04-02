import gradio as gr
import os
import subprocess
import threading
import sys
import zipfile
import shutil
import time

# Aurora ASR: Gradio Dashboard for Hugging Face Spaces

def run_aurora_repair(api_key, task_type, uploaded_zip=None):
    # Set the API key in the environment for the sub-process
    env = os.environ.copy()
    if api_key:
        env["OPENAI_API_KEY"] = api_key
    else:
        env["OPENAI_API_KEY"] = "mock" 
    
    cmd = [sys.executable, "inference.py"]
    
    terminal_output = ""
    env_output = ""
    
    # Handle Custom Upload
    temp_dir = None
    if task_type == "Custom Upload" and uploaded_zip is not None:
        try:
            # Create a unique temp directory for this upload
            temp_dir = os.path.abspath(f"tasks/uploads/upload_{int(time.time())}")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Extract ZIP
            with zipfile.ZipFile(uploaded_zip.name, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            cmd.extend(["--task_id", "custom_upload", "--repo_path", temp_dir])
            terminal_output = f"📂 Extracted custom code to: {temp_dir}\n"
            yield terminal_output, ""
        except Exception as e:
            yield f"❌ Error extracting file: {str(e)}\n", ""
            return
    
    # Run the inference script and capture output in real-time
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env
    )
    
    for line in iter(process.stdout.readline, ""):
        if line.startswith(">>>"):
            env_output += line
        else:
            terminal_output += line
        yield terminal_output, env_output
    
    process.stdout.close()
    process.wait()
    
    # Cleanup temp directory if created
    if temp_dir and os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        terminal_output += f"\n🧹 Cleaned up temporary directory: {temp_dir}"
        yield terminal_output, env_output

# UI Design
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🚀 Aurora ASR: Self-Healing CI/CD Agent
    **Autonomous Software Repair for OpenEnv-v4!**
    
    This agent identifies bugs and repairs them in isolated sandboxes.
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            key_input = gr.Textbox(
                label="API Key (Optional)", 
                placeholder="sk-...", 
                type="password",
                info="If left empty, the agent runs in 'Mock Mode' for benchmark tasks."
            )
            
            task_selector = gr.Radio(
                choices=["Benchmark Suite", "Custom Upload"],
                value="Benchmark Suite",
                label="Repair Target"
            )
            
            file_upload = gr.File(
                label="Upload Buggy Code (.zip)",
                file_types=[".zip"],
                visible=False
            )
            
            run_btn = gr.Button("🔥 Start Repair Pipeline", variant="primary")
            
        with gr.Column(scale=2):
            terminal_log = gr.Textbox(
                label="💻 Background AI Terminal", 
                lines=12, 
                max_lines=15,
                autoscroll=True
            )
            output_log = gr.Textbox(
                label="🛡️ OpenEnv-v4 Grader Logs", 
                lines=12, 
                max_lines=15,
                autoscroll=True
            )

    # Visibility Toggle for File Upload
    def toggle_upload(choice):
        return gr.update(visible=(choice == "Custom Upload"))
    
    task_selector.change(fn=toggle_upload, inputs=[task_selector], outputs=[file_upload])

    run_btn.click(
        fn=run_aurora_repair, 
        inputs=[key_input, task_selector, file_upload], 
        outputs=[terminal_log, output_log]
    )
    
    gr.Markdown("""
    ### 🛡️ OpenEnv-v4 Compliance
    This Space follows the strict **OpenEnv-v4 metadata and logging standards**.
    Key logs to watch for: `[START]`, `[STEP]`, `[END]`.
    """)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
