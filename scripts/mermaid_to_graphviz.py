#!/usr/bin/env python3
"""
Convert Mermaid diagrams to Graphviz DOT format (.gv files).
Improved version that handles nested subgraphs correctly.

Date: February 6, 2026 (system date)
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class MermaidToGraphvizConverter:
    """Convert Mermaid syntax to Graphviz DOT syntax."""
    
    def __init__(self):
        self.node_counter = 0
        self.node_map: Dict[str, str] = {}
        
    def sanitize_node_id(self, text: str) -> str:
        """Convert node label to valid Graphviz node ID."""
        # Remove HTML tags like <br/>
        text = re.sub(r'<br/?>', '\\n', text)
        # Replace special characters with underscores
        text = re.sub(r'[^a-zA-Z0-9_]', '_', text)
        # Ensure it starts with a letter
        if text and text[0].isdigit():
            text = 'N' + text
        if not text:
            text = f'node_{self.node_counter}'
            self.node_counter += 1
        return text
    
    def parse_mermaid(self, mermaid_code: str) -> str:
        """Parse Mermaid code and convert to Graphviz DOT format."""
        # Reset state for new diagram
        self.node_map = {}
        self.node_counter = 0
        
        lines = mermaid_code.strip().split('\n')
        
        # Determine graph direction
        direction = 'TB'  # default
        if lines[0].startswith('graph'):
            match = re.search(r'graph\s+(TB|LR|RL|BT)', lines[0])
            if match:
                direction = match.group(1)
        
        # Map Mermaid directions to Graphviz rankdir
        rankdir_map = {
            'TB': 'TB',
            'BT': 'BT',
            'LR': 'LR',
            'RL': 'RL'
        }
        rankdir = rankdir_map.get(direction, 'TB')
        
        # Start building Graphviz DOT
        dot_lines = ['digraph G {']
        dot_lines.append(f'    rankdir={rankdir};')
        dot_lines.append('    node [shape=box, style=rounded];')
        dot_lines.append('')
        
        # Parse with proper nested subgraph handling
        subgraph_stack: List[Tuple[str, List[str]]] = []  # (name, lines)
        edges: List[Tuple[str, str]] = []
        current_subgraph_name: Optional[str] = None
        current_subgraph_lines: List[str] = []
        i = 1
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                i += 1
                continue
            
            # Check for subgraph start
            subgraph_match = re.match(r'subgraph\s+"([^"]+)"', line)
            if subgraph_match:
                # Save current subgraph if exists
                if current_subgraph_name:
                    subgraph_stack.append((current_subgraph_name, current_subgraph_lines[:]))
                
                # Start new subgraph
                current_subgraph_name = subgraph_match.group(1)
                current_subgraph_lines = []
                i += 1
                continue
            
            # Check for subgraph end
            if line == 'end':
                if current_subgraph_name:
                    # Save this subgraph
                    subgraph_stack.append((current_subgraph_name, current_subgraph_lines[:]))
                    
                    # Restore parent subgraph if exists
                    if subgraph_stack:
                        current_subgraph_name, current_subgraph_lines = subgraph_stack.pop()
                    else:
                        current_subgraph_name = None
                        current_subgraph_lines = []
                i += 1
                continue
            
            # Check for node definition: ID[Label]
            node_match = re.match(r'(\w+)\[([^\]]+)\]', line)
            if node_match:
                node_id = node_match.group(1)
                node_label = node_match.group(2)
                # Replace <br/> with \n in label
                node_label = node_label.replace('<br/>', '\\n').replace('<br>', '\\n')
                node_label = node_label.replace('"', '\\"')
                
                node_def = f'        {node_id} [label="{node_label}"];'
                
                if current_subgraph_name:
                    current_subgraph_lines.append(node_def)
                else:
                    dot_lines.append(f'    {node_id} [label="{node_label}"];')
                
                self.node_map[node_id] = node_label
                i += 1
                continue
            
            # Check for edge: A --> B
            edge_match = re.match(r'(\w+)\s+-->\s+(\w+)', line)
            if edge_match:
                from_node = edge_match.group(1)
                to_node = edge_match.group(2)
                edges.append((from_node, to_node))
                i += 1
                continue
            
            i += 1
        
        # Process all collected subgraphs
        all_subgraphs: List[Tuple[str, List[str]]] = []
        if current_subgraph_name:
            all_subgraphs.append((current_subgraph_name, current_subgraph_lines[:]))
        all_subgraphs.extend(subgraph_stack)
        
        # Add subgraphs to DOT output
        for subgraph_name, subgraph_lines in all_subgraphs:
            cluster_id = self.sanitize_node_id(subgraph_name)
            dot_lines.append(f'    subgraph cluster_{cluster_id} {{')
            dot_lines.append(f'        label="{subgraph_name}";')
            dot_lines.append('        style=rounded;')
            dot_lines.extend(subgraph_lines)
            dot_lines.append('    }')
            dot_lines.append('')
        
        # Add edges
        if edges:
            dot_lines.append('    // Edges')
            for from_node, to_node in edges:
                dot_lines.append(f'    {from_node} -> {to_node};')
        
        dot_lines.append('}')
        
        return '\n'.join(dot_lines)
    
    def convert_file(self, input_file: Path, output_file: Path):
        """Convert a Mermaid file to Graphviz DOT file."""
        mermaid_code = input_file.read_text()
        dot_code = self.parse_mermaid(mermaid_code)
        output_file.write_text(dot_code)
        print(f"✅ Converted: {input_file.name} → {output_file.name}")


def main():
    """Convert all Mermaid diagrams to Graphviz format."""
    project_root = Path(__file__).parent.parent
    mermaid_dir = project_root / "docs" / "mermaid_diagrams"
    output_dir = project_root / "docs" / "graphviz_diagrams"
    
    if not mermaid_dir.exists():
        print(f"Error: Mermaid diagrams directory not found: {mermaid_dir}")
        return
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    mermaid_files = list(mermaid_dir.glob("*.mmd"))
    
    if not mermaid_files:
        print(f"No Mermaid files found in {mermaid_dir}")
        return
    
    print(f"📊 Converting {len(mermaid_files)} Mermaid diagram(s) to Graphviz format...")
    print(f"   Source: {mermaid_dir}")
    print(f"   Output: {output_dir}\n")
    
    converter = MermaidToGraphvizConverter()
    
    for mmd_file in sorted(mermaid_files):
        gv_file = output_dir / f"{mmd_file.stem}.gv"
        converter.convert_file(mmd_file, gv_file)
    
    print(f"\n📊 Summary:")
    print(f"   Generated {len(mermaid_files)} Graphviz file(s)")
    print(f"   Output directory: {output_dir}")
    print(f"\n💡 Next steps:")
    print(f"   Generate images with: dot -Tsvg {output_dir}/*.gv -O")
    print(f"   Or: dot -Tpng {output_dir}/*.gv -O")


if __name__ == "__main__":
    main()
