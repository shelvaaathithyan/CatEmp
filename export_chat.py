import json
import os

transcript_path = r"C:\Users\US DILEEPAN\.gemini\antigravity-ide\brain\4a864640-0b41-415a-9bfd-88146e347b15\.system_generated\logs\transcript_full.jsonl"
output_path = r"d:\CatEmp\chat_history.md"

def export_chat():
    if not os.path.exists(transcript_path):
        print("Transcript file not found!")
        return

    md_lines = ["# Complete Chat & Development History\n\n"]
    
    with open(transcript_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            step = json.loads(line.strip())
            step_type = step.get('type')
            content = step.get('content', '')
            
            if step_type == 'USER_INPUT' and content:
                # Clean prompt tags if present
                clean_content = content
                if '<USER_REQUEST>' in clean_content:
                    clean_content = clean_content.split('<USER_REQUEST>')[-1].split('</USER_REQUEST>')[0].strip()
                md_lines.append(f"## 👤 User Request\n\n{clean_content}\n\n---\n")
                
            elif step_type == 'PLANNER_RESPONSE':
                if content:
                    md_lines.append(f"### 🤖 Assistant Response\n\n{content}\n\n")
                
                tool_calls = step.get('tool_calls', [])
                if tool_calls:
                    md_lines.append("#### 🛠️ Tool Executions:\n")
                    for tc in tool_calls:
                        name = tc.get('name')
                        args = tc.get('args', {})
                        md_lines.append(f"- **{name}**: `{args}`\n")
                    md_lines.append("\n---\n")

    with open(output_path, 'w', encoding='utf-8') as out:
        out.writelines(md_lines)

    print(f"Successfully exported chat history to {output_path}")

if __name__ == '__main__':
    export_chat()
