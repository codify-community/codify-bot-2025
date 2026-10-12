from discord import Client, Color, Embed, Forbidden, Message, NotFound
from discord.ext import commands

from env import config
from repositories.unban_requests_repository import UnbanRequestsRepository
from repositories.users_repository import UsersRepository

FIBO_BOT_ID = config["bots"]["fibo"]
GUILD_ID = config["guild"]["id"]

PRESENTATION_CHANNEL_ID = config["guild"]["channels"]["presentation"]
ANTIBOT_CHANNEL_ID = config["guild"]["channels"]["antibot"]


class MessageEventCog(commands.Cog):
    def __init__(self, client: Client) -> None:
        self.client = client
        self.user_repository = UsersRepository()
        self.unban_requests_repository = UnbanRequestsRepository()

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.channel.id == ANTIBOT_CHANNEL_ID:
            embed = Embed(
                title="⚠️ Banimento Automático",
                description=f"Olá **{message.author.display_name}**, sua conta foi detectada efetuando **spam** e ativou o sistema de proteção automatizada do servidor.",
                color=Color.red(),
            )

            embed.add_field(
                name="⏳ Duração do Banimento", value="**24 horas**", inline=True
            )
            embed.add_field(
                name="🔄 O que fazer?",
                value="Aguarde o prazo. O desbanimento ocorre automaticamente.",
                inline=True,
            )

            embed.set_footer(
                text="Codify Anti-Bot System",
                icon_url=message.guild.icon.url if message.guild.icon else None,
            )
            embed.timestamp = message.created_at

            try:
                await message.author.send(embed=embed)
            except Exception as err:  # noqa: BLE001
                print(
                    f'Não foi possivel notificar o usuário "{message.author.id}" sobre o banimento automático! Erro: {err}'
                )

            try:
                await message.author.ban(
                    delete_message_seconds=86400,
                    reason="Banimento automático por meio do canal anti-bot",
                )
                await self.unban_requests_repository.create(user_id=message.author.id)
                print(
                    f'✅ O usuário "{message.author.id}" foi banido pelo sistema anti-bot.'
                )
            except Forbidden:
                print(
                    f'❌ Eu não tenho permissão para banir o usuário "{message.author.id}".'
                )
            except NotFound:
                print(
                    f'❌ O usuário "{message.author.id}" não está na lista de membros do servidor.'
                )
            except Exception as err:  # noqa: BLE001
                print(
                    f'❌ Ocorreu um erro ao tentar banir o usuário "{message.author.id}"! Erro: {err}'
                )

        elif message.author.id == FIBO_BOT_ID and message.guild.id == GUILD_ID:
            if message.content.startswith(
                "Thx for bumping our Server! We will remind you in 2 hours!"
            ):
                bumper = message.mentions[0]
                if not bumper:
                    return

                await self.user_repository.bump(bumper.id)
                return await message.add_reaction("🚀")

        elif message.content.startswith(self.client.user.mention):
            return await message.channel.send(
                f"{message.author.mention} | Meu prefixo é `..`!"
            )

        # ToDO: Add level up system


async def setup(client):
    await client.add_cog(MessageEventCog(client))
