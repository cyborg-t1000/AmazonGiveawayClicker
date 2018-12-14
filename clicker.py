import asyncio
import random
import getpass
from pyppeteer import launch


class Clicker(object):
    def __init__(self):
        self.email = None
        self.password = None
        self.browser = None
        self.mainPage = None
        self.LOGIN_PAGE = 'https://www.amazon.com/ap/signin?_encoding=UTF8&ignoreAuthState=1&openid.assoc_handle=usflex&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_signin&switch_account='

    async def checkRelogin(self, page):
        check = await page.querySelector('.cvf-account-switcher')
        if check:
            print('Relogin detected')
            continueButton = await page.querySelector('a[data-name="switch_account_request"]')
            await continueButton.click()
            await asyncio.sleep(2)

    async def createBrowser(self):
        self.browser = await launch(headless=False)

    async def closeBrowser(self):
        await self.browser.close()

    async def get_credentials(self):
        self.email = input('Enter your e-mail: ')
        self.password = getpass.getpass('Enter your password: ')

    async def login(self):
        self.mainPage = await self.browser.newPage()
        await self.mainPage.setViewport({'width': 1800, 'height': 1000})
        await self.mainPage.goto(self.LOGIN_PAGE)
        await self.mainPage.type('#ap_email', self.email)
        await self.mainPage.type('#ap_password', self.password)
        await asyncio.sleep(2)
        await self.mainPage.click('#signInSubmit')
        await asyncio.sleep(2)

    async def processPage(self, URL):
        print('Page:' + URL)
        await self.mainPage.goto(URL)
        await asyncio.sleep(random.randrange(1, 4))
        await self.checkRelogin(self.mainPage)
        table = await self.mainPage.querySelector('#giveaway-grid')
        if table:
            items = await table.xpath('*/*')
            for item in items:
                await self.processItem(item)
        lastPage = await self.mainPage.querySelector("li.a-disabled.a-last")
        if lastPage:
            print('Last page reached')
            return False
        else:
            nextPage = await self.mainPage.querySelector('li.a-last a')
            nextPageURL = await self.mainPage.evaluate(
                '(nextPage) => nextPage.href',
                nextPage
            )
            return nextPageURL

    async def processItem(self, item):
        itemType = await item.querySelector('.giveawayParticipationInfoContainer')
        if itemType:
            itemTypeTxt = await self.mainPage.evaluate(
                '(itemType) => itemType.textContent',
                itemType
            )
            if 'Follow ' in itemTypeTxt:
                return False
        itemURL = await self.mainPage.evaluate(
            '(item) => item.href',
            item
        )
        # print('Item:' + itemURL)
        itemPage = await self.browser.newPage()
        await itemPage.setViewport({'width': 1900, 'height': 1000})
        await itemPage.goto(itemURL)
        await asyncio.sleep(random.randrange(2, 4))
        await self.checkRelogin(itemPage)
        itemReady = await itemPage.querySelector('.qa-enter-chance-label')
        if itemReady:
            boxButton = await itemPage.querySelector('#box_click_target')
            enterButton = await itemPage.querySelector('#enterSubmitForm')
            itemTimeY = await itemPage.querySelector('#giveaway-youtube-video-watch-text')
            itemTimeA = await itemPage.querySelector('#giveaway-video-watch-text')
            if boxButton:
                await boxButton.click()
            elif enterButton:
                await enterButton.click()
            elif itemTimeY:
                await asyncio.sleep(10)
                await itemPage.waitForSelector('#enter-youtube-video-button:not(.a-button-disabled)')
                await asyncio.sleep(random.randrange(1, 4))
                continueButton = await itemPage.querySelector('#enter-youtube-video-button-announce')
                await continueButton.click()
            elif itemTimeA:
                print('Amazon video:' + itemURL)
            else:
                await itemPage.close()
                return False
            try:
                await itemPage.waitForSelector('.qa-giveaway-result-text')
            except:
                await itemPage.close()
                return False

            await asyncio.sleep(random.randrange(3, 4))
            result = await itemPage.querySelector('.qa-giveaway-result-text')
            resultText = await itemPage.evaluate(
                '(result) => result.textContent',
                result
            )
            if "you won!" in resultText:
                if itemTimeY:
                    print('It was Youtube')
                print('URL: ' + itemURL)
                shipmeButton = await itemPage.querySelector('input[name="ShipMyPrize"]')
                await shipmeButton.click()
                await asyncio.sleep(60)

        await itemPage.close()
