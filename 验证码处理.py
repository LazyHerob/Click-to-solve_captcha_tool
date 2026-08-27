from selenium.webdriver.common.action_chains import ActionChains as action
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
import time,base64
from selenium.webdriver.chrome.options import Options
from requests_html import HTMLSession
import ddddocr
# 创建session请求对象
session = HTMLSession()



chrome_options = Options()
chrome_options.add_argument("--window-size=1100,958")
chrome_options.add_argument("--force-device-scale-factor=1")
chrome_options.add_argument("--disable-high-dpi-support")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

class BZSpider(object):

    def __init__(self):

        self.login_url = 'https://www.bilibili.com/'
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"}
            )
        self.driver.maximize_window()
        self.start_url = 'http://api.jfbym.com/api/YmServer/customApi'

    def parse_login_url(self):

        self.driver.get(self.login_url)

        WebDriverWait(self.driver,20,0.5).until(
            EC.presence_of_element_located((By.XPATH,'//*[@id="app"]/div[2]/div[1]/div[1]/ul[2]/li[1]/li/div[1]/div/span'))).click()
        WebDriverWait(self.driver, 20, 0.5).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div/div[4]/div[2]/form/div[1]/input'))).send_keys('***********')#根据实际替换账号密码
        WebDriverWait(self.driver, 20, 0.5).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div/div[4]/div[2]/form/div[3]/input'))).send_keys('********')#根据实际替换账号密码
        WebDriverWait(self.driver, 20, 0.5).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div/div[4]/div[2]/div[2]/div[2]'))).click()
        time.sleep(2)

        tip_img = WebDriverWait(self.driver, 20, 0.5).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'geetest_tip_img')))
        tip_img.screenshot('b站点选验证码文字.png')

        img_div = WebDriverWait(self.driver, 20, 0.5).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div[2]')))
        img_div.screenshot('b站整副点选验证码.png')
        background_img = WebDriverWait(self.driver, 20, 0.5).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'geetest_item_img')))

        img_width = background_img.size['width']
        img_height = background_img.size['height']
        background_img.screenshot('b站点选验证码背景.png')

        self.parse_img_func(img_width,img_height)

    def parse_img_func(self,img_width,img_height):

        ocr = ddddocr.DdddOcr()
        # 读取图片
        with open('b站点选验证码文字.png', "rb") as f:
            image = f.read()
        # 识别图片
        result = ocr.classification(image, png_fix=True)

        char_list = list(result)
        print(result)
        print(char_list)
        with open('b站点选验证码背景.png', 'rb') as f:
            target_bytes = f.read()
        # 将图片数据经过base64加密处理
        base64_data = base64.b64encode(target_bytes).decode()
        data = {
            'image':base64_data,
            'token':'替换',#替换
            'type':'6246',
            'extra':','.join(char_list)
        }
        print(data['extra'])
        _headers = {
            "Content-Type": "application/json"
        }
        response = session.post(self.start_url,headers=_headers,json=data).json()
        print(response)
        data = response['data']['data']
        print(data)
        self.parse_click_img_html(data,img_width,img_height)

    def parse_click_img_html(self,data,img_width,img_height):

        # 定位验证码所在的标签
        img_div = WebDriverWait(self.driver, 20, 0.5).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div[2]')))

        for code_data in data.split('|'):
            x = int(code_data.split(r',')[0])
            y = int(code_data.split(r',')[1])
            print(x,y)

            x = x - img_width / 2
            y = y - img_height / 2
            print(x,y)

            actions = action(self.driver)
            actions.move_to_element_with_offset(img_div,x,y).click().perform()

            time.sleep(2)

        self.driver.find_element(By.XPATH,'/html/body/div[4]/div[2]/div[6]/div/div/div[3]/a/div').click()


if __name__ == '__main__':
    b = BZSpider()
    time.sleep(3)
    b.parse_login_url()
    time.sleep(300)