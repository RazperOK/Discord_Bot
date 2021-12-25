import discord
from discord.ext import commands
import webbrowser as wb
from random import randint
from discord.utils import get
import requests
from PIL import Image, ImageFont, ImageDraw
import io
import my_qr
import cv2
from pyzbar import pyzbar
import sqlite3

# Задаем префикс для бота
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
# Собственноручное изменение команды help
bot.remove_command('help')

# Слова, на которые реагирует бот
hello_words = ['hello', 'hi', 'привет', 'privet', 'хай', 'ку', 'ky', 'qq', 'здарова', 'дарова']
answer_words = ['информация о сервере', 'команды', 'команды сервера']
goodbye_words = ['пока', 'bb', 'bb all', 'bye', 'goodbye']
bad_words = ['сука', 'флуд', 'мат', 'хрень']


@bot.event # Статус бота
async def on_ready(): # Асинхронное программирование необходимое для работы команд, далее используется везде
    print('Bot connected')

    await bot.change_presence(status = discord.Status.online, activity = discord.Game('!help'))


@bot.event
async def on_command_error(ctx, error):
    pass


@bot.event # Реакция бота на присоединение нового пользователя
async def on_member_join(member):
    for ch in bot.get_guild(member.guild.id).channels:
        if ch.name == 'основной':
            await bot.get_channel(ch.id).send(f'{member}, Приветствую! Я Test-bot. Для просмотра команд используй команду !help')


@bot.event # Реакция бота на уход пользователя
async def on_member_remove(member):
    for ch in bot.get_guild(member.guild.id).channels:
        if ch.name == 'основной':
            await bot.get_channel(ch.id).send(f'{member}, нам будет тебя не хватать!')


@bot.event # Реакция бота на слова катализаторы
async def on_message(message):
    msg = message.content.lower() # Создаем переменную msg с нижним регистром для работы списков слов ниже

    if msg in hello_words:
        await message.channel.send('Привет, чем могу помочь?')

    if msg in answer_words:
        await message.channel.send('Пропиши команду !help и всё узнаешь!')

    if msg in goodbye_words:
        await message.channel.send('Пока, удачи тебе!')

    if msg in bad_words:
        await message.delete()
        await message.author.send(f'{message.author.name}, не пиши так!')
    await bot.process_commands(message)


@bot.command(pass_context=True) # Команда, показывающая пользователю все остальные команды
async def help(ctx):
    emb = discord.Embed(title='**Навигация по командам**') # вывод информации по командам

    emb.add_field(name='{}clear'.format('!'), value='Очистка чата(только для Админа)')
    emb.add_field(name='{}ban'.format('!'), value='бан пользователя(только для Админа)')
    emb.add_field(name='{}unban'.format('!'), value='разбан пользователя(только для Админа)')
    emb.add_field(name='{}hello'.format('!'), value='Приветствие')
    emb.add_field(name='{}kick'.format('!'), value='Удаление пользователя')
    emb.add_field(name='{}test'.format('!'), value='Тестирование бота')
    emb.add_field(name='{}random'.format('!'), value='Рандомное число')
    emb.add_field(name='{}google'.format('!'), value='Серфинг по сети')
    emb.add_field(name='{}send_a'.format('!'), value='Отправка сообщения себе')
    emb.add_field(name='{}send_m'.format('!'), value='Отправка сообщения пользователю')
    emb.add_field(name='{}qr'.format('!'), value='Создание qr кода')
    emb.add_field(name='{}news_g'.format('!'), value='Игровые новости')
    emb.add_field(name='{}news_c'.format('!'), value='Новости о политике')
    emb.add_field(name='{}card_user'.format('!'), value='Карточка пользователя')
    emb.add_field(name='{}math'.format('!'), value='Простой калькулятор')

    await ctx.send(embed=emb)


@bot.command(pass_context=True) # Команда очистки сообщений, доступна только для админа
@commands.has_permissions(administrator = True)
async def clear(ctx, amount : int): # Задаем функцию очистки, где благодаря int сами выбираем количество
    await ctx.channel.purge(limit=amount) # Лимит удаляемых сообщений завасити от числа, которое мы задаем


@bot.command(pass_context=True) # Команда приветствия пользователя
async def hello(ctx):
    author = ctx.message.author  # Объявляем переменную author и записываем туда информацию об авторе.
    await ctx.send(f'Hello, good to see you, {author.mention}!')  # Выводим сообщение с упоминанием автора, обращаясь к переменной author.


@bot.command(pass_context=True) # Кик пользователя
@commands.has_permissions(administrator = True)
async def kick(ctx, member: discord.Member, *, reason=None):
    emb = discord.Embed(title = 'Kick', colour = discord.Colour.red()) # вывод информации о кикнутом пользователе
    await ctx.channel.purge(limit=1)

    await member.kick(reason=reason)
    emb.set_author(name = member.name, icon_url = member.avatar_url)
    emb.add_field(name = 'Kick user', value = 'Изгнан пользователь : {}'.format(member.mention))
    await ctx.send(embed = emb)


@bot.command() # Бан пользователя
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await ctx.channel.purge(limit=1)
    await member.ban(reason=reason)

    emb = discord.Embed(title='Информация о блокировке участника', #вывод информации о бане пользователя
                        description=f'{member.name}, был заблокирован в связи с нарушением правил',
                        color=0xc25151)

    emb.set_author(name=member.name, icon_url=member.avatar_url)
    emb.add_field(name=f'ID: {member.id}', value=f'Блокированный участник : {member}')
    emb.set_footer(text='Был заблокирован администратором {}'.format(ctx.author.name), icon_url=ctx.author.avatar_url)

    await ctx.send(embed=emb)


@bot.command() # Разбан пользователя по той же схеме, как и бан
@commands.has_permissions(administrator=True)
async def unban(ctx, *, member):
    await ctx.channel.purge(limit = 1)

    banned_users = await ctx.guild.bans()

    for ban_entry in banned_users:
        user = ban_entry.user

        await ctx.guild.unban(user)
        await ctx.send(f'Unbanned user {user.mention}')

        return


@bot.command(pass_context=True) # Просто команда выводящая текст в кавычках
async def test(ctx):
    await ctx.send('Testing success.')


@bot.command(pass_context=True) # Функция random для вывода рандомного числа от 0 до 100
async def random(ctx):
    embed = discord.Embed(
        title=f"Рандомное число - {randint(0, 100)}",)
    await ctx.send(embed=embed) # вывод рандомного числа


# Работа с google поисковиком, работает правильно только на хостинге по типу heroku
@bot.command(pass_context=True)
async def google(ctx, *, arg_1 = None):
    if arg_1 != None:
        request = arg_1 # запрос ссылки
        await wb.open('http://www.google.com/search?q=' + request)
    else:
        wb.open('https://www.google.ru') # если не указана ссылка выводит просто страницу google


@bot.command(pass_context=True) # Отправка сообщения от бота самому себе
async def send_a(ctx):
    await ctx.author.send('Привет, друг!')


@bot.command(pass_context=True) # Отправка сообщения через бота другому пользователю
async def send_m(ctx, member: discord.Member):
    await member.send(f'{member.name}, Привет от {ctx.author.name}') # от member(пользователя) к author(отправителя)


@bot.command(pass_context=True) # Создание qr-кода с его последующим сохранением
async def qr(ctx, *, arg, error):
    my_qr.make_qr(arg) # запрос ссылки на создание
    await ctx.send('Ваш qr-код', file = discord.File('myqrcode.png'))


@bot.command(pass_context=True) # Выход на новостной сайт по играм
async def news_g(ctx):
    embed = discord.Embed(
        title="Тык для перехода",
        description="Ссылка для перехода на сайт 1 канала",
        url='https://vgtimes.ru/news/',
    )
    await ctx.send(embed=embed) # вывод гиперссылки на сайт


@bot.command(pass_context=True) # Выход на новостной сайт по политике
async def news_c(ctx):
    embed = discord.Embed(
        title="Тык для перехода",
        description="Ссылка для перехода на сайт 1 канала",
        url='https://www.1tv.ru/news',
    )
    await ctx.send(embed=embed) # вывод гиперссылки на сайт


@clear.error # Сообщение для пользователя о необходимости использования аргументов
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument): # если отсутствует аргмуент
        await ctx.send(f'{ctx.author.name}, обязательно укажите аргумент!')

    if isinstance(error, commands.MissingPermissions): # если нет прав
        await ctx.send(f'{ctx.author.name}, у вас недостаточно прав!')


@qr.error # Сообщение для пользователя о необходимости использования аргументов
async def qr_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.name}, обязательно укажите ссылку!')


@ban.error # Сообщение для пользователя о необходимости использования аргументов
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.name}, обязательно укажите участника!')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.name}, у вас недостаточно прав!')


@unban.error # Сообщение для пользователя о необходимости использования аргументов
async def unban_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.name}, обязательно укажите участника!')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.name}, у вас недостаточно прав!')


@bot.command(pass_context=True) # Создание карточки пользователя
async def card_user(ctx):
    await ctx.channel.purge(limit = 1)

    img = Image.new('RGBA', (400, 200), '#380580')
    url = str(ctx.author.avatar_url)

    response = requests.get(url, stream = True) # Response - это объект для проверки результатов запроса в виду переменной
    response = Image.open(io.BytesIO(response.content))
    response = response.convert('RGBA')
    response = response.resize((100, 100), Image.ANTIALIAS)

    img.paste(response, (15, 15, 115, 115))

    idraw = ImageDraw.Draw(img) # создаем переменные
    name = ctx.author.name
    tag = ctx.author.discriminator

    headline = ImageFont.truetype('arial.ttf', size = 20)
    undertext = ImageFont.truetype('arial.ttf', size = 12)
    text = ImageFont.truetype('arial.ttf', size = 12)

    idraw.text((145,15), f'{name}#{tag}', font = headline)
    idraw.text((145, 50), f'ID: {ctx.author.id}', font = undertext)
    idraw.text((145, 80), f'Я просто хочу спать.', font = text)

    img.save('user_card.png')

    await ctx.send(file = discord.File(fp = 'user_card.png'))


@bot.command(pass_context=True) # Простой калькулятор
async def math(ctx, a: int, arg, b: int = 1):
    if arg == '+':
        await ctx.send(f'Result: {a + b}') # Сложение

    elif arg == '-':
        await ctx.send(f'Result: {a - b}') # Вычитание

    elif arg == '/':
        await ctx.send(f'Result: {a / b}') # Деление

    elif arg == '*':
        await ctx.send(f'Result: {a * b}') # Умножение

    elif arg == '^':
        await ctx.send(f'Result: {a ** b}') # Возведение в степень


@kick.error # Сообщение для пользователя о необходимости использования аргументов
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.name}, обязательно укажите пользователя!')

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.name}, у вас недостаточно прав!')

# Токен для работы бота
bot.run('OTIyMTQ5MTQ1MTEwODA2NTQ5.Yb9QUA.ZtkSRXxoloRc8fO7AcgjeeyjEaE')