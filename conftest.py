import os
import pytest
from dotenv import load_dotenv
from utils.helper import BaseSession
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selene import browser

from utils import attach_ui

load_dotenv()

BOOKER_URL = os.getenv('booker_base_url')


@pytest.fixture(scope="session")
def booker(allure_attachments_flag=1):
    with BaseSession(base_url=BOOKER_URL) as session:
        yield session


DEFAULT_BROWSER_VERSION = "100.0"


def pytest_addoption(parser):
    parser.addoption(
        '--browser_version',
        default='100.0'
        # default='108.0'
    )


@pytest.fixture(scope='session', autouse=True)
def load_env():
    load_dotenv()


@pytest.fixture(scope='function')
def setup_browser(request):
    browser_version = request.config.getoption('--browser_version')
    browser_version = browser_version if browser_version != "" else DEFAULT_BROWSER_VERSION
    options = Options()
    selenoid_capabilities = {
        "browserName": "chrome",
        "browserVersion": browser_version,
        "selenoid:options": {
            "enableVNC": True,
            "enableVideo": True
        }
    }
    options.capabilities.update(selenoid_capabilities)

    login = os.getenv('LOGIN_SELENOID')
    password = os.getenv('PASSWORD_SELENOID')
    driver = webdriver.Remote(
        command_executor=f"https://{login}:{password}@selenoid.autotests.cloud/wd/hub",
        # command_executor="http://95.216.214.178:8080/wd/hub",
        options=options
    )

    # browser = Browser(Config(driver))
    browser.config.driver = driver
    ui_base_url = os.getenv('UI_BASE_URL')
    browser.config.base_url = (ui_base_url)
    browser.config.timeout = 6.0

    yield browser

    attach_ui.add_html(browser)
    attach_ui.add_screenshot(browser)
    attach_ui.add_logs(browser)
    attach_ui.add_video(browser)
    browser.quit()
