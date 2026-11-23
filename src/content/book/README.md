# Core MSK Radiology (the resident book)

The book lives at `/book/` on the website. Everything is plain Markdown, so you can edit it on GitHub in the browser.

```
src/content/book/
  chapters/      one file per chapter, e.g. 01-radiographs-do-not-touch.md
  examples/      one small file per real-life example ("From the reading room")
public/book/
  figures/       schematic SVG figures used by the chapters
  examples/      de-identified images for your examples
```

## Add a real-life example (the usual way to grow the book)

1. De-identify the images first, exactly as for the educational cases (see `public/cases/README.md` and `scripts/deid-image.py`). No names, initials, dates, accession numbers or scanner labels.
2. Put the images in `public/book/examples/` (PNG or JPG).
3. Copy `templates/BOOK_EXAMPLE.md` to `src/content/book/examples/` with a short name such as `ch1-nof-distal-tibia.md`, and fill it in:
   - `chapter`: the chapter number.
   - `topic`: where in the chapter it should appear (see the list below).
   - `title`, `added` (YYYY-MM), `modality`.
   - `images`: one line pair per image, with the path starting `/book/examples/`. Images that are already in the case library can be reused with `/cases/images/...`.
   - Optional `case`: the id of a full case on the Educational cases page.
   - Below the `---` line: two or three sentences, what you saw and what the resident should learn.
4. Commit. The example appears next to its topic in the chapter, and in the chapter's "Reading-room examples" list.

### Topics you can use

| Chapter | Topics |
| --- | --- |
| 1 | `nof`, `bone-island`, `enchondroma`, `osteochondroma`, `simple-bone-cyst`, `fibrous-dysplasia`, `intraosseous-lipoma`, `bone-infarct`, `myositis-ossificans`, `stress-fracture`, `variants`, `others`, `aggressive` |
| 2 | `marrow-replacement`, `chemical-shift`, `osteomyelitis`, `meniscus`, `ligament`, `tendon` |

To add a new topic, put `<div class="ex-slot" data-topic="your-topic"></div>` in the chapter where the example should appear. An example whose topic has no slot still shows in the "Reading-room examples" section at the end of the chapter.

## Edit or write a chapter

- Open the chapter file and edit the text. The front matter at the top controls the table of contents:
  - `status: outline` (planned), `draft` (written, awaiting your review) or `reviewed` (approved; the draft banner disappears).
  - `updated: YYYY-MM` shows on the chapter.
- `##` headings become the sidebar table of contents; `###` headings appear indented.
- Figures: `<figure><img src="/book/figures/name.svg" alt="..." /><figcaption>...</figcaption></figure>`.
- Boxes: wrap text in `<div class="lesion">` ... `</div>` for a lesion card, or `<div class="never">` for the "Never forget" box. Leave a blank line after the opening tag and before the closing tag so the Markdown inside still works.
- References: cite peer-reviewed sources with a DOI or PubMed link.

## Images: what is allowed

Use only schematic drawings, your own de-identified cases, or images with a license that allows reuse with attribution (and give the attribution in the caption). Do not copy figures from journals or textbooks.
