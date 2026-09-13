# Optional AWS integration points

No AWS SDK is imported and no cloud call is made in the current app. These are implementation notes for a future adapter, not a working cloud mode. Installing boto3 alone does not enable AWS.

## Amazon Lex V2: conversational understanding

Replace the call to `recognize` with a provider interface returning the existing `Understanding` contract. Configure a Lex bot with intents corresponding to the local names, sample utterances, and appropriate slot types. Build and publish a bot version/alias, then invoke `lexv2-runtime.recognize_text` with `botId`, `botAliasId`, `localeId`, `sessionId`, and `text`. Map the returned intent and slot values into the local contract. Keep bot session identity separate from raw customer identifiers.

Use `AMAZON.FallbackIntent` or low-confidence/ambiguous results to request clarification or route to human review. Implement timeouts, error handling, explicit provider status, and contract tests with mocked SDK responses. Do not silently claim a cloud prediction when a fallback was used. Lex supports dialog state and slot elicitation; the local mock does not emulate these features.

References: [RecognizeText API](https://docs.aws.amazon.com/lexv2/latest/APIReference/API_runtime_RecognizeText.html), [Lex slots](https://docs.aws.amazon.com/lexv2/latest/dg/intent-slots.html).

## Amazon Polly: speech output

After generating response text, an opt-in adapter could invoke `polly.synthesize_speech(Text=response, OutputFormat="mp3", VoiceId=...)`, using a compatible voice/engine configuration. Return or securely store the returned audio stream with an appropriate content type and lifecycle. Handle service failures without preventing the routing recommendation. Do not mark audio as generated until a valid stream is available.

Polly synthesizes speech. It does **not** classify customer intent or analyze sentiment. Transcript analytics remain separate; a future sentiment model/service would need its own evaluation and integration.

Reference: [SynthesizeSpeech API](https://docs.aws.amazon.com/polly/latest/APIReference/API_SynthesizeSpeech.html).

## Deployment boundaries

Add boto3 as an optional dependency, select providers explicitly, and use the standard AWS credential chain/role credentials. Use least-privilege permissions for the configured bot and speech operations, supported regions, encryption and retention policies, and cost controls. Keep secrets out of code and Git. Add an explicit queue adapter (for example, an Amazon Connect integration) before claiming that a caller is actually transferred. Cloud integration would require separate sandbox tests and a deployment review; local tests cannot validate AWS behavior.
