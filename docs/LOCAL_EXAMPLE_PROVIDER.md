# Local Example Provider Interface

This is the stable integration point for a user-managed local model. The repository does **not** call a hosted generation service and does not include a model runtime.

## Local-only implementation

Create this file on your own computer:

`docs/local-example-provider.local.js`

The file is intentionally ignored by Git, so it will not be committed or overwritten by normal `git pull` updates. It is loaded only when the site is running on `localhost` or `127.0.0.1`.

Define the following global object:

```js
window.GREContextLabExampleProvider = {
  apiVersion: 1,
  isConfigured: true,

  async generateExamples({ word, existingExamples, count, styles }) {
    // Connect to your own local model / local service here.
    // Return an array of candidate examples, e.g.:
    return [
      {
        id: "optional-stable-id",
        text: "The committee offered a succinct explanation of the result.",
        kind: "academic",
        note: "Shows concise expression with an emphasis on clarity."
      }
    ];
  }
};
```

## Request contract

`generateExamples(request)` receives:

- `word`: the word record, including its stable `id`, spelling, definition, nuance and examples.
- `existingExamples`: all examples already available for that word, including locally generated examples.
- `count`: suggested number of new examples (currently 3).
- `styles`: suggested coverage, currently `general`, `academic`, and `contrast`.

The method may return a Promise. It must resolve to an array of objects with:

- `text` (required): the English example sentence.
- `kind` (optional): `general`, `academic`, `contrast`, `collocation`, `narrative`, or another short label.
- `note` (optional): a short explanation of the context or nuance.
- `id` (optional): a stable ID if your local pipeline has one.

The app de-duplicates examples by sentence text and stores returned examples in browser-local storage as **unreviewed candidates**. They are shown separately from curated examples. A full local backup includes the candidate examples; they are not pushed to GitHub by the progress-sync button.

## Data-pack format

Each vocabulary item continues to support the legacy single field:

```json
{ "id": "taciturn", "word": "taciturn", "example": "She was taciturn at conferences." }
```

For multiple curated examples, add an optional `examples` array. Each item can be a string or an object:

```json
{
  "id": "taciturn",
  "word": "taciturn",
  "examples": [
    {
      "id": "taciturn-academic-01",
      "text": "The taciturn researcher rarely spoke at seminars.",
      "kind": "academic",
      "note": "Emphasizes a habitual reluctance to speak."
    },
    {
      "id": "taciturn-general-02",
      "text": "Usually taciturn, he surprised his friends with a long speech.",
      "kind": "general"
    }
  ]
}
```

If `examples` is present and non-empty, the app displays that array; otherwise it falls back to `example`. The main word ID remains stable, so examples do not become separate vocabulary entries.

## Boundaries

- The local provider runs only in the local desktop site; GitHub Pages does not load the ignored local adapter.
- No API key, model path, or private local configuration should be committed.
- Candidate examples are saved locally. Use **完整备份** to export them before clearing browser data.
- The app interface is model-agnostic: your adapter can use MLX/Ollama or another local runtime, and can call a local HTTP service or a locally extended desktop endpoint.
