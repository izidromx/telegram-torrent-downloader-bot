import logging
import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode

# Replace this with your bot token from BotFather
TELEGRAM_API_TOKEN = ""

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


async def start(message: types.Message):
    """
    Responds to the /start and /help commands with a greeting message.
    """
    await message.reply("Hi there! I'm a movie search bot. Type a movie title to get its details. You can also use "
                        "the command /help to see all available commands. Have fun searching!")


async def find_movie(message: types.Message):
    """
    Searches for a movie, extracts the movie data, and sends it to the user.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/99.0.4844.84 Safari/537.36'}
    movie_title = message.text
    search_url = f"https://solidtorrents.to/search?q={movie_title}+yg"

    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    movie_results = soup.find_all('li', class_='card search-result my-2')

    movies = [extract_movie_data(movie) for movie in movie_results]

    if movies:
        for movie in movies:
            movie_info = format_movie_info(movie)
            await message.reply(movie_info, parse_mode=ParseMode.MARKDOWN)
    else:
        await message.reply("Movie not found. Please check the title and try again.")


def extract_movie_data(movie):
    """
    Extracts the movie data from a BeautifulSoup movie object.

    Args:
        movie: A BeautifulSoup object containing the movie data.

    Returns:
        A dictionary containing the extracted movie data.
    """
    title = movie.find('h5', class_='title').text.strip()
    category = movie.find('a', class_='category').text.strip()
    download_links = movie.find('div', class_='links center-flex hide-on-small px-3').find_all('a')
    torrent_url = download_links[0]['href']
    magnet_url = download_links[1]['href']

    return {
        'title': title,
        'category': category,
        'torrent_url': torrent_url,
        'magnet_url': magnet_url
    }


def format_movie_info(movie):
    """
    Formats the extracted movie data into a string for messaging.

    Args:
        movie: A dictionary containing the movie data.

    Returns:
        A formatted string containing the movie information.
    """
    movie_info = f"*{movie['category']}*\n"
    movie_info += f"*{movie['title']}*\n"
    movie_info += f"[Download]({movie['torrent_url']})"
    return movie_info


def main():
    """
    Registers the message handlers and starts the polling.
    """
    from aiogram import executor
    dp.register_message_handler(start, commands=['start', 'help'])
    dp.register_message_handler(find_movie, content_types=types.ContentTypes.TEXT)
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
