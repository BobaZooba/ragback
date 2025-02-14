from backend.application.services.prompt import PromptBuilderServiceP
from backend.application.value_objects.prompts_data.rag import RAGPromptData
from backend.domain.value_objects.chat_actor import ChatActor
from backend.integrations.services.prompts.mako import BaseMakoPromptBuilder


class MakoRAGPromptBuilder(PromptBuilderServiceP[RAGPromptData], BaseMakoPromptBuilder):
    async def make(self, prompt_data: RAGPromptData) -> str:
        template = self.lookup.get_template(self.template_name)

        return template.render(
            user=prompt_data.user,
            character=prompt_data.character,
            messages=prompt_data.messages,
            search_results=prompt_data.search_results,
            ChatActor=ChatActor,
        )
