def text_chunker(text: str)-> list[str]:
    if not text:
        return[]
    
    chunks = []
    raw_chunks = text.split("\n")
    
    for chunk in raw_chunks:
        segmented = chunk.strip()
        
        if not segmented:
            continue
        
        if len(segmented.split())<8:
            continue
        
        chunks.append(segmented)
        
        return chunks
