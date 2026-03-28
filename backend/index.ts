import express, { Request, Response } from 'express';
import dotenv from "dotenv";
import cors from "cors";
import cookieParser from "cookie-parser";
import axios from 'axios';

dotenv.config();

const app = express();
const port = 8000;

const SOLR_URL = process.env.SOLR_URL || 'http://solr:8983/solr/football_core/select';

app.use(cors({
    origin: "http://localhost:5173",
    credentials: true,
}));

app.use(express.json());
app.use(cookieParser());

// Define the interface for TypeScript safety
interface NestedComment {
    text: string;
    sentiment: 'positive' | 'negative' | 'neutral';
}

/**
 * FINAL PARSER: Splits Python lists by looking for content inside '...' or "..."
 * This version avoids backreferences (\1) to prevent TypeScript Octal errors.
 */
const parseComments = (raw: string): string[] => {
    if (!raw || raw === '[]' || typeof raw !== 'string') return [];
    
    const result: string[] = [];
    // Catch content in 'single quotes' OR "double quotes" separately
    const regex = /'((?:\\.|[^'])*)'|"((?:\\.|[^"])*)"/gs;
    let match;

    while ((match = regex.exec(raw)) !== null) {
        // match[1] is content from single quotes, match[2] is from double quotes
        let content = (match[1] || match[2])
            .replace(/\\'/g, "'")
            .replace(/\\"/g, '"')
            .replace(/\\n/g, ' ')
            .replace(/\\r/g, '')
            .trim();
        
        if (content && content !== "[]") result.push(content);
    }
    return result;
};

const getSentiment = (text: string): 'positive' | 'negative' | 'neutral' => {
    const lowerText = text.toLowerCase();
    const positiveWords = ['good', 'great', 'amazing', 'goal', 'win', 'best', 'happy'];
    const negativeWords = ['bad', 'awful', 'terrible', 'worst', 'lose', 'fail', 'hate'];

    let score = 0;
    positiveWords.forEach(w => { if (lowerText.includes(w)) score++; });
    negativeWords.forEach(w => { if (lowerText.includes(w)) score--; });

    if (score > 0) return 'positive';
    if (score < 0) return 'negative';
    return 'neutral';
};

app.post('/search', async (req: Request, res: Response) => {
    try {
        const { query, team, source, start_date, end_date } = req.body;

        // TARGETED SEARCH: Title, Content, Author, Subreddit
        let q = '*:*';
        if (query) {
            q = `(title:("${query}") OR content:("${query}") OR author:("${query}") OR subreddit:("${query}"))`;
        }

        const params: any = {
            q: q,
            wt: 'json',
            rows: 50,
            sort: 'num_comments desc', // Rank by discussion volume
            fq: [] as string[]
        };

        if (team) params.fq.push(`author_flair:"${team}"`);
        if (source) params.fq.push(`subreddit:"${source}"`);
        if (start_date || end_date) {
            const start = start_date ? `${start_date}T00:00:00Z` : '*';
            const end = end_date ? `${end_date}T23:59:59Z` : '*';
            params.fq.push(`datetime:[${start} TO ${end}]`);
        }

        const solrResponse: any = await axios.get(SOLR_URL, { params });
        const docs = solrResponse.data.response.docs;

        const posts = docs.map((doc: any) => {
            let nestedComments: NestedComment[] = [];
            const rawCommentsStr = doc.comments_raw;

            if (rawCommentsStr) {
                // Tách bình luận lẻ bằng hàm Parser mới
                const commentTexts = parseComments(rawCommentsStr);
                nestedComments = commentTexts.map(text => ({
                    text,
                    sentiment: getSentiment(text)
                }));
            }

            return {
                id: doc.id,
                author: doc.author,
                title: doc.title,
                content: doc.content || "",
                timestamp: doc.datetime ? new Date(doc.datetime).toLocaleString() : "Unknown",
                source: doc.subreddit,
                team: doc.author_flair || "General",
                nestedComments: nestedComments 
            };
        });

        res.json({ posts: posts, recordCount: solrResponse.data.response.numFound });

    } catch (error: any) {
        console.error("Backend Error:", error.message);
        res.status(500).json({ error: "Search failed" });
    }
});

app.listen(port, () => console.log(`Backend running on port ${port}`));