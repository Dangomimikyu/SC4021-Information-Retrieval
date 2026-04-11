import express, { Request, Response } from 'express';
import dotenv from "dotenv";
import cors from "cors";
import cookieParser from "cookie-parser";
import axios from 'axios';

dotenv.config();

const app = express();
const port = 8000;

const SOLR_URL = process.env.SOLR_URL || 'http://localhost:8983/solr/football_core/select';

app.use(cors({
    origin: "http://localhost:5173",
    credentials: true,
}));

app.use(express.json());
app.use(cookieParser());

interface NestedComment {
    text: string;
    sentiment: 'positive' | 'negative' | 'neutral';
    absa_results?: any;
}

app.post('/search', async (req: Request, res: Response) => {
    try {
        const { query, source, start_date, end_date, aspect, aspect_sentiment } = req.body;

        let q = '*:*';
        if (query) {
            q = `(title:("${query}") OR content:("${query}") OR author:("${query}") OR subreddit:("${query}"))`;
        }

        const params = new URLSearchParams();
        params.append('q', q);
        params.append('wt', 'json');
        params.append('rows', '200'); 
        params.append('sort', 'num_comments desc');
        if (query) {
            params.append('spellcheck', 'true');
            params.append('spellcheck.q', query);
            params.append('spellcheck.collate', 'true');
        }

        if (source) params.append('fq', `subreddit:"${source}"`);
        if (start_date || end_date) {
            const start = start_date ? `${start_date}T00:00:00Z` : '*';
            const end = end_date ? `${end_date}T23:59:59Z` : '*';
            params.append('fq', `datetime:[${start} TO ${end}]`);
        }

        if (aspect) {
            params.append('fq', `(comments_raw:(${aspect}) OR content:(${aspect}) OR title:(${aspect}))`);
        }

        const solrResponse: any = await axios.get(SOLR_URL, { params });
        const docs = solrResponse.data.response.docs;

        let posts = docs.map((doc: any) => {
            let nestedComments: NestedComment[] = [];

            if (doc.comments_scored) {
                try {
                    nestedComments = typeof doc.comments_scored === 'string' 
                        ? JSON.parse(doc.comments_scored) 
                        : doc.comments_scored;
                } catch (err) {
                    console.error("Failed to parse pre-scored comments for doc", doc.id);
                }
            }

            let aspectStats = { positive: 0, negative: 0, neutral: 0, total: 0, targetAspect: aspect };

            // Filter AND Aggregate
            if (aspect && nestedComments.length > 0) {
                nestedComments = nestedComments.filter(comment => {
                    if (!comment.absa_results) return false;
                    
                    const aspectKey = Object.keys(comment.absa_results).find(
                        key => key.toLowerCase().includes(aspect.toLowerCase()) || 
                               aspect.toLowerCase().includes(key.toLowerCase())
                    );

                    if (!aspectKey) return false; 

                    const sent = comment.absa_results[aspectKey].sentiment.toLowerCase() as 'positive' | 'negative' | 'neutral';
                    // filter
                    if (sent === 'neutral' && Math.random() < 0.90) {
                        return false; 
                    }

                    if (aspectStats[sent] !== undefined) {
                        aspectStats[sent]++;
                    }
                    aspectStats.total++;

                    if (aspect_sentiment) {
                        return sent === aspect_sentiment.toLowerCase();
                    }

                    return true;
                });
            }

            return {
                id: doc.id,
                author: doc.author,
                title: doc.title,
                content: doc.content || "",
                timestamp: doc.datetime ? new Date(doc.datetime).toLocaleString() : "Unknown",
                source: doc.subreddit,
                team: doc.author_flair || "General",
                nestedComments: nestedComments,
                aspectSummary: aspect && aspectStats.total > 0 ? aspectStats : null 
            };
        });
        
        // Remove posts that have 0 comments left after strict filtering
        if (aspect) {
            posts = posts.filter((p: any) => p.nestedComments.length > 0);
        }

        res.json({ 
            posts: posts.slice(0, 50), 
            recordCount: posts.length,
            spellcheck: solrResponse.data.spellcheck 
        });

    } catch (error: any) {
        console.error("Backend Error:", error?.response?.data?.error?.msg || error.message);
        res.status(500).json({ error: "Search failed" });
    }
});

app.listen(port, () => console.log(`Backend running on port ${port}`));