import asyncio
from clicker import Clicker

async def main():
    counter = 0
    clicker = Clicker()
    nextPage = 'https://www.amazon.com/ga/giveaways?pageId=1'
    await clicker.createBrowser()
    await clicker.login()
    while nextPage:
        counter += 1
        if counter % 8 == 0: 
            # because it hangs sometimes
            print('Restart browser')
            await clicker.closeBrowser()
            await clicker.createBrowser()
            await clicker.login()
        nextPage = await clicker.processPage(nextPage)

asyncio.get_event_loop().run_until_complete(main())