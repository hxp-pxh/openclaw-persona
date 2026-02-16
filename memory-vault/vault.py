#!/usr/bin/env python3
"""
Vesper's Memory Vault v2 - Progressive disclosure semantic memory

Usage:
    python vault.py index              # Index all memory files
    python vault.py query "text"       # Search (summaries only - token efficient)
    python vault.py query --full "text"  # Search (full chunks)
    python vault.py get <id>           # Get full memory by ID
    python vault.py add "text"         # Add observation (default type)
    python vault.py add --type=decision "text"  # Add typed observation
    python vault.py consolidate        # Find similar memories to merge
    python vault.py delete <id>        # Delete memory by ID
    python vault.py stats              # Show vault statistics
    
Observation types: decision, lesson, bugfix, discovery, implementation, observation
Memory areas: core, trading, infrastructure, personal, projects

Path Resolution (in order):
    1. VMEM_DIR environment variable
    2. .vmem file in current directory (contains path)
    3. memory-vault/ in current directory (if exists)
    4. ~/.openclaw/memory/ (default)
"""

import os
import sys
import hashlib
import json
import re
from pathlib import Path
from datetime import datetime

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Dynamic path resolution
def get_vault_dir():
    """Find the vault directory using priority-based resolution."""
    # 1. Environment variable
    if os.environ.get('VMEM_DIR'):
        return Path(os.environ['VMEM_DIR'])
    
    # 2. Workspace config file (.vmem contains path)
    cwd = Path.cwd()
    config_file = cwd / '.vmem'
    if config_file.exists():
        configured_path = config_file.read_text().strip()
        if configured_path:
            return Path(configured_path).expanduser()
    
    # 3. Check for existing memory-vault in workspace
    workspace_vault = cwd / 'memory-vault'
    if workspace_vault.exists() and (workspace_vault / 'chroma_db').exists():
        return workspace_vault
    
    # 4. Default to ~/.openclaw/memory
    default_dir = Path.home() / '.openclaw' / 'memory'
    default_dir.mkdir(parents=True, exist_ok=True)
    return default_dir

def get_workspace_dir():
    """Find the workspace directory (where MEMORY.md etc. live)."""
    # Check for .vmem or MEMORY.md in cwd
    cwd = Path.cwd()
    if (cwd / 'MEMORY.md').exists() or (cwd / '.vmem').exists():
        return cwd
    # Fall back to home
    return Path.home()

# Paths
VAULT_DIR = get_vault_dir()
WORKSPACE_DIR = get_workspace_dir()
MEMORY_DIR = WORKSPACE_DIR / "memory"
LEARNINGS_DIR = WORKSPACE_DIR / ".learnings"
CHROMA_DIR = VAULT_DIR / "chroma_db"

# Files to index (relative to workspace)
def get_memory_files():
    files = []
    core_files = ["MEMORY.md", "SOUL.md", "USER.md", "TOOLS.md", "AGENTS.md", "HEARTBEAT.md", "IDENTITY.md"]
    for f in core_files:
        path = WORKSPACE_DIR / f
        if path.exists():
            files.append(path)
    return files

MEMORY_FILES = get_memory_files()

# Observation types
OBSERVATION_TYPES = {
    'decision': 'Choices and decisions made',
    'lesson': 'Lessons learned from experience',
    'bugfix': 'Bug fixes and their solutions',
    'discovery': 'New discoveries or insights',
    'implementation': 'Implementation details',
    'observation': 'General observations'
}

# Memory areas for organization
MEMORY_AREAS = ['core', 'trading', 'infrastructure', 'personal', 'projects']


class MemoryVault:
    def __init__(self, lazy_load=True):
        self.model = None
        self.client = None
        self.collection = None
        if not lazy_load:
            self._init_model()
            self._init_db()
    
    def _init_model(self):
        if self.model is None:
            print("Loading embedding model...", file=sys.stderr)
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def _init_db(self):
        if self.client is None:
            CHROMA_DIR.mkdir(parents=True, exist_ok=True)
            self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))
            self.collection = self.client.get_or_create_collection(
                name="memories",
                metadata={"hnsw:space": "cosine"}
            )
    
    def _chunk_markdown(self, text: str, source: str, chunk_size: int = 500) -> list:
        """Split markdown into semantic chunks."""
        chunks = []
        current_chunk = []
        current_size = 0
        current_headers = []
        
        for line in text.split('\n'):
            # Track headers for context
            if line.startswith('#'):
                level = len(line.split()[0])
                header_text = line.lstrip('#').strip()
                current_headers = current_headers[:level-1] + [header_text]
            
            line_size = len(line)
            
            # Start new chunk if too large
            if current_size + line_size > chunk_size and current_chunk:
                chunk_text = '\n'.join(current_chunk)
                header_context = ' > '.join(current_headers) if current_headers else ''
                chunks.append({
                    'text': chunk_text,
                    'source': source,
                    'headers': header_context,
                    'summary': self._summarize_chunk(chunk_text)
                })
                current_chunk = []
                current_size = 0
            
            current_chunk.append(line)
            current_size += line_size
        
        # Don't forget last chunk
        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            header_context = ' > '.join(current_headers) if current_headers else ''
            chunks.append({
                'text': chunk_text,
                'source': source,
                'headers': header_context,
                'summary': self._summarize_chunk(chunk_text)
            })
        
        return chunks
    
    def _summarize_chunk(self, text: str, max_len: int = 100) -> str:
        """Create a brief summary of a chunk."""
        # Take first meaningful line
        for line in text.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and len(line) > 10:
                if len(line) > max_len:
                    return line[:max_len] + "..."
                return line
        return text[:max_len] + "..." if len(text) > max_len else text
    
    def index_files(self):
        """Index all memory files into the vector store."""
        self._init_model()
        self._init_db()
        
        all_chunks = []
        
        # Index core files
        for file_path in MEMORY_FILES:
            if file_path.exists():
                print(f"Indexing {file_path.name}...")
                text = file_path.read_text()
                chunks = self._chunk_markdown(text, file_path.name)
                all_chunks.extend(chunks)
        
        # Index memory directory
        if MEMORY_DIR.exists():
            for md_file in MEMORY_DIR.glob("*.md"):
                print(f"Indexing {md_file.name}...")
                text = md_file.read_text()
                chunks = self._chunk_markdown(text, f"memory/{md_file.name}")
                all_chunks.extend(chunks)
        
        # Index learnings directory
        if LEARNINGS_DIR.exists():
            for md_file in LEARNINGS_DIR.glob("*.md"):
                print(f"Indexing {md_file.name}...")
                text = md_file.read_text()
                chunks = self._chunk_markdown(text, f".learnings/{md_file.name}")
                all_chunks.extend(chunks)
        
        if not all_chunks:
            print("No files to index.")
            return
        
        # Clear existing and add new
        try:
            self.client.delete_collection("memories")
        except:
            pass
        self.collection = self.client.create_collection(
            name="memories",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Batch embed and add
        texts = [c['text'] for c in all_chunks]
        print(f"Embedding {len(texts)} chunks...")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        ids = [hashlib.md5(t.encode()).hexdigest()[:12] for t in texts]
        metadatas = [{
            'source': c['source'],
            'headers': c['headers'],
            'summary': c['summary'],
            'indexed_at': datetime.now().isoformat()
        } for c in all_chunks]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=metadatas
        )
        
        print(f"✓ Indexed {len(all_chunks)} chunks from {len(MEMORY_FILES)} core files + memory/*.md + .learnings/*.md")
        print(f"  Vault location: {VAULT_DIR}")
    
    def query(self, text: str, n_results: int = 5, full: bool = False, obs_type: str = None) -> list:
        """Query the memory vault."""
        self._init_model()
        self._init_db()
        
        embedding = self.model.encode([text])[0]
        
        where_filter = None
        if obs_type:
            where_filter = {"type": obs_type}
        
        results = self.collection.query(
            query_embeddings=[embedding.tolist()],
            n_results=n_results,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )
        
        output = []
        for i, (doc, meta, dist) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        )):
            score = 1 - dist  # Convert distance to similarity
            result = {
                'id': results['ids'][0][i],
                'score': round(score, 3),
                'source': meta.get('source', 'unknown'),
                'headers': meta.get('headers', ''),
            }
            if full:
                result['text'] = doc
            else:
                result['summary'] = meta.get('summary', doc[:100])
            output.append(result)
        
        # Track access
        self.update_access([r["id"] for r in output])
        
        return output
    
    def get_by_id(self, memory_id: str) -> dict:
        """Get full memory content by ID."""
        self._init_db()
        
        result = self.collection.get(
            ids=[memory_id],
            include=["documents", "metadatas"]
        )
        
        if result['ids']:
            return {
                'id': memory_id,
                'text': result['documents'][0],
                'metadata': result['metadatas'][0]
            }
        return None
    
    def add_observation(self, text: str, obs_type: str = 'observation', area: str = 'core') -> str:
        """Add a new observation to the vault."""
        self._init_model()
        self._init_db()
        
        # Generate ID
        obs_id = hashlib.md5(f"{text}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        # Embed
        embedding = self.model.encode([text])[0]
        
        # Add to collection
        self.collection.add(
            ids=[obs_id],
            embeddings=[embedding.tolist()],
            documents=[text],
            metadatas=[{
                'source': 'observation',
                'type': obs_type,
                'area': area,
                'summary': text[:100] if len(text) > 100 else text,
                'indexed_at': datetime.now().isoformat()
            }]
        )
        
        return obs_id
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory by ID."""
        self._init_db()
        try:
            self.collection.delete(ids=[memory_id])
            return True
        except:
            return False
    
    def find_similar(self, threshold: float = 0.85) -> list:
        """Find similar memory pairs for consolidation."""
        self._init_db()
        
        # Get all memories
        all_data = self.collection.get(include=["documents", "metadatas", "embeddings"])
        
        if not all_data['ids']:
            return []
        
        similar_pairs = []
        ids = all_data['ids']
        embeddings = all_data['embeddings']
        docs = all_data['documents']
        
        # Compare all pairs
        import numpy as np
        embeddings_np = np.array(embeddings)
        
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                # Cosine similarity
                sim = np.dot(embeddings_np[i], embeddings_np[j]) / (
                    np.linalg.norm(embeddings_np[i]) * np.linalg.norm(embeddings_np[j])
                )
                if sim >= threshold:
                    similar_pairs.append({
                        'id1': ids[i],
                        'id2': ids[j],
                        'similarity': round(float(sim), 3),
                        'preview1': docs[i][:80],
                        'preview2': docs[j][:80]
                    })
        
        return sorted(similar_pairs, key=lambda x: -x['similarity'])
    
    def stats(self) -> dict:
        """Get vault statistics."""
        self._init_db()
        
        count = self.collection.count()
        
        # Get source distribution
        all_data = self.collection.get(include=["metadatas"])
        sources = {}
        types = {}
        for meta in all_data['metadatas']:
            src = meta.get('source', 'unknown')
            sources[src] = sources.get(src, 0) + 1
            t = meta.get('type', 'chunk')
            types[t] = types.get(t, 0) + 1
        
        return {
            'total_memories': count,
            'by_source': sources,
            'by_type': types,
            'vault_dir': str(VAULT_DIR),
            'workspace_dir': str(WORKSPACE_DIR)
        }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1]
    vault = MemoryVault()
    
    if cmd == 'index':
        vault.index_files()
    
    elif cmd == 'query':
        full = '--full' in sys.argv
        type_filter = None
        for arg in sys.argv:
            if arg.startswith('--type='):
                type_filter = arg.split('=')[1]
        
        # Find the query text (last non-flag argument)
        query_text = None
        for arg in sys.argv[2:]:
            if not arg.startswith('--'):
                query_text = arg
        
        if not query_text:
            print("Usage: vault.py query [--full] [--type=TYPE] \"search text\"")
            return
        
        results = vault.query(query_text, full=full, obs_type=type_filter)
        for r in results:
            print(f"\n[{r['id']}] ({r['score']}) {r['source']}")
            if r.get('headers'):
                print(f"  📍 {r['headers']}")
            if full:
                print(f"  {r['text']}")
            else:
                print(f"  {r['summary']}")
    
    elif cmd == 'get':
        if len(sys.argv) < 3:
            print("Usage: vault.py get <id> [<id2> ...]")
            return
        
        for mem_id in sys.argv[2:]:
            result = vault.get_by_id(mem_id)
            if result:
                print(f"\n=== {result['id']} ===")
                print(f"Source: {result['metadata'].get('source', 'unknown')}")
                if result['metadata'].get('headers'):
                    print(f"Headers: {result['metadata']['headers']}")
                print(f"\n{result['text']}")
            else:
                print(f"Memory {mem_id} not found")
    
    elif cmd == 'add':
        obs_type = 'observation'
        area = 'core'
        text = None
        
        for arg in sys.argv[2:]:
            if arg.startswith('--type='):
                obs_type = arg.split('=')[1]
            elif arg.startswith('--area='):
                area = arg.split('=')[1]
            elif not arg.startswith('--'):
                text = arg
        
        if not text:
            print("Usage: vault.py add [--type=TYPE] [--area=AREA] \"memory text\"")
            return
        
        obs_id = vault.add_observation(text, obs_type, area)
        print(f"✓ Added [{obs_id}] ({obs_type}): {text[:50]}...")
    
    elif cmd == 'consolidate':
        threshold = 0.85
        for arg in sys.argv[2:]:
            if arg.startswith('--threshold='):
                threshold = float(arg.split('=')[1])
        
        pairs = vault.find_similar(threshold)
        if not pairs:
            print(f"No similar pairs found above {threshold} threshold")
            return
        
        print(f"Found {len(pairs)} similar pairs:\n")
        for p in pairs:
            print(f"[{p['id1']}] ↔ [{p['id2']}] (similarity: {p['similarity']})")
            print(f"  1: {p['preview1']}...")
            print(f"  2: {p['preview2']}...")
            print()
    
    elif cmd == 'delete':
        if len(sys.argv) < 3:
            print("Usage: vault.py delete <id>")
            return
        
        mem_id = sys.argv[2]
        if vault.delete_memory(mem_id):
            print(f"✓ Deleted {mem_id}")
        else:
            print(f"Failed to delete {mem_id}")
    
    elif cmd == 'stats':
        stats = vault.stats()
        print(f"📊 Memory Vault Statistics")
        print(f"   Vault: {stats['vault_dir']}")
        print(f"   Workspace: {stats['workspace_dir']}")
        print(f"   Total memories: {stats['total_memories']}")
        print(f"\n   By source:")
        for src, count in sorted(stats['by_source'].items(), key=lambda x: -x[1])[:10]:
            print(f"      {src}: {count}")
        print(f"\n   By type:")
        for t, count in sorted(stats['by_type'].items(), key=lambda x: -x[1]):
            print(f"      {t}: {count}")
    
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == '__main__':
    main()


    def update_access(self, memory_ids: List[str]):
        """Update access tracking for retrieved memories."""
        self._init_db()
        
        for mem_id in memory_ids:
            try:
                # Get current metadata
                result = self.collection.get(ids=[mem_id], include=["metadatas"])
                if result["ids"]:
                    meta = result["metadatas"][0]
                    meta["last_accessed"] = datetime.now().isoformat()
                    meta["access_count"] = meta.get("access_count", 0) + 1
                    
                    # Update (ChromaDB requires upsert via update)
                    self.collection.update(
                        ids=[mem_id],
                        metadatas=[meta]
                    )
            except Exception as e:
                pass  # Don't crash on tracking failures
