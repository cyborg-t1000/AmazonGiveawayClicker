import asyncio
from clicker import Clicker


async def main():
    counter = 0
    clicker = Clicker()
    await clicker.get_credentials()
    next_page = 'https://www.amazon.com/ga/giveaways?pageId=2'
    await clicker.createBrowser()
    await clicker.login()
    while next_page:
        counter += 1
        if counter % 8 == 0:
            # because it hangs sometimes
            print('Restart browser')
            await clicker.closeBrowser()
            await clicker.createBrowser()
            await clicker.login()
        next_page = await clicker.processPage(next_page)

asyncio.get_event_loop().run_until_complete(main())
