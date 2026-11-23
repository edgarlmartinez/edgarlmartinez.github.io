import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

// The resident book "Core MSK Radiology" (see src/content/book/README.md).
// One Markdown file per chapter, and one small Markdown file per real-life example.
const chapters = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/book/chapters' }),
  schema: z.object({
    number: z.number(),
    title: z.string(),
    subtitle: z.string().optional(),
    status: z.enum(['draft', 'outline', 'reviewed']).default('outline'),
    summary: z.string(),
    updated: z.string().optional(),
  }),
});

const examples = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/book/examples' }),
  schema: z.object({
    chapter: z.number(),
    topic: z.string(),
    title: z.string(),
    added: z.string(),
    modality: z.string().optional(),
    case: z.string().optional(),
    images: z.array(z.object({ src: z.string(), caption: z.string() })).default([]),
  }),
});

export const collections = { chapters, examples };
