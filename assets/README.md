# Documentation assets

Versioned images used by the repository documentation. These files are explanatory illustrations, not policy evidence or runtime inputs.

## Organization

```text
assets/
|-- README.md
`-- readme/
    |-- README.md
    |-- 01-grounded-answers.png
    `-- 02-rewrite-evaluation.png
```

| Folder | Purpose |
| --- | --- |
| [readme/](readme/README.md) | Illustrations embedded in the root README, with an image inventory and context. |

Group future assets by the document or feature that owns them. Create folders when there are actual files to place in them.

## Maintenance

- Use lowercase, hyphenated filenames. Prefix images with an order number when they form a reading sequence.
- Keep paths relative so images work in local previews and on GitHub. Update every reference when moving or renaming a file.
- Give each embedded image descriptive alt text. Keep commands, policy facts, and essential instructions in Markdown as well.
- Prefer SVG for authored diagrams and PNG for raster illustrations. Keep text readable at README width and avoid unnecessary file size.
- Record an image's purpose and origin in its folder README. Do not infer licensing or attribution rights from its presence here.
- Keep real company policies, private screenshots, temporary exports, and credentials out of this directory.

Before publishing, check image links and review both desktop and narrow-screen rendering.

[Back to the project README](../README.md)
