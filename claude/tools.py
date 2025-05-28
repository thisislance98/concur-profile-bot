import asyncio
import json
import os
from dotenv import load_dotenv
from typing import List, Dict, Any, AsyncGenerator, Optional
from anthropic import AsyncAnthropic
from anthropic.types.beta import BetaMessageParam

# Load environment variables from .env_tools file
load_dotenv(".env_tools")


class ClaudeSonnet4NativeToolsAgent:
    """
    A streaming agent that uses Claude Sonnet 4 with Anthropic's native web search 
    and code execution tools.
    
    Requirements:
    - Web search must be enabled in your Anthropic Console
    - Code execution requires beta header
    """
    
    def __init__(self, api_key: str):
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = "claude-3-5-opus-20241022"  # Supports both tools
        self.conversation_history = []
        
    async def stream_message(
        self, 
        user_message: str,
        enable_web_search: bool = True,
        enable_code_execution: bool = True,
        web_search_config: Optional[Dict[str, Any]] = None,
        code_execution_config: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream a response from Claude Opus 4 with native tools.
        
        Args:
            user_message: The user's input message
            enable_web_search: Enable web search tool
            enable_code_execution: Enable code execution tool
            web_search_config: Configuration for web search (max_uses, domains, etc.)
            code_execution_config: Configuration for code execution
        """
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Configure tools
        tools = []
        
        if enable_web_search:
            web_search_tool = {
                "type": "web_search_20250305",
                "name": "web_search"
            }
            if web_search_config:
                web_search_tool.update(web_search_config)
            tools.append(web_search_tool)
        
        if enable_code_execution:
            code_exec_tool = {
                "type": "code_execution_20250522",
                "name": "code_execution"
            }
            if code_execution_config:
                code_exec_tool.update(code_execution_config)
            tools.append(code_exec_tool)
        
        # Prepare headers for beta features
        extra_headers = {}
        if enable_code_execution:
            extra_headers["anthropic-beta"] = "code-execution-2025-05-22"
        
        try:
            # Create streaming message with native tools
            stream = await self.client.messages.create(
                model=self.model,
                messages=self.conversation_history,
                tools=tools if tools else None,
                max_tokens=4096,
                stream=True,
                extra_headers=extra_headers
            )
            
            current_content = ""
            
            async for event in stream:
                # Handle message start
                if event.type == "message_start":
                    yield {
                        "type": "message_start",
                        "message_id": event.message.id if hasattr(event, "message") else None
                    }
                
                # Handle content blocks
                elif event.type == "content_block_start":
                    content_block = event.content_block
                    if content_block.type == "text":
                        yield {"type": "text_start"}
                    elif content_block.type == "tool_use":
                        yield {
                            "type": "tool_start",
                            "tool_name": content_block.name,
                            "tool_id": content_block.id
                        }
                
                # Handle content deltas
                elif event.type == "content_block_delta":
                    delta = event.delta
                    if hasattr(delta, "type") and delta.type == "text_delta":
                        current_content += delta.text
                        yield {
                            "type": "text_delta",
                            "text": delta.text
                        }
                    elif hasattr(delta, "type") and delta.type == "input_json_delta":
                        yield {
                            "type": "tool_input_delta",
                            "json": delta.partial_json
                        }
                
                # Handle tool results
                elif event.type == "content_block_stop":
                    index = event.index
                    yield {
                        "type": "content_block_stop",
                        "index": index
                    }
                
                # Handle tool results from native tools
                elif hasattr(event, "type") and "tool_result" in str(event.type):
                    if event.type == "web_search_tool_result":
                        yield {
                            "type": "web_search_result",
                            "results": event.content if hasattr(event, "content") else None
                        }
                    elif event.type == "code_execution_tool_result":
                        yield {
                            "type": "code_execution_result",
                            "stdout": getattr(event.content, "stdout", "") if hasattr(event, "content") else "",
                            "stderr": getattr(event.content, "stderr", "") if hasattr(event, "content") else "",
                            "return_code": getattr(event.content, "return_code", None) if hasattr(event, "content") else None
                        }
                
                # Handle message completion
                elif event.type == "message_stop":
                    # Save to conversation history
                    if current_content:
                        self.conversation_history.append({
                            "role": "assistant",
                            "content": current_content
                        })
                    
                    stop_reason = None
                    if hasattr(event, "message") and hasattr(event.message, "stop_reason"):
                        stop_reason = event.message.stop_reason
                    
                    yield {
                        "type": "message_complete",
                        "stop_reason": stop_reason
                    }
                
                # Handle errors
                elif event.type == "error":
                    yield {
                        "type": "error",
                        "error": event.error if hasattr(event, "error") else "Unknown error"
                    }
                    
        except Exception as e:
            yield {
                "type": "error",
                "error": str(e)
            }
    
    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []


# Example usage with formatting
async def main():
    """Demonstrate using Claude Opus 4 with native tools."""
    
    # Initialize the agent
    api_key = os.getenv("ANTHROPIC_API_KEY", "YOUR_ANTHROPIC_API_KEY")
    agent = ClaudeOpus4NativeToolsAgent(api_key=api_key)
    
    # Example queries that will trigger different tools
    examples = [
        {
            "query": "Search for the latest AI developments in 2025 and explain their significance",
            "config": {
                "web_search_config": {
                    "max_uses": 3  # Limit to 3 searches
                }
            }
        },
        {
            "query": "Write and execute Python code to generate a visualization of the Fibonacci sequence",
            "config": {
                "enable_web_search": False  # Code execution only
            }
        },
        {
            "query": "Find current Python job market trends and create a data visualization showing salary ranges",
            "config": {
                "web_search_config": {
                    "max_uses": 5,
                    "user_location": {
                        "type": "approximate",
                        "city": "San Francisco",
                        "region": "California",
                        "country": "United States",
                        "timezone": "America/Los_Angeles"
                    }
                }
            }
        },
        {
            "query": "Research machine learning frameworks and write code to compare their performance",
            "config": {
                "web_search_config": {
                    "allowed_domains": ["pytorch.org", "tensorflow.org", "scikit-learn.org"]
                }
            }
        }
    ]
    
    for i, example in enumerate(examples):
        print(f"\n{'='*80}")
        print(f"Example {i+1}: {example['query']}")
        print(f"{'='*80}\n")
        
        config = example.get("config", {})
        
        async for event in agent.stream_message(
            example["query"],
            enable_web_search=config.get("enable_web_search", True),
            enable_code_execution=config.get("enable_code_execution", True),
            web_search_config=config.get("web_search_config"),
            code_execution_config=config.get("code_execution_config")
        ):
            # Handle different event types
            if event["type"] == "message_start":
                print("Assistant: ", end="", flush=True)
            
            elif event["type"] == "text_delta":
                print(event["text"], end="", flush=True)
            
            elif event["type"] == "tool_start":
                print(f"\n\n[🔧 Using {event['tool_name']}...]", flush=True)
            
            elif event["type"] == "web_search_result":
                print(f"\n[🔍 Web search completed]", flush=True)
            
            elif event["type"] == "code_execution_result":
                print(f"\n[💻 Code execution completed]", flush=True)
                if event.get("stdout"):
                    print(f"Output: {event['stdout'][:200]}...")
            
            elif event["type"] == "message_complete":
                print(f"\n\n[✓ Response complete - Stop reason: {event.get('stop_reason')}]")
            
            elif event["type"] == "error":
                print(f"\n[❌ Error: {event['error']}]")
        
        # Small delay between examples
        await asyncio.sleep(1)


# Handle web search citations
class WebSearchHandler:
    """Helper to handle web search results and citations."""
    
    def __init__(self):
        self.search_results = []
        self.citations = []
    
    def process_search_result(self, result: Dict[str, Any]):
        """Process web search results including citations."""
        if "web_search_result_locations" in result:
            for location in result["web_search_result_locations"]:
                citation = {
                    "url": location.get("url"),
                    "title": location.get("title"),
                    "cited_text": location.get("cited_text"),
                    "encrypted_index": location.get("encrypted_index")
                }
                self.citations.append(citation)
        
        if "content" in result:
            self.search_results.append(result["content"])
    
    def format_citations(self) -> str:
        """Format citations for display."""
        if not self.citations:
            return ""
        
        formatted = "\n\n📚 **Sources:**\n"
        for i, cite in enumerate(self.citations, 1):
            formatted += f"{i}. [{cite['title']}]({cite['url']})\n"
            if cite['cited_text']:
                formatted += f"   > \"{cite['cited_text'][:100]}...\"\n"
        return formatted


# Complete example with proper event handling
async def complete_example_with_handling():
    """Complete example showing proper handling of all native tool events."""
    
    agent = ClaudeOpus4NativeToolsAgent(api_key=os.getenv("ANTHROPIC_API_KEY"))
    search_handler = WebSearchHandler()
    
    # Complex query requiring both tools
    query = """
    Search for the latest breakthroughs in quantum computing from 2025,
    then write Python code to simulate a simple quantum algorithm and 
    visualize the results.
    """
    
    # Configure tools with specific settings
    web_search_config = {
        "max_uses": 5,
        "user_location": {
            "type": "approximate",
            "country": "United States",
            "timezone": "America/New_York"
        }
    }
    
    print(f"User: {query}\n")
    print("Assistant: ", end="", flush=True)
    
    full_response = ""
    code_outputs = []
    
    async for event in agent.stream_message(
        query,
        web_search_config=web_search_config
    ):
        event_type = event.get("type")
        
        # Text streaming
        if event_type == "text_delta":
            text = event["text"]
            full_response += text
            print(text, end="", flush=True)
        
        # Tool usage
        elif event_type == "tool_start":
            tool = event["tool_name"]
            if tool == "web_search":
                print("\n\n🔍 [Searching the web...]", flush=True)
            elif tool == "code_execution":
                print("\n\n💻 [Executing Python code...]", flush=True)
        
        # Web search results
        elif event_type == "web_search_result":
            if event.get("results"):
                search_handler.process_search_result(event["results"])
                print("\n✓ [Search completed]", flush=True)
        
        # Code execution results
        elif event_type == "code_execution_result":
            result = {
                "stdout": event.get("stdout", ""),
                "stderr": event.get("stderr", ""),
                "return_code": event.get("return_code", -1)
            }
            code_outputs.append(result)
            
            if result["return_code"] == 0:
                print("\n✓ [Code executed successfully]", flush=True)
                if result["stdout"]:
                    print(f"\nOutput preview:\n{result['stdout'][:200]}...")
            else:
                print(f"\n❌ [Code execution failed: {result['stderr']}]", flush=True)
        
        # Handle errors
        elif event_type == "error":
            error = event.get("error", "Unknown error")
            print(f"\n\n❌ Error: {error}", flush=True)
            
            # Check for specific error codes
            if isinstance(error, dict):
                error_code = error.get("error_code")
                if error_code == "max_uses_exceeded":
                    print("Web search limit reached.")
                elif error_code == "code_execution_exceeded":
                    print("Code execution time limit exceeded.")
                elif error_code == "too_many_requests":
                    print("Rate limit exceeded. Please try again later.")
        
        # Message complete
        elif event_type == "message_complete":
            stop_reason = event.get("stop_reason")
            
            # Handle pause_turn for long-running operations
            if stop_reason == "pause_turn":
                print("\n\n⏸️  [Turn paused - continue conversation to resume]")
            else:
                # Show citations if any
                citations = search_handler.format_citations()
                if citations:
                    print(citations)
                
                # Show code outputs summary
                if code_outputs:
                    print(f"\n\n📊 Code Execution Summary:")
                    print(f"   - Executions: {len(code_outputs)}")
                    print(f"   - Successful: {sum(1 for o in o['return_code'] == 0)}")
                
                print(f"\n\n✅ Response complete")


# Advanced example with file handling
async def file_analysis_example():
    """Example showing code execution with file uploads."""
    
    agent = ClaudeOpus4NativeToolsAgent(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    # This would be used with files uploaded via the Files API
    query = """
    Analyze the uploaded CSV file and create visualizations showing:
    1. Data distribution
    2. Key statistics
    3. Any interesting patterns
    """
    
    # Enable both tools with file support
    async for event in agent.stream_message(
        query,
        enable_web_search=False,
        enable_code_execution=True,
        code_execution_config={
            "max_execution_duration": 300  # 5 minutes max
        }
    ):
        # Handle events...
        pass


# Streaming example with real-time processing
async def streaming_example():
    """Show how to process streaming responses in real-time."""
    
    agent = ClaudeOpus4NativeToolsAgent(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    print("Ask me anything (I can search the web and run Python code):")
    user_input = input("> ")
    
    # Track tool usage
    tools_used = []
    response_parts = []
    
    async for event in agent.stream_message(user_input):
        if event["type"] == "text_delta":
            text = event["text"]
            response_parts.append(text)
            print(text, end="", flush=True)
        
        elif event["type"] == "tool_start":
            tools_used.append(event["tool_name"])
            print(f"\n[Using {event['tool_name']}...]", flush=True)
        
        elif event["type"] == "message_complete":
            print(f"\n\nTools used: {', '.join(tools_used) if tools_used else 'None'}")
            print(f"Total response length: {len(''.join(response_parts))} characters")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())
    
    # Uncomment to try other examples:
    # asyncio.run(complete_example_with_handling())
    # asyncio.run(file_analysis_example())
    # asyncio.run(streaming_example())