Read this when a PR body needs screenshots or terminal PNGs as evidence. It is the detail behind the "PR Body Evidence Attachments" section in [SKILL.md](../SKILL.md).

Use only the code host's own authenticated attachment feature, so the image is hosted where the PR lives and readers can open it. Never commit temporary images, never use release assets for PR evidence, and never use external image hosts. Never log session cookies, anti-forgery tokens, upload form fields, or upload headers.

1. Confirm an authenticated web session for the host exists; an API token from a command-line client is usually not enough for attachment upload.
2. Upload each image through the host's attachment flow, from the PR or issue page in that session.
3. Keep only the final hosted attachment URL for each image.
4. Put those URLs in the PR body: write the body to a temp file and pass it with the host client's body-file option instead of shell-quoting it.

If no authenticated session or attachment feature is available, skip the images and state the blocker in the PR body without publishing local file paths: local paths are unreadable to reviewers and expose host details. Do not improvise another host.
