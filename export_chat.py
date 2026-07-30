import json
import os

transcript_path = r"C:\Users\US DILEEPAN\.gemini\antigravity-ide\brain\4a864640-0b41-415a-9bfd-88146e347b15\.system_generated\logs\transcript_full.jsonl"
output_path = r"d:\CatEmp\chat_history.md"

def export_chat():
    with open(transcript_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write("# Conversation History\n\n")
        
        for line in lines:
            if not line.strip():
                continue
                
            try:
                data = json.loads(line)
                step_type = data.get("type", "")
                content = data.get("content", "")
                
                if step_type == "USER_INPUT":
                    out.write(f"## User\n\n{content}\n\n---\n\n")
                elif step_type == "PLANNER_RESPONSE":
                    out.write(f"## Antigravity (Agent)\n\n{content}\n\n")
                    
                    # Also include tool calls if any
                    tool_calls = data.get("tool_calls", [])
                    if tool_calls:
                        for tool in tool_calls:
                            tool_name = tool.get("name", "tool")
                            args = tool.get("arguments", {})
                            out.write(f"**Tool Call:** `{tool_name}`\n")
                            if "toolSummary" in args:
                                out.write(f"**Summary:** {args['toolSummary']}\n")
                            out.write("\n")
                    out.write("---\n\n")
            except json.JSONDecodeError:
                pass
                
if __name__ == "__main__":
    export_chat()
    print(f"Chat exported successfully to {output_path}")
