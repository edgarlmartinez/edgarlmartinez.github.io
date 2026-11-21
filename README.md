# edgarlmartinez.github.io

Personal website and Harvard Medical School (HMS) format CV of Edgar L. Martinez Salazar, MD.

Built with [Astro](https://astro.build) and published free on GitHub Pages. Every page is generated from two plain-text files, so keeping the site current means editing data, not code.

| File | What it holds |
| --- | --- |
| `src/data/cv.yaml` | The whole CV, in HMS section order. Single source of truth. |
| `src/data/site.yaml` | Website-only text: headline, bio, focus areas, profile links. |

Pages:

- `/` home page (bio, current roles, leadership, selected publications, training, mentorship, contact)
- `/publications/` searchable list of all publications and abstracts
- `/cv/` the CV in HMS format, print-ready, with a downloadable `cv.pdf`

## Updating the CV

1. Open `src/data/cv.yaml` on GitHub and click the pencil (Edit) icon.
2. Copy an existing entry in the right section, paste it, and change the text. Order inside a list does not matter: entries are sorted by date when the site is built.
3. Click **Commit changes**. The site and the PDF rebuild and go live in about two minutes (see the **Actions** tab).

Examples:

```yaml
# A new publication (under publications: research_investigations or case_reports)
    - authors: Lastname AB**, Martinez-Salazar EL.
      title: Title of the paper.
      journal: Skeletal Radiol.
      details: 2027 Jan;56(1):1-10. Epub 2026 Dec 1.
      doi: 10.1007/xxxx
      pmid: "12345678"
      year: 2027
      featured: true        # also show it on the home page

# A new appointment (under faculty_academic_appointments)
  - start: 07/2027
    end: Present
    title: Assistant Professor of Radiology
    department: Radiology
    institution: Harvard Medical School/Beth Israel Deaconess Medical Center
```

Tips:

- Dates are `MM/YYYY`; use `end: Present` for current roles. A role that ends today just gets its end date.
- `**` after an author marks a mentored trainee and `*` marks equal contribution, as in the HMS template.
- Text that contains a colon followed by a space must be wrapped in double quotes.
- Home address and phone are not in this repository. To print a full copy for HMS, copy `src/data/private.example.yaml` to `src/data/private.yaml` on your computer (it is git-ignored) and set `show_private_on_print: true` locally.
- Lines with `# check:` are items that need a quick confirmation.

## Running it on your computer (optional)

```bash
npm install
npm run dev            # live preview at http://localhost:4321
npm run build          # build the static site into dist/
npm run pdf            # write dist/cv.pdf (needs: npx playwright install chromium)
```

## Hosting

`.github/workflows/deploy.yml` builds the site and the PDF on every push to `main` and publishes to GitHub Pages. In the repository settings, set **Pages → Source** to **GitHub Actions**. A custom domain (e.g. `edgarmartinezmd.com`) can be added later under the same settings page.
