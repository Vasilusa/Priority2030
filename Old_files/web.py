from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

options = Options()

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
# driver.get("https://www.google.com")
# driver = webdriver.Chrome(executable_path='/usr/bin/google-chrome-stable')

driver.get('https://vk.ru')
print(driver.title)

# print(driver.find_element(by=By.TAG_NAME, value='body').text)
print(driver.page_source)

# driver.close()

driver.get('https://yandex.ru')
print(driver.title)

# print(driver.find_element(by=By.TAG_NAME, value='body').text)
# print(driver.execute(driver_command='getPageSource').get('value'))

# driver.close()