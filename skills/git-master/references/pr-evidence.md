Read this when a PR body needs screenshots or terminal PNGs as evidence. It is the detail behind the "PR Body Evidence Attachments" section in [SKILL.md](../SKILL.md).

The allowed hosting path is GitHub user attachments from the authenticated web attachment flow. Never commit temporary images, never use release assets for PR evidence, and never use external image hosts. Never log browser cookies, CSRF tokens, form fields, or upload headers.

The flow needs an authenticated GitHub web session; an API token from the `gh` CLI alone is not enough.

1. Open the target PR or issue page in that session and read its file-attachment CSRF token and repository id.
2. `POST https://github.com/upload/policies/assets` with `repository_id`, `name`, `size`, `content_type`, and that token as `authenticity_token`.
3. Upload the bytes to the returned storage URL with the returned form fields exactly as given.
4. `PUT https://github.com/upload/assets/:id` with the returned `asset_upload_authenticity_token`.
5. Put only the final `https://github.com/user-attachments/assets/<uuid>` URL in the PR body: write the body to a temp file and pass it with `gh pr edit --body-file`.

If no authenticated browser session is available, leave the local evidence paths in the PR body and state the blocker. Do not improvise another host.
