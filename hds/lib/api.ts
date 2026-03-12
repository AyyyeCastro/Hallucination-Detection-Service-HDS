export async function analyzeText(text: string){
    const response = await fetch("http://localhost:8000/analyze/",{
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ text })
    });
    
    if (!response.ok){
        throw new Error("Text Analyze API failed to respond");
    }

    return response.json();
}