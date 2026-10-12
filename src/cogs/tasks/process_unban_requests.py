from discord import Client, Forbidden, NotFound, Object
from discord.ext import commands, tasks

from env import config
from repositories.unban_requests_repository import UnbanRequestsRepository


class ProcessUnbanRequestsTaskCog(commands.Cog):
    def __init__(self, client: Client) -> None:
        self.client = client
        self.unban_requests_repository = UnbanRequestsRepository()

    @tasks.loop(minutes=30)
    async def process_unban_requests(self) -> None:
        await self.client.wait_until_ready()
        guild = self.client.get_guild(config["guild"]["id"])

        if guild is None:
            print(
                "❌ Erro: Guild não encontrada! Verifique se o bot está no servidor correto."
            )
            return

        unban_requests = await self.unban_requests_repository.get_unban_requests()
        for unban_request in unban_requests:
            user_id = unban_request["_id"]

            try:
                await guild.unban(user=Object(user_id))
                await self.unban_requests_repository.delete_unban_request(
                    user_id=user_id
                )
                print(
                    f'✅ O usuário "{user_id}" foi desbanido automaticamente pelo sistema anti-bot.'
                )
            except NotFound:
                print(
                    f'❌ O usuário "{user_id}" não está na lista de banidos do servidor.'
                )
                await self.unban_requests_repository.delete_unban_request(
                    user_id=user_id
                )
            except Forbidden:
                print("❌ Eu não tenho permissão para desbanir membros.")
            except Exception as err:  # noqa: BLE001
                print(
                    f'❌ Ocorreu um erro ao tentar desbanir o usuário "{user_id}"! Erro: {err}'
                )

    async def cog_load(self) -> None:
        self.process_unban_requests.start()
        print("✅ Task `process_unban_requests` iniciada com sucesso!")

    async def cog_unload(self) -> None:
        self.process_unban_requests.cancel()
        print("✅ Task `process_unban_requests` foi terminada com sucesso!")


async def setup(client):
    await client.add_cog(ProcessUnbanRequestsTaskCog(client))
