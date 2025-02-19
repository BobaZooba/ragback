# ragback

A service for generating AI character responses in dialogue context. Key features:

- Generation of context-aware responses considering character personality
- Retrieval and utilization of relevant user facts through RAG (Retrieval Augmented Generation)
- Maintaining character consistency throughout the dialogue
- Flexible prompt system that considers situation and context

The service is designed as an independent microservice responsible only for response generation. Storage of dialogue
history, user information, and character data is assumed to be handled by a separate service.
**Tech stack:** Python 3.12, FastAPI, OpenRouter (via OpenAI lib), Cohere for embeddings, Qdrant for vector search.

# My approach

This service would only be responsible for generating responses from
the LLM. Therefore, there is no storage of Characters, Users, and messages. Hence, there is no database and cache, not
even IDs. I assume that another service is responsible for context formation and storing all this information. That
service will be the source of truth.

Therefore, the contracts look like this:
As input, I accept message history, user information, and character information.
As output, I provide the character-generated message and the used search results (facts about the user).

How it works:

- Facts are retrieved from the last message
    - They are filtered by a selected threshold
    - Specifically the last message, because this reduces noise due to the too general embedder
        - In reality, we need to train our own embedder
        - And also add a `reranker`
- The prompt includes character description, found facts about the user (if any), username, dialogue history
  (last n messages)
    - The prompt also contains additional instructions about style and response format
- Based on the prompt, the next character's reply is generated using LLM

## Architecture

I use Domain Driven Design, or at least a significant part of it. The code is divided into layers:

- `domain` - description of data models, their services and repositories (data storage methods)
- `application` - business logic description, services, integration interfaces
- `integrations` - implementation of integration interfaces
- `infrastructure` - configuration, DI, implementation of repositories and other data storage methods
- `presentation` - implementation of ways to interact with this context

In DDD, what I dislike most are data models and data mappings between layers. Domain <-> infra, domain <-> application,
application <-> presentation. This takes a lot of time, so I consciously abandoned it. I didn't use value objects for
the domain layer to save time. I used pydantic in domain and application layers. Deliberately didn't use DTOs in the
application layer.

I didn't create repositories as I assumed my service isn't responsible for data storage.

## Why Python 3.12

Protocols - for interface description. This allows thinking about implementation much later and (more importantly) not
being tied to specific implementations (Dependency Inversion). Actually, couldn't implement DDD without this. A similar
alternative is abstract classes.

Generics - used minimally here, only in `PromptBuilder`.

## Libraries

`rye` - instead of `poetry`. An incredibly good solution for dependency management, venv, and everything else. Removes
most of the headaches with Python version conflicts. Based on `uv`, so it loads dependencies quickly.

I use `Makefile` for running commands. I prefer `justfile` (https://github.com/casey/just), but it's less popular.

### Code style

- `mypy` - for typed Python
- `ruff` - for unified code style (instead of `black`)
- `wemake-python-styleguide` - the strictest and most configurable linter (based on
  flake8): https://github.com/wemake-services/wemake-python-styleguide
- `pre-commit` - for checks and running `ruff` before commit

In Github CI, I only set up `code style` and `mypy`. Usually, I also add tests and deployment, or at least Docker build
and storing it in the right place for deployment.

### Backend

- `fastapi` - for asynchronous API
- `pydantic` - for data models and validation
- `pydantic-settings` - for config setup and reading from `.env`
- `tenacity` - retry policy
- `structlog` - for structured logs. Used minimally and without configuration to store in `json` to save time
- `dishka` - for dependency injection: https://github.com/reagento/dishka
- `pytest` - would use for tests, but that would be excessive for a test task
- `click` - for configuring `cli` tools
- `uuid` - would use for IDs if there was anything to store

### LLM

- `mako` - for templates like `jinja`
- `openai` - actually using OpenRouter
- `cohere` - for getting embeddings, because they have quite good models
- `qdrant` - vector database. There are too many vector databases, advantages of this one: has everything I need; scales
  well; I know the CTO and can guarantee its quality myself; written in Rust, which I know

### Logging

I didn't log much. Setting up logging is an important but time-consuming topic. I showed a few logging examples to
convince the reader that I know what it is, that structured logs should be stored, etc.

### Error Handling

I deliberately handled few errors to save time. This is quite understandable but meticulous work that would take a lot
of time.

### Tests

I didn't write tests because it's beyond the scope of the requirements. If I were to write them, I would use `pytest`,
fixtures, mocks, monkey patching.

# How to run

1. Install `rye` (https://rye.astral.sh/)
2. Create an `.env` file and fill it following the `.env.template` example. You'll need to obtain API keys from
   OpenRouter (https://openrouter.ai/) and Cohere (https://cohere.com/). OpenRouter is an aggregator of LLMs from
   different
   providers, while Cohere is needed for embedding models
3. In the terminal, enter `make dc.up` to start the `qdrant` container - a vector search database
4. In the terminal, enter `make add-facts`. This command populates `qdrant` with facts about the user
5. In the terminal, enter `make run`. This command starts the API service
6. In the terminal, enter `make interact`. This command starts a dialogue in the terminal. Wait a few seconds until the
   bot
   writes its first message

The solution works without RAG as well. So you don't have to run `qdrant`.

# Character consistency

Work done:

- Writing prompts
- Writing character descriptions
- Generating facts about the user
- Manual testing in dialogue and error analysis
- Selecting threshold for vector similarity of facts
- Model selection

The prompt is tailored for the situation. This information could have been moved to the character level. I would also
pass the situation description in the API. Then it would be: character + user + situation. But the requirements and time
didn't imply this.

In reality, I would also store facts about the character.

## How the situation is taken into account

The prompt explicitly states that different actions should be used. Examples: *fist bumps*, *sips drink*, *checks menu*,
etc. This allows for better immersion in the situation without explicitly mentioning what situation we're in. Thus,
through the prompt, the model clearly shows context. The model explicitly has the ability to perform small actions and
immerse the user in the simulated situation.

## How the character remains consistent

Through the selected model. There is no explicit verification. Manual testing and optimization of prompts and
descriptions.

**Advancements**: I optimized the prompt using Claude. Claude had the test task text, current prompt, and character
description in context. I submitted several of my dialogues, indicated what I didn't like, and asked to rewrite the
prompt or parts of it. I reviewed the resulting prompt and asked to fix places that concerned me. Then again
communicated and submitted dialogues. This way, for example, I managed to overcome too long replies and correct use of
asterisks (*sips drink*). I tried to make sure the prompt wasn't tailored to a specific model, but would be useful and
understandable for other models as well.

## Important disclaimer

Open source models are very poorly suited for such a task. You need to train your own. Therefore, quality optimization
seems excessive at this stage.

# Metrics

Metrics in such tasks are built based on data labeling. For data labeling, you need either a human or an approximation
of a human (LLM-as-judge). So unlike other tasks, we cannot calculate metrics instantly.

What types of metrics exist? Relative and absolute. Offline and online. Labeling can be done for calculating metrics and
for model fine-tuning. We can evaluate the entire dialogue or just one response in a dialogue.

## Absolute

Absolute metrics are convenient because you can calculate a metric for models and understand which one is better. Sounds
great, but it doesn't work in reality. Global benchmarks like MMLU have already lost their significance.

There are too many downsides to such metrics. The first downside is instructions. Updated the instructions? You can no
longer compare models with each other because they are evaluated slightly differently. Not updating instructions is
impossible. Moreover, with product requirements, they change too frequently. So the previously highlighted advantage is
too ephemeral.

Designed a scale:

- 0 - bad response
- 1 - normal response
- 2 - good response

We develop the product, initially the proportion of 0s is too high, then 1s, then 2s. We get say 95% of twos. What next?
Update the instructions?

- 3 - excellent response
- 4 - incredible response
- 5 - unimaginably impressive response

This won't work. You must describe each category well, corner cases, how 3 differs from 4 and so on. A response might be
good in terms of character consistency but poor in terms of engagement. Okay, let's make two metrics. In my previous
research, I reached about 50 potential evaluation criteria.

In general, all this is difficult to design and translate into instructions that someone will understand. And then
you'll have to change it anyway. And in the end, decisions are still made like this: model A has metric 73, model B has

70. So model A goes to production.

Why then do we need absolute evaluations?

I suggest using these metrics for lower bound evaluation. It's more about verification rather than improvements. That
is, we can grow in many directions and don't know where in advance, but we usually know exactly what we don't want.

Examples:

- Discussion about suicide
- Suggesting to meet in real life
- Sexting

## Relative

In brief: we give a person (or LLM) two variants. They need to choose which is better. Then we complicate it: which
variant is better in terms of character consistency? Unlike absolute evaluation, we don't need to describe the
differences between categories in such detail.

Changes are much more noticeable. In absolute evaluation, you can't give 2.3, it must be either 2 or 3. Here such things
work. One model is slightly better than another.

Downsides: we only compare in pairs (or groups). So we don't know how much better our current model is compared to the
model we had a year ago (considering we periodically release new ones). We can calculate this, but it's a separate
measurement. We assume that if model A > B, and model B > C, then A > C.

## Offline evaluation

We take historical data, remove the last reply in the dialogue and generate a response with the new model. This is
simple, but there's a nuance: the new model might not generate such context. This creates a distribution shift. If we
iteratively improve the product, the impact of such an effect is not so significant.

## Online evaluation

We created a model, asked people to talk to it. Pros: the model works on the context it generated itself. Cons:
expensive. Automation using LLM is still dangerous (or rather takes long to develop).

## Solution

### Production Model Evaluation

Take data from the last week. Create dialogues approximately 20 messages long with a window of 5.

#### Moderation

Send random dialogues to LLM-as-judge with tags indicating the presence of model messages:

- Hate speech
- Sexual content
- Self-harm
- Violence
- Errors (grammatical etc.)

We can also use https://platform.openai.com/docs/guides/moderation

Then we can train a classifier on this data to check larger volumes.

#### Improvements

The requirements state that we need to evaluate two things:

- "In-character" consistency
- Scenario focus

Here I really want to argue why exactly these need to be evaluated. It seems that from a product perspective, it's much
more important to evaluate engagement in dialogue. This leads to longer sessions. And we're not accounting for
teaching-related aspects at all.

It's not so important that our model got 76 points in the "In-character" consistency benchmark. What's important is
whether we've improved over time. So we'll compare with dialogues from the previous model version. We'll take historical
data and also split it into 20 messages.

Furthermore, each dialogue should have data about which character the model was playing and in what situation.

Example:

```
Character 1
Dialogue 1

Character 2
Dialogue 2

Which dialogue better portrays its character: 1, 2, or a tie?
```

Of course, the instruction should be more extensive and cover more cases. What does it mean to better portray one
character versus another?
Such instruction is created based on real dialogues.

We get 3 evaluations:

- How much better model B matches the character compared to model A
- How much better model B matches the situation compared to model A
- How much better model B engages in dialogue compared to model A

Where model B is the new model that has been responding in production for the last week, and model A is the model that
was
responding in production before.

If the new model underperforms in some areas, we need to move on to error analysis (which is as big a topic as metric
calculation) and work on model C. Model C will need to be compared with model B as well. Whether we should roll back to
model
A remains a debatable point.

### Should we roll out the new model?

We also take historical data, remove the last response, and generate with the new model. We need to evaluate different
parts of
dialogues - beginning, middle, end - meaning there should be different context sizes. Then we evaluate how much better
the new
response is compared to the old one according to the criteria above. We expect that we're optimizing on roughly the same
data
flow, so the context from the new model will be more or less the same as from the old one and we're not deceiving
ourselves
too much.

If we get an improvement (and don't worsen on any other criteria), then we roll it out to a subset of users.
