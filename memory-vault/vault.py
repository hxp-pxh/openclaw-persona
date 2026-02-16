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

# Paths
VAULT_DIR = Path(__file__).parent
CLAWD_DIR = VAULT_DIR.parent
MEMORY_DIR = CLAWD_DIR / "memory"
LEARNINGS_DIR = CLAWD_DIR / ".learnings"
CHROMA_DIR = VAULT_DIR / "chroma_db"

# Files to index
MEMORY_FILES = [
    CLAWD_DIR / "MEMORY.md",
    CLAWD_DIR / "SOUL.md",
    CLAWD_DIR / "USER.md",
    CLAWD_DIR / "TOOLS.md",
    CLAWD_DIR / "AGENTS.md",
    CLAWD_DIR / "HEARTBEAT.md",
    CLAWD_DIR / "IDENTITY.md",
]

# Observation types
VALID_TYPES = ["decision", "lesson", "bugfix", "discovery", "implementation", "observation"]

# Model - small and fast, good for semantic search
MODEL_NAME = "all-MiniLM-L6-v2"


def generate_summary(text: str, max_len: int = 100) -> str:
    """Generate a one-line summary from text."""
    # Clean up text
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Try to find a meaningful first sentence or section
    # Look for first sentence
    match = re.match(r'^(.+?[.!?])\s', text)
    if match and len(match.group(1)) <= max_len:
        return match.group(1)
    
    # Look for first line with content
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and len(line) > 10:
            if len(line) <= max_len:
                return line
            return line[:max_len-3] + "..."
    
    # Fall back to truncation
    if len(text) <= max_len:
        return text
    return text[:max_len-3] + "..."


class MemoryVault:
    def __init__(self):
        self.model = None
        self.client = None
        self.collection = None
    
    def _load_model(self):
        if self.model is None:
            print("Loading embedding model...", file=sys.stderr)
            self.model = SentenceTransformer(MODEL_NAME)
        return self.model
    
    def _get_collection(self):
        if self.collection is None:
            CHROMA_DIR.mkdir(exist_ok=True)
            self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))
            self.collection = self.client.get_or_create_collection(
                name="vesper_memory",
                metadata={"hnsw:space": "cosine"}
            )
        return self.collection
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
        """Split text into overlapping chunks for better retrieval."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        return chunks
    
    def _hash_content(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def index_file(self, filepath: Path) -> int:
        """Index a single file, return number of chunks added."""
        if not filepath.exists():
            return 0
        
        content = filepath.read_text()
        chunks = self._chunk_text(content)
        
        if not chunks:
            return 0
        
        model = self._load_model()
        collection = self._get_collection()
        
        # Create embeddings
        embeddings = model.encode(chunks).tolist()
        
        # Prepare data with summaries
        ids = []
        metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_hash = self._hash_content(chunk)
            doc_id = f"{filepath.stem}_{chunk_hash}_{i}"
            ids.append(doc_id)
            metadatas.append({
                "source": str(filepath),
                "chunk_idx": i,
                "indexed_at": datetime.utcnow().isoformat(),
                "summary": generate_summary(chunk),
                "type": "file_chunk",
            })
        
        # Delete old entries from this file
        existing = collection.get(where={"source": str(filepath)})
        if existing["ids"]:
            collection.delete(ids=existing["ids"])
        
        # Add new entries
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )
        
        return len(chunks)
    
    def index_all(self):
        """Index all memory files."""
        total = 0
        
        # Index main files
        for filepath in MEMORY_FILES:
            if filepath.exists():
                count = self.index_file(filepath)
                print(f"  {filepath.name}: {count} chunks")
                total += count
        
        # Index daily memory files
        if MEMORY_DIR.exists():
            for filepath in sorted(MEMORY_DIR.glob("*.md")):
                count = self.index_file(filepath)
                print(f"  memory/{filepath.name}: {count} chunks")
                total += count
        
        # Index learnings files (errors, corrections, feature requests)
        if LEARNINGS_DIR.exists():
            for filepath in sorted(LEARNINGS_DIR.glob("*.md")):
                count = self.index_file(filepath)
                print(f"  .learnings/{filepath.name}: {count} chunks")
                total += count
        
        print(f"\nTotal: {total} chunks indexed")
        return total
    
    def query(self, query_text: str, n_results: int = 5, full: bool = False, 
              obs_type: str = None) -> list[dict]:
        """Search memories semantically.
        
        Args:
            query_text: Search query
            n_results: Max results to return
            full: If True, return full text. If False, return summaries only (token-efficient)
            obs_type: Filter by observation type (optional)
        """
        model = self._load_model()
        collection = self._get_collection()
        
        # Create query embedding
        query_embedding = model.encode([query_text]).tolist()
        
        # Build where clause
        where = None
        if obs_type:
            where = {"type": obs_type}
        
        # Search
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted = []
        for i in range(len(results["ids"][0])):
            meta = results["metadatas"][0][i]
            score = 1 - results["distances"][0][i]
            
            result = {
                "id": results["ids"][0][i],
                "score": round(score, 3),
                "source": Path(meta["source"]).name,
                "type": meta.get("type", "unknown"),
            }
            
            if full:
                result["text"] = results["documents"][0][i]
            else:
                # Progressive disclosure: summary only (token-efficient)
                result["summary"] = meta.get("summary", generate_summary(results["documents"][0][i]))
            
            formatted.append(result)
        
        return formatted
    
    def get_by_id(self, doc_id: str) -> dict | None:
        """Fetch full memory by ID."""
        collection = self._get_collection()
        
        result = collection.get(
            ids=[doc_id],
            include=["documents", "metadatas"]
        )
        
        if not result["ids"]:
            return None
        
        meta = result["metadatas"][0]
        return {
            "id": doc_id,
            "text": result["documents"][0],
            "source": meta.get("source", "unknown"),
            "type": meta.get("type", "unknown"),
            "indexed_at": meta.get("indexed_at"),
        }
    
    def get_by_ids(self, doc_ids: list[str]) -> list[dict]:
        """Fetch multiple memories by ID (batch operation)."""
        collection = self._get_collection()
        
        result = collection.get(
            ids=doc_ids,
            include=["documents", "metadatas"]
        )
        
        formatted = []
        for i, doc_id in enumerate(result["ids"]):
            meta = result["metadatas"][i]
            formatted.append({
                "id": doc_id,
                "text": result["documents"][i],
                "source": meta.get("source", "unknown"),
                "type": meta.get("type", "unknown"),
                "indexed_at": meta.get("indexed_at"),
            })
        
        return formatted
    
    def add_memory(self, text: str, obs_type: str = "observation", source: str = "quick_add") -> str:
        """Add a typed observation.
        
        Args:
            text: Memory content
            obs_type: One of: decision, lesson, bugfix, discovery, implementation, observation
            source: Source label
        """
        if obs_type not in VALID_TYPES:
            print(f"Warning: Unknown type '{obs_type}', using 'observation'", file=sys.stderr)
            obs_type = "observation"
        
        model = self._load_model()
        collection = self._get_collection()
        
        embedding = model.encode([text]).tolist()
        timestamp = datetime.utcnow()
        doc_id = f"{obs_type}_{self._hash_content(text)}_{timestamp.strftime('%Y%m%d%H%M%S')}"
        
        collection.add(
            ids=[doc_id],
            embeddings=embedding,
            documents=[text],
            metadatas=[{
                "source": source,
                "type": obs_type,
                "summary": generate_summary(text),
                "indexed_at": timestamp.isoformat(),
            }]
        )
        
        return doc_id
    
    def delete_by_id(self, doc_id: str) -> bool:
        """Delete a memory by ID."""
        collection = self._get_collection()
        try:
            collection.delete(ids=[doc_id])
            return True
        except Exception as e:
            print(f"Delete failed: {e}", file=sys.stderr)
            return False
    
    def find_similar_pairs(self, threshold: float = 0.85, limit: int = 20) -> list[dict]:
        """Find pairs of similar memories that could be consolidated.
        
        Returns list of: {id1, id2, similarity, summary1, summary2}
        """
        collection = self._get_collection()
        model = self._load_model()
        
        # Get all memories
        all_docs = collection.get(include=["documents", "metadatas", "embeddings"])
        
        if not all_docs["ids"]:
            return []
        
        pairs = []
        ids = all_docs["ids"]
        docs = all_docs["documents"]
        metas = all_docs["metadatas"]
        
        # Compare each pair (expensive but thorough)
        import numpy as np
        embeddings = all_docs.get("embeddings")
        
        if embeddings is None or len(embeddings) == 0:
            # Re-embed if needed
            embeddings = model.encode(docs).tolist()
        
        embeddings = np.array(embeddings)
        
        # Compute cosine similarities
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        normalized = embeddings / (norms + 1e-10)
        similarities = np.dot(normalized, normalized.T)
        
        # Find pairs above threshold (excluding self-matches)
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                sim = similarities[i, j]
                if sim >= threshold:
                    pairs.append({
                        "id1": ids[i],
                        "id2": ids[j],
                        "similarity": round(float(sim), 3),
                        "summary1": metas[i].get("summary", docs[i][:50] + "..."),
                        "summary2": metas[j].get("summary", docs[j][:50] + "..."),
                        "source1": Path(metas[i].get("source", "unknown")).name,
                        "source2": Path(metas[j].get("source", "unknown")).name,
                    })
        
        # Sort by similarity descending
        pairs.sort(key=lambda x: x["similarity"], reverse=True)
        return pairs[:limit]
    
    def stats(self) -> dict:
        """Get vault statistics."""
        collection = self._get_collection()
        count = collection.count()
        
        # Get type distribution
        types = {}
        sources = {}
        all_docs = collection.get(include=["metadatas"])
        for meta in all_docs["metadatas"]:
            t = meta.get("type", "unknown")
            types[t] = types.get(t, 0) + 1
            s = Path(meta.get("source", "unknown")).name
            sources[s] = sources.get(s, 0) + 1
        
        return {
            "total_chunks": count,
            "by_type": types,
            "by_source": sources,
        }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    vault = MemoryVault()
    cmd = sys.argv[1]
    
    if cmd == "index":
        print("Indexing memory files...")
        vault.index_all()
    
    elif cmd == "query":
        # Parse flags
        full = False
        obs_type = None
        args = sys.argv[2:]
        query_parts = []
        
        i = 0
        while i < len(args):
            if args[i] == "--full":
                full = True
            elif args[i].startswith("--type="):
                obs_type = args[i].split("=", 1)[1]
            elif args[i] == "--type" and i + 1 < len(args):
                obs_type = args[i + 1]
                i += 1
            else:
                query_parts.append(args[i])
            i += 1
        
        if not query_parts:
            print("Usage: vault.py query [--full] [--type=TYPE] 'search text'")
            sys.exit(1)
        
        query = " ".join(query_parts)
        results = vault.query(query, full=full, obs_type=obs_type)
        print(json.dumps(results, indent=2))
    
    elif cmd == "get":
        if len(sys.argv) < 3:
            print("Usage: vault.py get <id> [<id2> ...]")
            sys.exit(1)
        
        ids = sys.argv[2:]
        if len(ids) == 1:
            result = vault.get_by_id(ids[0])
            if result:
                print(json.dumps(result, indent=2))
            else:
                print(f"Not found: {ids[0]}", file=sys.stderr)
                sys.exit(1)
        else:
            results = vault.get_by_ids(ids)
            print(json.dumps(results, indent=2))
    
    elif cmd == "add":
        # Parse flags
        obs_type = "observation"
        args = sys.argv[2:]
        text_parts = []
        
        i = 0
        while i < len(args):
            if args[i].startswith("--type="):
                obs_type = args[i].split("=", 1)[1]
            elif args[i] == "--type" and i + 1 < len(args):
                obs_type = args[i + 1]
                i += 1
            else:
                text_parts.append(args[i])
            i += 1
        
        if not text_parts:
            print("Usage: vault.py add [--type=TYPE] 'memory text'")
            print(f"Types: {', '.join(VALID_TYPES)}")
            sys.exit(1)
        
        text = " ".join(text_parts)
        doc_id = vault.add_memory(text, obs_type=obs_type)
        print(f"Added [{obs_type}]: {doc_id}")
    
    elif cmd == "stats":
        stats = vault.stats()
        print(json.dumps(stats, indent=2))
    
    elif cmd == "delete":
        if len(sys.argv) < 3:
            print("Usage: vault.py delete <id>")
            sys.exit(1)
        
        doc_id = sys.argv[2]
        if vault.delete_by_id(doc_id):
            print(f"Deleted: {doc_id}")
        else:
            print(f"Failed to delete: {doc_id}")
            sys.exit(1)
    
    elif cmd == "consolidate":
        # Parse flags
        threshold = 0.85
        args = sys.argv[2:]
        
        for arg in args:
            if arg.startswith("--threshold="):
                threshold = float(arg.split("=", 1)[1])
        
        print(f"Finding similar memories (threshold: {threshold})...")
        pairs = vault.find_similar_pairs(threshold=threshold)
        
        if not pairs:
            print("✅ No redundant memories found above threshold")
        else:
            print(f"\n🔗 Found {len(pairs)} similar pairs:\n")
            for p in pairs:
                print(f"  [{p['similarity']}] {p['source1']} ↔ {p['source2']}")
                print(f"    1: {p['summary1'][:60]}...")
                print(f"    2: {p['summary2'][:60]}...")
                print(f"    IDs: {p['id1']}")
                print(f"         {p['id2']}")
                print()
            
            print("To merge manually:")
            print("  1. vmem get <id1> <id2>  # Review full text")
            print("  2. vmem delete <id>      # Remove redundant")
            print("  3. vmem add 'merged'     # Add consolidated")
    
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
