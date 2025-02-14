import click
from cohere import ClientV2 as CohereClient
from qdrant_client import QdrantClient
from qdrant_client.http import models

from backend.domain.entities.fact import Fact
from backend.domain.value_objects.chat_actor import ChatActor
from backend.infrastructure.configuration.config import get_config


@click.command()
@click.option(
    "--path-to-user-facts",
    default="./static/user_facts.txt",
    type=str,
    help="Path to user facts",
)
@click.option(
    "--batch-size",
    default=32,
    type=int,
    help="Batch size for processing facts",
)
@click.option(
    "--embedding-dimension",
    default=1024,
    type=int,
    help="Dimension of embeddings from Cohere model",
)
def add_facts(  # noqa: WPS213
    path_to_user_facts: str,
    batch_size: int,
    embedding_dimension: int,
) -> None:
    config = get_config()
    user_facts = []
    with open(path_to_user_facts) as file_object:
        for line in file_object:
            if line:
                fact = Fact(owner=ChatActor.USER, text=line.strip())
                user_facts.append(fact)
    click.echo(f"Num user facts: {len(user_facts)}")

    cohere_client = CohereClient(
        api_key=config.embedder.api_key.get_secret_value(),
    )
    qdrant_client = QdrantClient(
        host=config.vector_storage.host.get_secret_value(),
        port=config.vector_storage.port,
    )

    collection_name = config.vector_storage.collection_name
    if qdrant_client.collection_exists(collection_name):
        qdrant_client.delete_collection(collection_name)

    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=embedding_dimension, distance=models.Distance.COSINE
        ),
    )

    for fact_index in range(0, len(user_facts), batch_size):
        batch = user_facts[fact_index : fact_index + batch_size]

        texts = [fact.text for fact in batch]
        embeddings_response = cohere_client.embed(
            texts=texts,
            model=config.embedder.model,
            input_type=config.embedder.input_type,
            embedding_types=[config.embedder.embedding_type],
        )

        if embeddings_response.embeddings.float_ is None:
            raise ValueError("Embeddings is None")

        points = [
            models.PointStruct(
                id=index + fact_index,
                vector=embedding,
                payload={"text": fact.text, "owner": fact.owner.value},
            )
            for index, (fact, embedding) in enumerate(
                zip(batch, embeddings_response.embeddings.float_, strict=False)
            )
        ]

        qdrant_client.upsert(collection_name=collection_name, points=points)

        click.echo(f"Processed batch {fact_index // batch_size + 1}, added {len(points)} facts")

    click.echo("Finished adding facts to vector storage")
    collection_info = qdrant_client.get_collection(collection_name=collection_name)
    click.echo(collection_info)

    test_text = user_facts[0].text
    test_qdrant_response = cohere_client.embed(
        texts=[test_text],
        model=config.embedder.model,
        input_type=config.embedder.input_type,
        embedding_types=[config.embedder.embedding_type],
    )

    if test_qdrant_response.embeddings.float_ is None:
        raise ValueError("Test embeddings is None")

    test_embedding = test_qdrant_response.embeddings.float_[0]

    search_result = qdrant_client.query_points(
        collection_name=collection_name, query=test_embedding, limit=1
    )
    click.echo("\nVerification search results:")
    click.echo(f"Original text: {test_text}")
    if search_result:
        payload = search_result.points[0].payload
        if payload:
            click.echo(f"Found text: {payload['text']}")
        else:
            click.echo("Payload is None")
        click.echo(f"Score: {search_result.points[0].score}")
    else:
        click.echo("No results found!")


if __name__ == "__main__":
    add_facts()
