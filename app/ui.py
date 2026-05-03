"""UI Module - Gradio interface for the chatbot"""

import os
import gradio as gr
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
from app.agent import PDFAgent


class ChatbotUI:
    """Gradio-based UI for the PDF conversational agent"""
    
    def __init__(self):
        """Initialize chatbot UI components"""
        load_dotenv()
        hf_api_token = os.getenv("HF_API_TOKEN")
        
        if not hf_api_token:
            raise ValueError("HF_API_TOKEN not found in environment variables")
        
        self.agent = PDFAgent(hf_api_token)
        self.pdf_filename = None
        self.chunk_count = 0
        self.page_count = 0
    
    def load_pdf(self, pdf_file) -> tuple:
        """
        Load a PDF file and build retrieval index
        
        Args:
            pdf_file: Uploaded PDF file (can be path string or FileData object)
            
        Returns:
            Tuple of (status_message, pdf_info_text)
        """
        try:
            if pdf_file is None:
                return "✗ No file selected", ""
            
            # Handle both file path strings and FileData objects from Gradio
            if hasattr(pdf_file, 'name'):
                # FileData object from Gradio 6.x
                pdf_path = Path(pdf_file.name)
                file_to_load = pdf_file.name
            else:
                # String path from older Gradio versions
                pdf_path = Path(pdf_file)
                file_to_load = pdf_file
            
            self.pdf_filename = pdf_path.name
            
            # Load PDF with agent
            status = self.agent.load_pdf(file_to_load)
            
            if not status.startswith("✓"):
                return status, ""
            
            # Extract chunk count from status message
            status_parts = status.split()
            chunk_count_idx = status_parts.index("chunks") - 1
            self.chunk_count = int(status_parts[chunk_count_idx])
            
            # Estimate page count from chunks (approximate based on PDF structure)
            # Each page roughly creates ~3-5 chunks depending on content
            self.page_count = max(1, self.chunk_count // 3)
            
            # Build PDF info text
            pdf_info = f"""
**PDF Loaded Successfully!**

📄 **File:** {self.pdf_filename}
📖 **Estimated Pages:** {self.page_count}
📝 **Chunks Indexed:** {self.chunk_count}

Ready to answer questions about your document.
            """.strip()
            
            status_msg = f"✓ PDF loaded: {self.pdf_filename}, {self.chunk_count} chunks indexed"
            
            return status_msg, pdf_info
        
        except Exception as e:
            error_msg = f"✗ Error loading PDF: {str(e)}"
            return error_msg, ""
    
    def chat_with_agent(self, message: str, chat_history: list) -> tuple:
        """
        Process user message and generate response via agent
        
        Args:
            message: User message
            chat_history: Previous chat history (list of dicts with 'role' and 'content')
            
        Returns:
            Tuple of (updated_chat_history, empty_message_for_clearing_input)
        """
        if not self.pdf_filename:
            # Append to history in Gradio 6.x format
            chat_history.append({"role": "user", "content": message})
            chat_history.append({"role": "assistant", "content": "Please upload a PDF first."})
            return chat_history, ""
        
        if not message or message.strip() == "":
            return chat_history, ""
        
        try:
            response = self.agent.chat(message, chat_history)
            # Append in Gradio 6.x format
            chat_history.append({"role": "user", "content": message})
            chat_history.append({"role": "assistant", "content": response})
            return chat_history, ""
        
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            chat_history.append({"role": "user", "content": message})
            chat_history.append({"role": "assistant", "content": error_msg})
            return chat_history, ""
    
    def create_interface(self) -> gr.Blocks:
        """Create and return Gradio interface"""
        
        with gr.Blocks(title="PDF Conversational Agent") as demo:
            gr.Markdown("# 📄 PDF Conversational Agent")
            gr.Markdown("Intelligently search and understand your PDFs with AI-powered answers")
            
            with gr.Row():
                # Main content area
                with gr.Column(scale=3):
                    # How to use section
                    with gr.Accordion("ℹ️ How to Use", open=False):
                        gr.Markdown("""
1. **Upload PDF**: Click the upload button and select a PDF file from your computer
2. **Wait for Processing**: The system will extract text and create searchable chunks
3. **Ask Questions**: Type your questions about the PDF content in the chat
4. **Get Cited Answers**: The AI will provide answers with page references [Page X]

**Tips:**
- Ask specific questions for best results
- The AI only uses information from your PDF
- Questions outside the document scope will be politely declined
- Conversation history is maintained for follow-up questions
                        """)
                    
                    # PDF upload section
                    gr.Markdown("### 📥 Upload Your PDF")
                    pdf_upload = gr.File(
                        label="Select PDF File",
                        file_types=[".pdf"],
                        file_count="single"
                    )
                    upload_button = gr.Button("🚀 Load PDF", variant="primary", scale=2)
                    upload_status = gr.Markdown("*No PDF loaded yet*")
                    
                    # Chat interface
                    gr.Markdown("### 💬 Chat with Your PDF")
                    chatbot = gr.Chatbot(
                        label="Document Q&A",
                        height=400
                    )
                    
                    with gr.Row():
                        msg = gr.Textbox(
                            label="Your question",
                            placeholder="Ask a question about your PDF...",
                            scale=4
                        )
                        submit_btn = gr.Button("Send", scale=1, variant="primary")
                
                # Sidebar with PDF info
                with gr.Column(scale=1):
                    gr.Markdown("### 📋 PDF Information")
                    pdf_info_display = gr.Markdown(
                        "**No PDF loaded**\n\n" +
                        "Upload a PDF to see:\n" +
                        "- File name\n" +
                        "- Page count\n" +
                        "- Indexed chunks"
                    )
            
            # Event handlers
            upload_button.click(
                fn=self.load_pdf,
                inputs=pdf_upload,
                outputs=[upload_status, pdf_info_display]
            )
            
            submit_btn.click(
                fn=self.chat_with_agent,
                inputs=[msg, chatbot],
                outputs=[chatbot, msg]
            )
            
            msg.submit(
                fn=self.chat_with_agent,
                inputs=[msg, chatbot],
                outputs=[chatbot, msg]
            )
        
        return demo
    
    def launch(self, share: bool = False, debug: bool = False):
        """
        Launch the Gradio interface
        
        Args:
            share: Whether to create a public link
            debug: Whether to run in debug mode
        """
        interface = self.create_interface()
        interface.launch(share=share, debug=debug, theme=gr.themes.Soft())
